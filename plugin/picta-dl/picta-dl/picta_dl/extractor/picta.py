import itertools
import math
import re
import time
import urllib.parse

from ..networking.exceptions import HTTPError
from ..utils import (
    ExtractorError,
    base_url,
    determine_ext,
    int_or_none,
    parse_duration,
    str_or_none,
    strftime_or_none,
    traverse_obj,
    unified_timestamp,
    url_or_none,
    urlencode_postdata,
    urljoin,
    variadic,
)
from .common import InfoExtractor, SearchInfoExtractor


# noinspection PyAbstractClass
class PictaBaseIE(InfoExtractor):
    _NETRC_MACHINE = 'picta'
    ROOT_BASE_URL = 'https://www.picta.cu/'
    API_BASE_URL = 'https://api.picta.cu/v2/'

    @staticmethod
    def _extract_video(video, video_id=None, require_title=True):
        result = traverse_obj(video, ('results', 0), expected_type=dict)
        if not result:
            raise ExtractorError('Cannot find video!')

        timestamp = unified_timestamp(traverse_obj(result, ('fecha_creacion'), ('fecha')))
        modified_timestamp = traverse_obj(
            result, ('categoria', 'capitulo', 'temporada', 'serie', 'last_update'),
            ('fecha_publicado'))

        channel = traverse_obj(result, ('canal', 'nombre', {str_or_none}))
        release = traverse_obj(
            traverse_obj(result, ('categoria'), expected_type=dict),
            ('pelicula', 'ano'),
            ('capitulo', 'temporada', 'serie', 'ano'),
            ('video', 'ano'),
            expected_type=int_or_none)
        precios = traverse_obj(result, ('precios'), expected_type=list)

        info_video = {
            **traverse_obj(result, {
                'id': ('id', {str_or_none}),
                'title': ('nombre', {str_or_none}) if require_title else None,
                'slug_url': ('slug_url', {str_or_none}),
                'description': ('descripcion', {str_or_none}),
                'thumbnail': ('url_imagen', {url_or_none}),
                'uploader': ('usuario', 'username', {str_or_none}),
                'category': ('categoria', 'tipologia', 'nombre', {str_or_none}),
                'manifest_url': ('url_manifiesto', {url_or_none}),
                'subtitle_url': ('url_subtitulo', {url_or_none}),
                'duration': ('duracion', {parse_duration}),
                'view_count': ('cantidad_visitas', {int_or_none}),
                'like_count': ('cantidad_me_gusta', {int_or_none}),
                'dislike_count': ('cantidad_no_me_gusta', {int_or_none}),
                'comment_count': ('cantidad_comentarios', {int_or_none}),
                'tags': ('palabraClave', {list}),
                'playlist_channel': ('lista_reproduccion_canal', 0, ('nombre'), {str_or_none}),
                'playlist_channel_id': ('lista_reproduccion_canal', 0, ('id'), {str_or_none}),
                'channel_id': ('canal', 'id', {int_or_none}),
                'uploader_id': ('canal', 'usuario_id', {int_or_none}),
            }),  # type: ignore
            'channel': channel,
            'channel_url': urljoin(PictaBaseIE.ROOT_BASE_URL + 'canal/', urllib.parse.quote(f'{channel}')),
            'timestamp': timestamp,
            'modified_timestamp': unified_timestamp(modified_timestamp),
            'release_year': release if release else int_or_none(strftime_or_none(timestamp, '%Y')),
        }

        # Get Serie info
        if str(info_video.get('category')).lower() == 'serie':
            info_video.update(
                **traverse_obj(traverse_obj(result, ('categoria', 'capitulo')), {
                    'series': ('temporada', 'serie', 'nombre', {str_or_none}),
                    'series_id': ('temporada', 'serie', 'pelser_id', {str_or_none}),
                    'episode_number': ('numero', {int_or_none}),
                    'season_id': ('temporada', 'id', {str_or_none}),
                }))  # type: ignore

        if precios:
            info_video.update({'precios': precios})

        return info_video


