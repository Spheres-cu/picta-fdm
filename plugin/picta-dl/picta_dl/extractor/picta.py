import itertools
import math
import re
import time
import urllib.parse
from typing import Any

from ..networking.exceptions import HTTPError
from ..utils import (
    ExtractorError,
    base_url,
    determine_ext,
    float_or_none,
    int_or_none,
    mimetype2ext,
    parse_codecs,
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

ROOT_BASE_URL = 'https://www.picta.cu/'
API_BASE_URL = 'https://api.picta.cu/v2/'


# noinspection PyAbstractClass
class PictaBaseIE(InfoExtractor):
    _NETRC_MACHINE = 'picta'

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
            'channel_url': urljoin(ROOT_BASE_URL + 'canal/', channel),
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
        r'https?://(?:www\.)?picta\.cu/(?:medias|movie|documental|musical)/(?P<id>[\da-z-]+)'
        r'(?:\?playlist=(?P<playlist_id>[\da-z-]+))?'
    )

    _TESTS = [
        {
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
        },
        {
            'url': 'https://www.picta.cu/movie/dioses-rotos-tuovh5s2oodjg5bc',
            'only_matching': True,
        },
        {
            'url': 'https://www.picta.cu/documental/ascenso-imperio-romano-6atcoxx2wmvcblsk',
            'only_matching': True,
        },
        {
            'url': 'https://www.picta.cu/musical/ronkalunga-refranero-gtiu6juzuo3e4tex',
            'only_matching': True,
        },
    ]

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
        API_USER_ENDPOINT = API_BASE_URL + 'usuario/me/?format=json'
        try:
            token_response = self._download_json(
                API_USER_ENDPOINT, video_id=None,
                note='Checking cached token',
                errnote=False, fatal=False,
                headers={'Authorization': f'Bearer {token_cache}'},
                expected_status=True)

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
            'password': password,
        })
        token_cache = {}
        try:
            self.report_login()
            token_data = self._download_json(
                self.API_TOKEN_URL, None,
                note='Fetching access token', data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                fatal=True, expected_status=True)
        except ExtractorError as e:
            if isinstance(e.cause, HTTPError) and e.cause.status in (400, 401, 403):
                resp = self._parse_json(
                    e.cause.response.read().decode(), None, fatal=False) or {}
                message = str(resp.get('error_description'))
                self.report_warning(
                    f'{message} This video is only available for registered users. '
                    f'{self._login_hint("password")}',
                )
            raise ExtractorError(e.orig_msg, expected=True)

        if token_data and 'access_token' in token_data:
            expires = time.time() + token_data['expires_in'] + 60
            token_cache = {
                'access_token': token_data['access_token'],
                'refresh_token': token_data['refresh_token'],
                'expires_in': expires,
            }
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
                    {'name': 'Spanish', 'url': sub_url, 'ext': ext })
            sub_lang_list.update({f'{lang}': sub_formats})

        if not sub_lang_list:
            return {}
        return sub_lang_list

    def _extract_mpd_formats(
            self, mpd_url, video_id, mpd_id=None, note=None, errnote=None,
            fatal=True, formats_dict={}, data=None, headers={}, query={}):

        if self.get_param('ignore_no_formats_error'):
            fatal = False

        res = self._download_xml_handle(
            mpd_url, video_id,
            note=note or 'Downloading MPD manifest',
            errnote=errnote or 'Failed to download MPD manifest',
            fatal=fatal, data=data, headers=headers, query=query)
        if res is False:
            return []
        mpd_doc, urlh = res
        if mpd_doc is None:
            return []
        mpd_base_url = base_url(urlh.url)

        return self._parse_mpd_formats(
            mpd_doc, mpd_id=mpd_id,
            mpd_base_url=mpd_base_url,
            formats_dict=formats_dict,
            mpd_url=mpd_url)

    def _parse_mpd_formats(
            self, mpd_doc, mpd_id=None, mpd_base_url='',
            formats_dict={}, mpd_url=None):
        """
        # noqa
        Parse formats from MPD manifest.
        References:
        1. MPEG-DASH Standard, ISO/IEC 23009-1:2014(E),
        http://standards.iso.org/ittf/PubliclyAvailableStandards/c065274_ISO_IEC_23009-1_2014.zip
        2. https://en.wikipedia.org/wiki/Dynamic_Adaptive_Streaming_over_HTTP
        - Note: Fix MPD manifest for Picta
        3. https://developer.mozilla.org/en-US/docs/Web/Guide/Audio_and_video_delivery/Setting_up_adaptive_streaming_media_sources
        """
        if mpd_doc.get('type') == 'dynamic':
            return []

        namespace = self._search_regex(
            r'(?i)^{([^}]+)?}MPD$', mpd_doc.tag, 'namespace', default=None,
        )

        def _add_ns(path):
            return self._xpath_ns(path, namespace)

        def is_drm_protected(element):
            return element.find(_add_ns('ContentProtection')) is not None

        def extract_multisegment_info(element, ms_parent_info):
            ms_info = ms_parent_info.copy()

            # As per [1, 5.3.9.2.2] SegmentList and SegmentTemplate share some
            # common attributes and elements.  We will only extract relevant
            # for us.
            def extract_common(source):
                segment_timeline = source.find(_add_ns('SegmentTimeline'))
                if segment_timeline is not None:
                    s_e = segment_timeline.findall(_add_ns('S'))
                    if s_e:
                        ms_info['total_number'] = 0
                        ms_info['s'] = []
                        for s in s_e:
                            r = int(s.get('r', 0))
                            ms_info['total_number'] += 1 + r
                            ms_info['s'].append(
                                {
                                    't': int(s.get('t', 0)),
                                    # @d is mandatory (see [1, 5.3.9.6.2, Table 17, page 60])
                                    'd': int(s.attrib['d']),
                                    'r': r,
                                },
                            )
                start_number = source.get('startNumber')
                if start_number:
                    ms_info['start_number'] = int(start_number)
                timescale = source.get('timescale')
                if timescale:
                    ms_info['timescale'] = int(timescale)
                segment_duration = source.get('duration')
                if segment_duration:
                    ms_info['segment_duration'] = float(segment_duration)

            def extract_Initialization(source):
                initialization = source.find(_add_ns('Initialization'))
                # TODO: Different Initialization sourceURL. See docs/manifests/*.mpd
                if initialization is not None:
                    ms_info['initialization_url'] = initialization.attrib['range']

            segment_list = element.find(_add_ns('SegmentList'))
            if segment_list is not None:
                extract_common(segment_list)
                extract_Initialization(segment_list)
                segment_urls_e = segment_list.findall(_add_ns('SegmentURL'))
                if segment_urls_e:
                    # TODO: Different SegmentURL media / mediaRange
                    # Picta dont use fragments
                    segment_urls = [
                        segment.attrib.get('media')
                        for segment in segment_urls_e
                        if segment.attrib.get('media') is not None
                    ]
                    if segment_urls:
                        ms_info['segment_urls'] = segment_urls
            else:
                segment_template = element.find(_add_ns('SegmentTemplate'))
                if segment_template is not None:
                    extract_common(segment_template)
                    media = segment_template.get('media')
                    if media:
                        ms_info['media'] = media
                    initialization = segment_template.get('initialization')
                    if initialization:
                        ms_info['initialization'] = initialization
                    else:
                        extract_Initialization(segment_template)
            return ms_info

        mpd_duration = parse_duration(mpd_doc.get('mediaPresentationDuration'))
        formats = []
        for period in mpd_doc.findall(_add_ns('Period')):
            period_duration = parse_duration(period.get('duration')) or mpd_duration
            period_ms_info = extract_multisegment_info(
                period,
                {
                    'start_number': 1,
                    'timescale': 1,
                },
            )
            for adaptation_set in period.findall(_add_ns('AdaptationSet')):
                if is_drm_protected(adaptation_set):
                    continue
                adaption_set_ms_info = extract_multisegment_info(
                    adaptation_set, period_ms_info,
                )
                for representation in adaptation_set.findall(_add_ns('Representation')):
                    if is_drm_protected(representation):
                        continue
                    representation_attrib = adaptation_set.attrib.copy()
                    representation_attrib.update(representation.attrib)
                    # According to [1, 5.3.7.2, Table 9, page 41], @mimeType is mandatory
                    mime_type = representation_attrib['mimeType']
                    content_type = mime_type.split('/')[0]
                    if content_type == 'text' or content_type == 'application':
                        # TODO: implement WebVTT downloading
                        pass
                    elif content_type in ('video', 'audio'):
                        base_url = ''
                        for element in (
                            representation,
                            adaptation_set,
                            period,
                            mpd_doc,
                        ):
                            base_url_e = element.find(_add_ns('BaseURL'))
                            if base_url_e is not None:
                                base_url = base_url_e.text + base_url
                                if re.match(r'^https?://', base_url):
                                    break
                        if mpd_base_url and not re.match(r'^https?://', base_url):
                            if not mpd_base_url.endswith(
                                '/',
                            ) and not base_url.startswith('/'):
                                mpd_base_url += '/'
                            base_url = mpd_base_url + base_url
                        representation_id = representation_attrib.get('id')
                        lang = representation_attrib.get('lang')
                        url_el = representation.find(_add_ns('BaseURL'))
                        filesize = int_or_none(
                            url_el.attrib.get(
                                '{http://youtube.com/yt/2012/10/10}contentLength',
                            )
                            if url_el is not None
                            else None,
                        )
                        bandwidth = int_or_none(representation_attrib.get('bandwidth'))
                        f: dict[str, Any] = {
                            'format_id': '%s-%s' % (mpd_id, representation_id)
                            if mpd_id
                            else representation_id,
                            'manifest_url': mpd_url,
                            'ext': mimetype2ext(mime_type),
                            'width': int_or_none(representation_attrib.get('width')),
                            'height': int_or_none(representation_attrib.get('height')),
                            'tbr': float_or_none(bandwidth, 1000),
                            'asr': int_or_none(
                                representation_attrib.get('audioSamplingRate'),
                            ),
                            'fps': int_or_none(representation_attrib.get('frameRate')),
                            'language': lang
                            if lang not in ('mul', 'und', 'zxx', 'mis')
                            else None,
                            'format_note': 'DASH %s' % content_type,
                            'filesize': filesize,
                            'container': f'{mimetype2ext(mime_type)}' + '_dash',
                        }
                        f.update(parse_codecs(representation_attrib.get('codecs')))
                        representation_ms_info = extract_multisegment_info(
                            representation, adaption_set_ms_info,
                        )

                        def prepare_template(template_name, identifiers):
                            tmpl = representation_ms_info[template_name]
                            # First of, % characters outside $...$ templates
                            # must be escaped by doubling for proper processing
                            # by % operator string formatting used further (see
                            # https://github.com/ytdl-org/youtube-dl/issues/16867).
                            t = ''
                            in_template = False
                            for c in tmpl:
                                t += c
                                if c == '$':
                                    in_template = not in_template
                                elif c == '%' and not in_template:
                                    t += c
                            # Next, $...$ templates are translated to their
                            # %(...) counterparts to be used with % operator
                            t = t.replace('$RepresentationID$', representation_id)
                            t = re.sub(
                                r'\$(%s)\$' % '|'.join(identifiers), r'%(\1)d', t,
                            )
                            t = re.sub(
                                r'\$(%s)%%([^$]+)\$' % '|'.join(identifiers),
                                r'%(\1)\2',
                                t,
                            )
                            t.replace('$$', '$')
                            return t

                        # @initialization is a regular template like @media one
                        # so it should be handled just the same way (see
                        # https://github.com/ytdl-org/youtube-dl/issues/11605)
                        if 'initialization' in representation_ms_info:
                            initialization_template = prepare_template(
                                'initialization',
                                # As per [1, 5.3.9.4.2, Table 15, page 54] $Number$ and
                                # $Time$ shall not be included for @initialization thus
                                # only $Bandwidth$ remains
                                ('Bandwidth',),
                            )
                            representation_ms_info[
                                'initialization_url'
                            ] = initialization_template % {
                                'Bandwidth': bandwidth,
                            }

                        def location_key(location):
                            return (
                                'url' if re.match(r'^https?://', location) else 'path'
                            )

                        if (
                            'segment_urls' not in representation_ms_info
                            and 'media' in representation_ms_info
                        ):

                            media_template = prepare_template(
                                'media', ('Number', 'Bandwidth', 'Time'),
                            )
                            media_location_key = location_key(media_template)

                            # As per [1, 5.3.9.4.4, Table 16, page 55] $Number$ and $Time$
                            # can't be used at the same time
                            if (
                                '%(Number' in media_template
                                and 's' not in representation_ms_info
                            ):
                                segment_duration = None
                                if (
                                    'total_number' not in representation_ms_info
                                    and 'segment_duration' in representation_ms_info
                                ):
                                    segment_duration = float_or_none(
                                        representation_ms_info['segment_duration'],
                                        representation_ms_info['timescale'],
                                    )
                                    representation_ms_info['total_number'] = math.ceil(
                                        float(period_duration) / segment_duration,
                                    )
                                representation_ms_info['fragments'] = [
                                    {
                                        media_location_key: media_template
                                        % {
                                            'Number': segment_number,
                                            'Bandwidth': bandwidth,
                                        },
                                        'duration': segment_duration,
                                    }
                                    for segment_number in range(
                                        representation_ms_info['start_number'],
                                        representation_ms_info['total_number']
                                        + representation_ms_info['start_number'],
                                    )
                                ]
                            else:
                                # $Number*$ or $Time$ in media template with S list available
                                # Example $Number*$: http://www.svtplay.se/klipp/9023742/stopptid-om-bjorn-borg
                                # Example $Time$: https://play.arkena.com/embed/avp/v2/player/media/b41dda37-d8e7-4d3f-b1b5-9a9db578bdfe/1/129411 # noqa
                                representation_ms_info['fragments'] = []
                                segment_time = 0
                                segment_d = None
                                segment_number = representation_ms_info['start_number']

                                def add_segment_url():
                                    segment_url = media_template % {
                                        'Time': segment_time,
                                        'Bandwidth': bandwidth,
                                        'Number': segment_number,
                                    }
                                    representation_ms_info['fragments'].append(
                                        {
                                            media_location_key: segment_url,
                                            'duration': float_or_none(
                                                segment_d,
                                                representation_ms_info['timescale'],
                                            ),
                                        },
                                    )

                                for _num, s in enumerate(representation_ms_info['s']):
                                    segment_time = s.get('t') or segment_time
                                    segment_d = s['d']
                                    add_segment_url()
                                    segment_number += 1
                                    for _r in range(s.get('r', 0)):
                                        segment_time += segment_d
                                        add_segment_url()
                                        segment_number += 1
                                    segment_time += segment_d
                        elif (
                            'segment_urls' in representation_ms_info
                            and 's' in representation_ms_info
                        ):
                            # No media template
                            # Example: https://www.youtube.com/watch?v=iXZV5uAYMJI
                            # or any YouTube dashsegments video
                            fragments = []
                            segment_index = 0
                            timescale = representation_ms_info['timescale']
                            for s in representation_ms_info['s']:
                                duration = float_or_none(s['d'], timescale)
                                for _r in range(s.get('r', 0) + 1):
                                    segment_uri = representation_ms_info[
                                        'segment_urls'
                                    ][segment_index]
                                    fragments.append(
                                        {
                                            location_key(segment_uri): segment_uri,
                                            'duration': duration,
                                        },
                                    )
                                    segment_index += 1
                            representation_ms_info['fragments'] = fragments
                        elif 'segment_urls' in representation_ms_info:
                            # Segment URLs with no SegmentTimeline
                            # Example: https://www.seznam.cz/zpravy/clanek/cesko-zasahne-vitr-o-sile-vichrice-muze-byt-i-zivotu-nebezpecny-39091  # noqa
                            # https://github.com/ytdl-org/youtube-dl/pull/14844
                            fragments = []
                            segment_duration = (
                                float_or_none(
                                    representation_ms_info['segment_duration'],
                                    representation_ms_info['timescale'],
                                )
                                if 'segment_duration' in representation_ms_info
                                else None
                            )
                            for segment_url in representation_ms_info['segment_urls']:
                                fragment = {
                                    location_key(segment_url): segment_url,
                                }
                                if segment_duration:
                                    fragment['duration'] = segment_duration
                                fragments.append(fragment)
                            representation_ms_info['fragments'] = fragments
                        # If there is a fragments key available then we correctly recognized fragmented media.
                        # Otherwise we will assume unfragmented media with direct access. Technically, such
                        # assumption is not necessarily correct since we may simply have no support for
                        # some forms of fragmented media renditions yet, but for now we'll use this fallback.
                        if 'fragments' in representation_ms_info:
                            f.update(
                                {
                                    # NB: mpd_url may be empty when MPD manifest is parsed from a string
                                    'url': mpd_url or base_url,
                                    'fragment_base_url': base_url,
                                    'fragments': [],
                                    'protocol': 'http_dash_segments',
                                },
                            )
                            if 'initialization_url' in representation_ms_info:
                                initialization_url = representation_ms_info[
                                    'initialization_url'
                                ]
                                if not f.get('url'):
                                    f['url'] = initialization_url
                                f['fragments'].append(
                                    {
                                        location_key(
                                            initialization_url,
                                        ): initialization_url,
                                    },
                                )
                            f['fragments'].extend(representation_ms_info['fragments'])
                        else:
                            # Assuming direct URL to unfragmented media.
                            f['url'] = base_url

                        # According to [1, 5.3.5.2, Table 7, page 35] @id of Representation
                        # is not necessarily unique within a Period thus formats with
                        # the same `format_id` are quite possible. There are numerous examples
                        # of such manifests (see https://github.com/ytdl-org/youtube-dl/issues/15111,
                        # https://github.com/ytdl-org/youtube-dl/issues/13919)
                        full_info = formats_dict.get(representation_id, {}).copy()
                        full_info.update(f)
                        formats.append(full_info)
                        formats.append(f)
                    else:
                        self.report_warning(
                            'Unknown MIME type %s in DASH manifest' % mime_type,
                        )
        return formats

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
        json_url = API_BASE_URL + 'publicacion/?format=json&slug_url_raw=%s' % video_id
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
                ROOT_BASE_URL + 'medias/' + video_id + '?' + 'playlist=' + playlist_id,
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
                ROOT_BASE_URL + 'medias/' + video_id + '?' + 'playlistchannel=' + playlist_id,
                PictaChannelPlaylistIE.ie_key(),
                playlist_id,
            )
        elif self.get_param('noplaylist'):
            self.to_screen(
                'Downloading just video %s because of --no-playlist' % video_id,
            )

        # Get season number
        if str(info.get('category')).lower() == 'serie':
            url_json = API_BASE_URL + 'temporada/?format=json&serie_pelser_id=%s' % str(info.get('series_id'))
            seasons = self._download_json(url_json, video_id, 'Downloading seasons JSON', headers=self._HEADERS)
            info.update(traverse_obj(
                traverse_obj(
                    seasons, ('results', lambda i, s: str(s.get('id')) == str(info.get('season_id'))),
                    get_all=False),
                {'season_number': ('numero', {int_or_none}) }))  # type: ignore

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
            formats.extend(
                self._extract_m3u8_formats(manifest_url, video_id, 'mp4', m3u8_id='hls'),
            )
        elif src_ext == 'mpd':
            formats.extend(
                self._extract_mpd_formats(manifest_url, video_id, mpd_id='dash'),
            )

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
    API_PLAYLIST_ENDPOINT = API_BASE_URL + 'lista_reproduccion_canal/'
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
            raise ExtractorError('Playlist no exists!')

        info_playlist = self._extract_playlist(playlist, playlist_id)
        playlist_entries = info_playlist.get('entries')

        for video in playlist_entries:
            video_id = video.get('id')
            video_url = (
                ROOT_BASE_URL
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
        json_slug_url = API_BASE_URL + 'publicacion/?format=json&slug_url_raw=%s' % video_id

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
        info_playlist = self.playlist_result(entries, playlist_id, info.get('title'))

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

    _TESTS = [
        {
            'url': 'https://www.picta.cu/medias/monarch-legado-monstruos-s02e01-7fu48wnjb6jrphoq',
            'info_dict': {
                'id': 55685,
                'title': 'Monarch: el legado de los monstruos S02E01',
                'thumbnail': r're:^https?://.*imagen/img.*\.jpeg$',
                'category': 'Serie',
                'playlist_channel': 'Monarch: El legado de los monstruos - Temp 2',
                'playlist_channel_id': '56161',
            },
        },
    ]


# noinspection PyAbstractClass
class PictaUserPlaylistIE(PictaPlaylistIE):
    API_PLAYLIST_ENDPOINT = API_BASE_URL + 'lista_reproduccion/'
    IE_NAME = 'picta:user:playlist'
    IE_DESC = 'Picta user playlist'

    _VALID_URL = (
        r'https?://(?:www\.)?picta\.cu/medias/(?P<id>[\da-z-]+)'
        r'\?playlist=(?P<playlist_id>[\da-z-]+)$'
    )

    _TESTS = [
        {
            'url': 'https://www.picta.cu/medias/peaky-blinders-the-immortal-man-9f7rze22y4xzl6wc?playlist=22876',
            'info_dict': {
                'id': 22876,
                'title': 'test',
                '_type': 'playlist',
                'thumbnail': r're:^https?://.*imagen/img.*\.jpeg$',
            },
        },
    ]

    def _extract_playlist(self, playlist, playlist_id=None, require_title=True):
        result = traverse_obj(playlist, ('results', 0), {dict})
        if not result:
            raise ExtractorError('Cannot find user playlist!')

        title = traverse_obj(result, ('nombre'), {str_or_none}) if require_title else None
        thumbnail = None
        thumbnail = traverse_obj(
            self._download_json(
                API_BASE_URL + 'usuario/me/?format=json',
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
    API_SEARCH_ENDPOINT = API_BASE_URL + 'publicacion/'

    def _search_results(self, query):
        next_page = None
        for i in itertools.count(1):
            search_response = self._download_json(
                self.API_SEARCH_ENDPOINT, query,
                note=f'Downloading search page: {i}',
                query={
                    'page': i,
                    'page_size': self.PAGE_SIZE,
                    'nombre__contains': query,
                    'format':'json'},
                headers=self._HEADERS)
            results = traverse_obj(search_response, ('results'), {list})
            if not results or not isinstance(results, list):
                raise ExtractorError(
                    f'Could not find search results for query "{query}"', expected=True)
            for video in results:
                video_id = video.get('id')
                video_url = (
                    ROOT_BASE_URL
                    + 'medias/'
                    + video.get('slug_url')
                    + '/?playlist=pictasearch')
                video_title = video.get('nombre')
                duration = parse_duration(video.get('duracion'))
                entries = self.url_result(video_url, PictaIE.ie_key(), video_id, video_title)
                entries.update({'duration': duration})
                yield entries

            next_page = traverse_obj(search_response, ('next'), {int_or_none})
            if not results or next_page is None or i >= math.ceil(self._MAX_RESULTS / self.PAGE_SIZE):
                break

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
                self.report_warning('%s returns max %i results (you requested %i)' % (self._SEARCH_KEY, self._MAX_RESULTS, n))
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
        },
        {
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