# noinspection PyAbstractClass
class PictaIE(PictaBaseIE):
    IE_NAME = 'picta'
    IE_DESC = 'Picta videos'
    API_CLIENT_ID = 'ebkU3YeFu3So9hesQHrS8AZjEa4v7TiYbS5QZIgO'
    API_TOKEN_URL = 'https://api.picta.cu/o/token/'
    _HEADERS = {}

    _VALID_URL = (
        r'https?://(?:www\.)?picta\.cu/(?:medias|movie|documental|musical|short)/(?P<id>[\da-z-]+)'
        r'(?:\?playlist=(?P<playlist_id>[\da-z-]+))?'
    )

    _TESTS = [{
        'url': 'https://www.picta.cu/medias/presunto-inocente-1x06-2024-07-14-20-03-18-226686',
        'file': 'Presunto inocente 1x06.mp4',
        'md5': '69b108601d67f8b49d665b801c493ddf',
        'info_dict': {
            'id': '38868',
            'slug_url': 'presunto-inocente-1x06-2024-07-14-20-03-18-226686',
            'ext': 'mp4',
            'title': 'Presunto inocente 1x06',
            'thumbnail': r're:^https?://.*imagen/img.*\.png$',
            'duration': 2529,
            'upload_date': '20240714',
            'description': (
                'Un asesinato horrible trastoca a la Fiscalía de Chicago '
                'cuando uno de los suyos es sospechoso del crimen. '
                'El acusado deberá luchar por mantener unida a su familia.'),
            'uploader': 'leodanis',
            'timestamp': 1720987398,
            'release_year': 2024,
        },
    }, {
        'url': 'https://www.picta.cu/movie/dioses-rotos-tuovh5s2oodjg5bc',
        'only_matching': True,
    }, {
        'url': 'https://www.picta.cu/documental/ascenso-imperio-romano-6atcoxx2wmvcblsk',
        'only_matching': True,
    }, {
        'url': 'https://www.picta.cu/musical/ronkalunga-refranero-gtiu6juzuo3e4tex',
        'only_matching': True,
    }, {
        'url': 'https://www.picta.cu/short/spider-man-2026-nuevo-dia-trailer-azdvtcyshnje44kx',
        'only_matching': True,
    }]

    _LANGUAGES_CODES = ['es']
    _LANG_ES = _LANGUAGES_CODES[0]

    _SUBTITLE_FORMATS = ('srt',)

    def _perform_login(self, username, password):
        token_cache = self.cache.load(self._NETRC_MACHINE, username)
        if (
            token_cache is not None
            and time.time() <= token_cache['expires_in']
            and self._valid_token(username, token_cache['access_token'])
        ):
            token_auth = token_cache
        else:
            if not token_cache:
                self.cache.remove()
            token_auth = self._get_access_token(username, password)
        if token_auth:
            self._access_token = token_auth['access_token']
            self._refresh_token = token_auth['refresh_token']
            self._HEADERS = {'Authorization': f'Bearer {self._access_token}'}

    def _valid_token(self, username, token_cache) -> bool:
        try:
            token_response = self._download_json(
                self.API_BASE_URL + 'usuario/me/?format=json', video_id=None,
                note='Checking cached token',
                errnote=False, fatal=False,
                headers={'Authorization': f'Bearer {token_cache}'},
                expected_status=True,
                impersonate=True)

            if token_response:
                return token_response['username'] == username
            else:
                return False
        except ExtractorError as e:
            if isinstance(e.cause, HTTPError) and e.cause.status in (401, 403):
                return False
        return False

    def _get_access_token(self, username, password):
        data = urlencode_postdata({
            'grant_type': 'password',
            'client_id': self.API_CLIENT_ID,
            'client_secret': '',
            'username': username,
            'password': password})
        token_cache = {}
        try:
            self.report_login()
            token_data = self._download_json(
                self.API_TOKEN_URL, None,
                note='Fetching access token', data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                fatal=True, expected_status=True,
                impersonate=True)
        except ExtractorError as e:
            if isinstance(e.cause, HTTPError) and e.cause.status in (400, 401, 403):
                resp = self._parse_json(
                    e.cause.response.read().decode(), None, fatal=False) or {}
                message = str(resp.get('error_description'))
                self.report_warning(
                    f'{message} This video is only available for registered users. '
                    f'{self._login_hint("password")}')
            raise ExtractorError(e.orig_msg, expected=True)

        if token_data and 'access_token' in token_data:
            expires = time.time() + token_data['expires_in'] + 60
            token_cache = {
                'access_token': token_data['access_token'],
                'refresh_token': token_data['refresh_token'],
                'expires_in': expires}
            self.cache.store(self._NETRC_MACHINE, username, token_cache)
        else:
            return None

        return token_cache

    def _real_initialize(self):
        if not self._HEADERS:
            raise ExtractorError(
                f'This video is only available for registered users. '
                f'{self._login_hint("password")}',
                expected=True)
        self.playlist_id = None

    @classmethod
    def _match_playlist_id(cls, url):
        if '_VALID_URL_RE' not in cls.__dict__:
            cls._VALID_URL_RE = tuple(map(re.compile, variadic(cls._VALID_URL)))
        m = next(filter(None, (regex.match(url) for regex in cls._VALID_URL_RE)), None)
        assert m
        return m.group('playlist_id')

    def _get_subtitles(self, video):
        sub_lang_list = {}
        lang = self._LANG_ES
        sub_url = video.get('subtitle_url')

        if sub_url:
            sub_formats = []
            for ext in self._SUBTITLE_FORMATS:
                sub_formats.append(
                    {'name': 'Spanish', 'url': sub_url, 'ext': ext})
            sub_lang_list.update({f'{lang}': sub_formats})

        if not sub_lang_list:
            return {}
        return sub_lang_list

    def _fix_thumbnails(self, info):
        """ Fix thumbnails """
        thumbnails = []
        thumbnail = url_or_none(info.get('thumbnail'))

        if not thumbnail:
            return thumbnails

        # Try width/height from info first
        width = int_or_none(info.get('width'))
        height = int_or_none(info.get('height'))

        # Fallback: pick largest format that has width/height
        if not width or not height:
            _formats = info.get('formats') or []

            def _fmt_area(f):
                return (int_or_none(f.get('width')) or 0) * (int_or_none(f.get('height')) or 0)
            for f in sorted(_formats, key=_fmt_area, reverse=True):
                fw = int_or_none(f.get('width'))
                fh = int_or_none(f.get('height'))
                if fw and fh:
                    width, height = fw, fh
                    break

        # Fallback: try to parse size from thumbnail filename like _800x600
        if not width or not height:
            m = re.search(r'[_-](?P<w>\d{2,5})x(?P<h>\d{2,5})(?:\.[a-zA-Z]{2,4})?$', thumbnail)
            if m:
                width = int_or_none(m.group('w'))
                height = int_or_none(m.group('h'))
                thumbnail = thumbnail.replace(f'_{width}x{height}', '')

        # If we still don't have size info, return original thumbnail only
        if not width or not height:
            thumbnails.append({'url': thumbnail, 'id': 0})
            return thumbnails

        new_url = f'{thumbnail}_{width}x{height}'
        thumbnails.append({'url': new_url, 'id': 0, 'width': width, 'height': height})

        return thumbnails

    def _real_extract(self, url):
        playlist_id = None
        video_id = self._match_id(url)
        json_url = self.API_BASE_URL + 'publicacion/?format=json&slug_url_raw=%s' % video_id
        video = self._download_json(json_url, video_id, 'Downloading video JSON', headers=self._HEADERS)
        info = self._extract_video(video, video_id)
        playlist_channel_id = info.get('playlist_channel_id')
        matched_playlist_id = self._match_playlist_id(url)

        if (
            playlist_channel_id
            and self.playlist_id is None
            and (matched_playlist_id is None or matched_playlist_id == playlist_channel_id)
            and not bool(re.search(r'\bpictasearch$', url))
        ):
            playlist_id = str(playlist_channel_id)
            self.playlist_id = playlist_id
        # Download Playlist (--yes-playlist) in first place
        if (
            self.playlist_id is None
            and matched_playlist_id
            and not self.get_param('noplaylist')
        ):
            playlist_id = matched_playlist_id
            self.playlist_id = playlist_id
            self.to_screen(
                'Downloading user playlist %s - add --no-playlist to just download video'
                % playlist_id,
            )
            return self.url_result(
                self.ROOT_BASE_URL + 'medias/' + video_id + '?' + 'playlist=' + playlist_id,
                PictaUserPlaylistIE.ie_key(),
                playlist_id,
            )
        elif playlist_id and not self.get_param('noplaylist'):
            self.playlist_id = playlist_id
            self.to_screen(
                'Downloading channel playlist %s - add --no-playlist to just download video'
                % playlist_id,
            )
            return self.url_result(
                self.ROOT_BASE_URL + 'medias/' + video_id + '?' + 'playlistchannel=' + playlist_id,
                PictaChannelPlaylistIE.ie_key(),
                playlist_id,
            )
        elif self.get_param('noplaylist'):
            self.to_screen(
                'Downloading just video %s because of --no-playlist' % video_id,
            )

        # Get season number
        if str(info.get('category')).lower() == 'serie':
            url_json = self.API_BASE_URL + 'temporada/?format=json&serie_pelser_id=%s' % str(info.get('series_id'))
            seasons = self._download_json(url_json, video_id, 'Downloading seasons JSON', headers=self._HEADERS)
            info.update(traverse_obj(
                traverse_obj(
                    seasons, ('results', lambda _, s: str(s.get('id')) == str(info.get('season_id'))),
                    get_all=False),
                {'season_number': ('numero', {int_or_none})}))  # type: ignore

        availability = self._availability(**traverse_obj(video, {
            'is_private': ('pr', {lambda x: str(x) == 'false'}),
            'is_unlisted': ('eliminado', {lambda x: str(x) == 'true'}),
            'needs_premium': ('premium', {lambda x: str(x) == 'true'}),
            'needs_auth': ('precios', {lambda x: isinstance(x, list) and bool(x)}),
            'needs_subscription': ('planes', {lambda x: isinstance(x, list) and bool(x)}),
        }))  # type: ignore
        info.update({'availability': availability})

        formats = []
        # M3U8|MPD manifest
        manifest_url = info.get('manifest_url')
        src_ext = determine_ext(manifest_url)

        # Check for paid video
        price = info.get('precios')
        if isinstance(price, list) and price and not manifest_url:
            raise ExtractorError('This video is paid only', expected=True)

        if src_ext.startswith('m3u'):
            fmts, _ = self._extract_m3u8_formats_and_subtitles(manifest_url, video_id)
            formats.extend(fmts)
        elif src_ext == 'mpd':
            try:
                fmts, _ = self._extract_mpd_formats_and_subtitles(manifest_url, video_id, mpd_id='dash')
            except Exception:
                pass
                m3u8_url = urljoin(base_url(manifest_url), 'master.m3u8')
                fmts, _ = self._extract_m3u8_formats_and_subtitles(m3u8_url, video_id)
            formats.extend(fmts)

        if not formats:
            raise ExtractorError('Cannot find video formats', expected=True)

        info.update({'formats': formats})

        subtitle_url = url_or_none(info.get('subtitle_url'))
        subtitles = {}
        lang = self._LANG_ES
        if subtitle_url:
            for ext in self._SUBTITLE_FORMATS:
                sub_info = {
                    'name': 'Spanish',
                    'url': subtitle_url,
                    'ext': ext,
                }
            subtitles.setdefault(lang, []).append(sub_info)

        info.update({'subtitles': subtitles})

        # Try fix thumbnails format scale
        thumbnails = self._fix_thumbnails(info)
        info.update({'thumbnails': thumbnails})

        return info


# noinspection PyAbstractClass
class PictaPlaylistIE(PictaIE):
    API_PLAYLIST_ENDPOINT = PictaIE.API_BASE_URL + 'lista_reproduccion_canal/'
    IE_NAME = 'picta:playlist'
    IE_DESC = 'Picta playlist'
    _VALID_URL = (
        r'https?://(?:www\.)?picta\.cu/medias/(?P<id>[\da-z-]+)'
        r'\?(?:playlist|playlistchannel)=(?P<playlist_id>[\da-z-]+)$'
    )

    @classmethod
    def _match_playlist_id(cls, url):
        if '_VALID_URL_RE' not in cls.__dict__:
            cls._VALID_URL_RE = tuple(map(re.compile, variadic(cls._VALID_URL)))
        m = next(filter(None, (regex.match(url) for regex in cls._VALID_URL_RE)), None)
        assert m
        return m.group('playlist_id')

    def _extract_playlist(self, playlist, playlist_id=None, require_title=True):
        result = traverse_obj(playlist, ('results', 0), {dict})
        if not result:
            raise ExtractorError('Cannot find channel playlist!')

        return {
            **traverse_obj(result, {
                'id': ('id', {str_or_none}),
                'title': ('nombre', {str_or_none}) if require_title else None,
                'thumbnail': ('url_imagen', {url_or_none}),
                'entries': ('publicaciones', {list}),
            }),  # type: ignore
        }

    def _entries(self, playlist_id):
        json_url = self.API_PLAYLIST_ENDPOINT + '?format=json&id=%s' % playlist_id
        try:
            playlist = self._download_json(
                json_url, playlist_id, 'Downloading playlist JSON', headers=self._HEADERS)
            assert isinstance(playlist, dict) and playlist.get('count', 0) >= 1
        except AssertionError:
            raise ExtractorError('Playlist not exists!')

        info_playlist = self._extract_playlist(playlist, playlist_id)
        playlist_entries = info_playlist.get('entries')

        for video in playlist_entries:
            video_id = video.get('id')
            video_url = (
                self.ROOT_BASE_URL
                + 'medias/'
                + video.get('slug_url'))
            video_title = video.get('nombre')
            duration = parse_duration(video.get('duracion'))
            entries = self.url_result(video_url, PictaIE.ie_key(), video_id, video_title)
            entries.update({'duration': duration})
            yield entries

    def _real_extract(self, url):
        video_id = self._match_id(url)
        playlist_id = self._match_playlist_id(url)
        json_slug_url = self.API_BASE_URL + 'publicacion/?format=json&slug_url_raw=%s' % video_id

        video = traverse_obj(self._download_json(
            json_slug_url, video_id, 'Downloading video JSON', headers=self._HEADERS),
            ('results', 0))

        if not playlist_id:
            playlist_id = traverse_obj(
                video, ('lista_reproduccion_canal', 0, ('id'), {str_or_none}))

        entries = self._entries(playlist_id)

        json_url = self.API_PLAYLIST_ENDPOINT + '?format=json&id=%s' % playlist_id
        playlist = self._download_json(
            json_url, playlist_id, 'Downloading playlist JSON', headers=self._HEADERS)

        info = self._extract_playlist(playlist, playlist_id)
        info_playlist = self.playlist_result(
            entries, playlist_id,
            info.get('title'), self.IE_DESC)

        thumbnail = info.get('thumbnail') or traverse_obj(
            video,
            ('categoria', 'capitulo', 'temporada', 'serie', 'imagen_secundaria'),
            ('categoria', 'pelicula', 'imagen_secundaria'),
            ('url_imagen'), {url_or_none})

        if thumbnail:
            thumbnails = []
            thumbnail = f'{thumbnail}'
            m = re.search(
                r'[_-](?P<w>\d{2,5})x(?P<h>\d{2,5})(?:\.[a-zA-Z]{2,4})?$',
                thumbnail)
            if m is None:
                thumbnail = thumbnail + '_1280x720'
                width, height = 1280, 720
            else:
                width = int_or_none(m.group('w'))
                height = int_or_none(m.group('h'))
            thumb_info = {
                'url': thumbnail, 'id': 0,
                'width': width, 'height': height}
            thumbnails.append(thumb_info)
            info_playlist.update({'thumbnail': thumbnail})
            info_playlist.update({'thumbnails': thumbnails})

        return info_playlist


# noinspection PyAbstractClass
class PictaChannelPlaylistIE(PictaPlaylistIE):
    IE_NAME = 'picta:channel:playlist'
    IE_DESC = 'Picta channel playlist'

    _VALID_URL = (
        r'https?://(?:www\.)?picta\.cu/medias/(?P<id>[\da-z-]+)'
        r'\?playlistchannel=(?P<playlist_id>[\da-z-]+)$'
    )

    _TESTS = [{
        'url': 'https://www.picta.cu/medias/monarch-legado-monstruos-s02e01-7fu48wnjb6jrphoq',
        'info_dict': {
            'id': 55685,
            'title': 'Monarch: el legado de los monstruos S02E01',
            'thumbnail': r're:^https?://.*imagen/img.*\.jpeg$',
            'category': 'Serie',
            'playlist_channel': 'Monarch: El legado de los monstruos - Temp 2',
            'playlist_channel_id': '56161',
        },
    }]


# noinspection PyAbstractClass
class PictaUserPlaylistIE(PictaPlaylistIE):
    API_PLAYLIST_ENDPOINT = PictaIE.API_BASE_URL + 'lista_reproduccion/'
    IE_NAME = 'picta:user:playlist'
    IE_DESC = 'Picta user playlist'

    _VALID_URL = (
        r'https?://(?:www\.)?picta\.cu/medias/(?P<id>[\da-z-]+)'
        r'\?playlist=(?P<playlist_id>[\da-z-]+)$'
    )

    _TESTS = [{
        'url': 'https://www.picta.cu/medias/peaky-blinders-the-immortal-man-9f7rze22y4xzl6wc?playlist=22876',
        'info_dict': {
            'id': 22876,
            'title': 'test',
            '_type': 'playlist',
            'thumbnail': r're:^https?://.*imagen/img.*\.jpeg$',
        },
    }]

    def _extract_playlist(self, playlist, playlist_id=None, require_title=True):
        result = traverse_obj(playlist, ('results', 0), {dict})
        if not result:
            raise ExtractorError('Cannot find user playlist!')

        title = traverse_obj(result, ('nombre'), {str_or_none}) if require_title else None
        thumbnail = None
        thumbnail = traverse_obj(
            self._download_json(
                self.API_BASE_URL + 'usuario/me/?format=json',
                video_id=None, note='Fetching user avatar',
                errnote=False, fatal=False, headers=self._HEADERS),
            ('avatar'), {url_or_none})

        entries = traverse_obj(result, ('publicacion'), {list})

        return {
            'id': traverse_obj(result, ('id'), {str_or_none}) or playlist_id,
            'title': title,
            'thumbnail': f'{thumbnail}_320x320',
            'entries': entries,
        }


class PictaSearchIE(PictaIE, SearchInfoExtractor):
    IE_DESC = 'Picta search videos'
    IE_NAME = 'picta:search'
    _SEARCH_KEY = 'pictasearch'
    _VALID_URL = rf'{_SEARCH_KEY}(?P<prefix>|[1-9][0-9]*|all):(?P<query>[^?#&]+)?'
    _TESTS = [{
        'url': 'pictasearch20:smallville',
        'info_dict': {
            'id': 'picta:search20: smallville',
            'title': 'smallville',
        },
        'playlist_count': 20,
    }]
    _MAX_RESULTS = 100
    PAGE_SIZE = 20

    def _entries(self, results):
        for video in results:
            video_id = video.get('id')
            video_url = (
                self.ROOT_BASE_URL
                + 'medias/'
                + video.get('slug_url')
                + '/?playlist=pictasearch')
            video_title = video.get('nombre')
            duration = parse_duration(video.get('duracion'))
            entries = self.url_result(video_url, PictaIE.ie_key(), video_id, video_title)
            entries.update({'duration': duration})
            yield entries

    def _search_series_results(self, query):
        serie_search = self._download_json(
            self.API_BASE_URL + 'serie/', query,
            note=f'Searching serie: {query}',
            query={
                'format': 'json',
                'genero_raw_exclude': 'Anime__Novela__Infantil__Show__Deportivo__Videojuego__Dorama',
                'ordering': '-last_update',
                'nombre__contains': query},
            headers=self._HEADERS)

        results = traverse_obj(serie_search, ('results'), {list})
        if not results or not isinstance(results, list):
            raise ExtractorError(
                f'Could not find search results for query "{query}"', expected=True)

        serie_id = traverse_obj(traverse_obj(results, 0), ('pelser_id'), {int_or_none})
        seasons = self._download_json(
            self.API_BASE_URL + 'temporada/', query,
            note=f'Downloading serie id: {serie_id}',
            query={'serie_pelser_id': serie_id, 'format': 'json'},
            headers=self._HEADERS)
        seasons_id = [*traverse_obj(
            seasons, ('results', lambda _, s: s.get('id'), ('id')),
            get_all=True)]  # type: ignore

        for s in range(len(seasons_id)):
            season = seasons_id[s]
            for i in itertools.count(1):
                serie_response = self._download_json(
                    self.API_BASE_URL + 'publicacion/', query,
                    note=f'Downloading season id: {season} page: {i}',
                    query={
                        'temporada_id': season,
                        'page': i,
                        'page_size': self.PAGE_SIZE,
                        'ordering': '-fecha_publicado',
                        'format': 'json'},
                    headers=self._HEADERS)
                serie = traverse_obj(serie_response, ('results'), {list})
                if not serie or not isinstance(serie, list):
                    self.write_debug(
                        f'Could not find results for season: {season}')
                    if s == 0:
                        raise ExtractorError(
                            f'Could not find results for query "{query}"', expected=True)
                    break
                else:
                    yield from self._entries(serie)
                next_page = traverse_obj(serie_response, ('next'), {int_or_none})
                if next_page is None:
                    break

    def _search_results(self, query):
        next_page = None
        results = None

        for i in itertools.count(1):
            search_response = self._download_json(
                self.API_BASE_URL + 'publicacion/', query,
                note=f'Downloading search page: {i}',
                query={
                    'page': i,
                    'page_size': self.PAGE_SIZE,
                    'nombre__contains': query,
                    'format': 'json'},
                headers=self._HEADERS)

            results = traverse_obj(search_response, ('results'), {list})
            if results and isinstance(results, list):
                yield from self._entries(results)
            next_page = traverse_obj(search_response, ('next'), {int_or_none})
            if next_page is None or i >= math.ceil(self._MAX_RESULTS / self.PAGE_SIZE):
                break

        if not results:
            yield from self._search_series_results(query)

    def _real_extract(self, url):
        prefix, query = self._match_valid_url(url).group('prefix', 'query')
        parse_query = urllib.parse.unquote_plus(query)

        if prefix == '':
            return self._get_n_results(parse_query, 1)
        elif prefix == 'all':
            return self._get_n_results(parse_query, self._MAX_RESULTS)
        else:
            n = int(prefix)
            if n <= 0:
                raise ExtractorError(f'invalid download number {n} for query "{parse_query}"')
            elif n > self._MAX_RESULTS:
                self.report_warning(
                    '%s returns max %i results (you requested %i)' % (self._SEARCH_KEY, self._MAX_RESULTS, n))
                n = self._MAX_RESULTS
            return self._get_n_results(parse_query, n)

    def _get_n_results(self, query, n):
        return self.playlist_result(itertools.islice(
            self._search_results(query), 0, None if n == float('inf') else n),
            f'{self.IE_NAME}{n}: {query}',
            query, self.IE_DESC)


class PictaSearchURLIE(PictaSearchIE):
    IE_DESC = 'Picta search URLs'
    IE_NAME = f'{PictaSearchIE.IE_NAME}' + '_url'
    _VALID_URL = r'https?://(?:www\.)?picta\.cu/search/(?P<query>[^?#&]+)?'
    _TESTS = [{
        'url': 'https://www.picta.cu/search/smallville',
        'info_dict': {
            'id': 'picta:search_url: smallville',
            'title': 'smalville',
        },
        'playlist_count': 56,
    }, {
        'url': 'https://www.picta.cu/search/super mario',
        'info_dict': {
            'id': 'picta:search_url: super mario',
            'title': 'super mario',
        },
        'playlist_count': 4,
    }]

    def _real_extract(self, url):
        query = self._match_valid_url(url).group('query')
        parse_query = urllib.parse.unquote_plus(query)
        return self.playlist_result(
            self._search_results(parse_query),
            f'{self.IE_NAME}: {parse_query}',
            parse_query, self.IE_DESC)


class PictaSearchSerieIE(PictaSearchURLIE):
    IE_DESC = 'Picta search Serie'
    IE_NAME = f'{PictaSearchIE.IE_NAME}' + '_serie'
    _VALID_URL = r'https?://(?:www\.)?picta\.cu/serie/(?P<query>[^?#&]+)?'
    _TESTS = [{
        'url': 'https://www.picta.cu/serie/smallville',
        'info_dict': {
            'id': 'picta:search_serie: Gravity Falls',
            'title': 'Gravity Falls',
        },
        'playlist_count': 47,
    }, {
        'url': 'https://www.picta.cu/serie/Primal',
        'info_dict': {
            'id': 'picta:search_serie: Primal',
            'title': 'Primal',
        },
        'playlist_count': 30,
    }]

    def _search_results(self, query):
        yield from self._search_series_results(query)
