from typing import Dict, Any

import re
import math
import time
from ..networking.exceptions import HTTPError
from ..utils import (
    float_or_none,
    mimetype2ext,
    parse_duration,
    parse_codecs,
    int_or_none,
    unified_timestamp,
    try_get,
    ExtractorError,
    base_url,
    urljoin,
    determine_ext,
    urlencode_postdata,
    url_or_none,
    variadic,
    traverse_obj,
)
from .common import InfoExtractor

ROOT_BASE_URL = "https://www.picta.cu/"
API_BASE_URL = "https://api.picta.cu/v2/"
API_CLIENT_ID = "ebkU3YeFu3So9hesQHrS8AZjEa4v7TiYbS5QZIgO"
API_TOKEN_URL = "https://api.picta.cu/o/token/"


# noinspection PyAbstractClass
class PictaBaseIE(InfoExtractor):
    _NETRC_MACHINE = "picta"

    @staticmethod
    def _extract_video(video, video_id=None, require_title=True):
        result = traverse_obj(video, ('results', 0), expected_type=dict)
        if not result:
            raise ExtractorError("Cannot find video!")

        title = traverse_obj(result, ('nombre',)) if require_title else traverse_obj(result, ('nombre',))
        description = traverse_obj(result, ('descripcion',), expected_type=str)
        slug_url = traverse_obj(result, ('slug_url',), expected_type=str)
        uploader = traverse_obj(result, ('usuario', 'username'), expected_type=str)
        add_date = traverse_obj(result, ('fecha_creacion',))
        timestamp = int_or_none(unified_timestamp(add_date))
        duration = traverse_obj(result, ('duracion',))
        thumbnail = traverse_obj(result, ('url_imagen',))
        manifest_url = traverse_obj(result, ('url_manifiesto',))
        category = traverse_obj(result, ('categoria', 'tipologia', 'nombre'), expected_type=str)
        precios = traverse_obj(result, ('precios'), expected_type=list)

        playlist_channel = traverse_obj(
            result,
            ('lista_reproduccion_canal', 0),
            expected_type=dict
        )

        subtitle_url = traverse_obj(result, ('url_subtitulo',))
        video_id_from_result = traverse_obj(result, ('id',), expected_type=str)
        info_video = {
            "id": video_id_from_result or video_id,
            "title": title,
            "slug_url": slug_url,
            "description": description,
            "thumbnail": thumbnail,
            "duration": parse_duration(duration),
            "uploader": uploader,
            "timestamp": timestamp,
            "category": [category] if category else None,
            "manifest_url": manifest_url,
            "playlist_channel": playlist_channel,
            "subtitle_url": url_or_none(subtitle_url),
        }

        if precios:
            info_video['precios'] = precios

        return info_video


# noinspection PyAbstractClass
class PictaIE(PictaBaseIE):

    IE_NAME = "picta"
    IE_DESC = "Picta videos"
    _HEADERS = {}

    _VALID_URL = (
        r"https?://(?:www\.)?picta\.cu/(?:medias|movie|embed)/(?:\?v=)?(?P<id>[\da-z-]+)"
        r"(?:\?playlist=(?P<playlist_id>[\da-z-]+))?"
    )

    _TESTS = [
        {
            "url": "https://www.picta.cu/medias/orishas-everyday-2019-01-16-16-36-42-443003",
            "file": "Orishas - Everyday-orishas-everyday-2019-01-16-16-36-42-443003.webm",
            "md5": "7ffdeb0043500c4bb660c04e74e90f7a",
            "info_dict": {
                "id": "818",
                "slug_url": "orishas-everyday-2019-01-16-16-36-42-443003",
                "ext": "webm",
                "title": "Orishas - Everyday",
                "thumbnail": r"re:^https?://.*imagen/img.*\.png$",
                "duration": 204,
                "upload_date": "20190116",
                "description": "Orishas - Everyday (Video Oficial)",
                "uploader": "admin",
                "timestamp": 1547656602,
            },
            "params": {"format": "4"},
        },
        {
            "url": (
                "https://www.picta.cu/embed/"
                "palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895"
            ),
            "file": (
                "Palmiche Galeno tercer lugar en torneo virtual de "
                "robótica-palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895.mp4"
            ),
            "md5": "6031b7a3add2eade9c5bef7ecf5d4b02",
            "info_dict": {
                "id": "3500",
                "slug_url": "palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895",
                "ext": "mp4",
                "title": "Palmiche Galeno tercer lugar en torneo virtual de robótica",
                "thumbnail": r"re:^https?://.*imagen/img.*\.jpeg$",
                "duration": 252,
                "upload_date": "20200521",
                "description": (
                    "En esta emisión:\r\n"
                    "Iniciará en La Habana nuevo método para medir el consumo "
                    "eléctrico |  https://bit.ly/jtlecturacee\r\n"
                    "GICAcovid: nueva aplicación web para los centros de "
                    "aislamiento |  https://bit.ly/jtgicacovid\r\n"
                    "Obtuvo Palmiche tercer lugar en la primera competencia "
                    "virtual de robótica |  https://bit.ly/jtpalmichegaleno\r\n"
                    "\r\n"
                    "Síguenos en:\r\n"
                    "Facebook: http://www.facebook.com/JuventudTecnicaCuba\r\n"
                    "Twitter e Instagram: @juventudtecnica\r\n"
                    "Telegram: http://t.me/juventudtecnica"
                ),
                "uploader": "ernestoguerra21",
                "timestamp": 1590077731,
            },
        },
        {
            "url": "https://www.picta.cu/movie/phineas-ferb-pelicula-candace-universo-2020-08-28-21-00-32-857026",
            "only_matching": True,
        },
        {"url": "https://www.picta.cu/embed/?v=818", "only_matching": True},
        {
            "url": (
                "https://www.picta.cu/embed/"
                "palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895"
            ),
            "only_matching": True,
        },
    ]

    _LANGUAGES_CODES = ["es"]
    _LANG_ES = _LANGUAGES_CODES[0]

    _SUBTITLE_FORMATS = ("srt",)

    def _perform_login(self, username, password):
        token_cache = self.cache.load(self._NETRC_MACHINE, username)
        if (
            token_cache is not None
            and time.time() <= token_cache['expires_in']
        ):
            token_auth = token_cache
        else:
            if not token_cache:
                self.cache.remove()
            token_auth = self._get_access_token(username, password)
        if token_auth:
            self._access_token = token_auth['access_token']
            self._refresh_token = token_auth['refresh_token']
            self._HEADERS = {"Authorization": f"Bearer {self._access_token}"}

    def _get_access_token(self, username, password):
        data = urlencode_postdata({
            "grant_type": "password",
            "client_id": API_CLIENT_ID,
            "client_secret": "",
            "username": username,
            "password": password,
        })
        token_cache = {}
        try:
            self.report_login()
            token_data = self._download_json(
                API_TOKEN_URL, None,
                note="Fetching access token",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                fatal=True,  # Crash if token fetch fails
                expected_status=True,
            )
        except ExtractorError as e:
            if isinstance(e.cause, HTTPError) and e.cause.status in (400, 401, 403):
                resp = self._parse_json(
                    e.cause.response.read().decode(), None, fatal=False) or {}
                message = str(resp.get('error_description'))
                self.report_warning(
                    f'{message} This video is only available for registered users. '
                    f'{self._login_hint("password")}'
                )
            raise ExtractorError(e.orig_msg, expected=True)

        if token_data and 'access_token' in token_data:
            expires = time.time() + token_data['expires_in'] + 60
            token_cache = {
                'access_token': token_data['access_token'],
                'refresh_token': token_data['refresh_token'],
                'expires_in': expires
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
                expected=True
            )
        self.playlist_id = None

    @classmethod
    def _match_playlist_id(cls, url):
        if "_VALID_URL_RE" not in cls.__dict__:
            cls._VALID_URL_RE = tuple(map(re.compile, variadic(cls._VALID_URL)))
        m = next(filter(None, (regex.match(url) for regex in cls._VALID_URL_RE)), None)
        assert m
        return m.group("playlist_id")

    def _get_subtitles(self, video):
        sub_lang_list = {}
        lang = self._LANG_ES

        sub_url = video.get("subtitle_url")

        if sub_url:
            sub_formats = []
            for ext in self._SUBTITLE_FORMATS:
                sub_formats.append(
                    {
                        "name": "Spanish",
                        "url": sub_url,
                        "ext": ext,
                    }
                )
            sub_lang_list[lang] = sub_formats
        if not sub_lang_list:
            self.report_warning("video doesn't have subtitles")
            return {}
        return sub_lang_list

    def _extract_mpd_formats(
        self,
        mpd_url,
        video_id,
        mpd_id=None,
        note=None,
        errnote=None,
        fatal=True,
        formats_dict={},
        data=None,
        headers={},
        query={},
    ):
        res = self._download_xml_handle(
            mpd_url,
            video_id,
            note=note or "Downloading MPD manifest",
            errnote=errnote or "Failed to download MPD manifest",
            fatal=fatal,
            data=data,
            headers=headers,
            query=query,
        )
        if res is False:
            return []
        mpd_doc, urlh = res
        if mpd_doc is None:
            return []
        mpd_base_url = base_url(urlh.url)

        return self._parse_mpd_formats(
            mpd_doc,
            mpd_id=mpd_id,
            mpd_base_url=mpd_base_url,
            formats_dict=formats_dict,
            mpd_url=mpd_url,
        )

    def _parse_mpd_formats(
        self, mpd_doc, mpd_id=None, mpd_base_url="", formats_dict={}, mpd_url=None
    ):
        """
        Parse formats from MPD manifest.
        References:
            1. MPEG-DASH Standard, ISO/IEC 23009-1:2014(E),
            http://standards.iso.org/ittf/PubliclyAvailableStandards/c065274_ISO_IEC_23009-1_2014.zip
            2. https://en.wikipedia.org/wiki/Dynamic_Adaptive_Streaming_over_HTTP
        Note: Fix MPD manifest for Picta
            3. https://developer.mozilla.org/en-US/docs/Web/Guide/Audio_and_video_delivery/Setting_up_adaptive_streaming_media_sources
        """
        if mpd_doc.get("type") == "dynamic":
            return []

        namespace = self._search_regex(
            r"(?i)^{([^}]+)?}MPD$", mpd_doc.tag, "namespace", default=None
        )

        def _add_ns(path):
            return self._xpath_ns(path, namespace)

        def is_drm_protected(element):
            return element.find(_add_ns("ContentProtection")) is not None

        def extract_multisegment_info(element, ms_parent_info):
            ms_info = ms_parent_info.copy()

            # As per [1, 5.3.9.2.2] SegmentList and SegmentTemplate share some
            # common attributes and elements.  We will only extract relevant
            # for us.
            def extract_common(source):
                segment_timeline = source.find(_add_ns("SegmentTimeline"))
                if segment_timeline is not None:
                    s_e = segment_timeline.findall(_add_ns("S"))
                    if s_e:
                        ms_info["total_number"] = 0
                        ms_info["s"] = []
                        for s in s_e:
                            r = int(s.get("r", 0))
                            ms_info["total_number"] += 1 + r
                            ms_info["s"].append(
                                {
                                    "t": int(s.get("t", 0)),
                                    # @d is mandatory (see [1, 5.3.9.6.2, Table 17, page 60])
                                    "d": int(s.attrib["d"]),
                                    "r": r,
                                }
                            )
                start_number = source.get("startNumber")
                if start_number:
                    ms_info["start_number"] = int(start_number)
                timescale = source.get("timescale")
                if timescale:
                    ms_info["timescale"] = int(timescale)
                segment_duration = source.get("duration")
                if segment_duration:
                    ms_info["segment_duration"] = float(segment_duration)

            def extract_Initialization(source):
                initialization = source.find(_add_ns("Initialization"))
                # TODO: Different Initialization sourceURL. See docs/manifests/*.mpd
                if initialization is not None:
                    ms_info["initialization_url"] = initialization.attrib['range']

            segment_list = element.find(_add_ns("SegmentList"))
            if segment_list is not None:
                extract_common(segment_list)
                extract_Initialization(segment_list)
                segment_urls_e = segment_list.findall(_add_ns("SegmentURL"))
                if segment_urls_e:
                    # TODO: Different SegmentURL media / mediaRange
                    # Picta dont use fragments
                    segment_urls = [
                        segment.attrib.get("media")
                        for segment in segment_urls_e
                        if segment.attrib.get("media") is not None
                    ]
                    if segment_urls:
                        ms_info["segment_urls"] = segment_urls
            else:
                segment_template = element.find(_add_ns("SegmentTemplate"))
                if segment_template is not None:
                    extract_common(segment_template)
                    media = segment_template.get("media")
                    if media:
                        ms_info["media"] = media
                    initialization = segment_template.get("initialization")
                    if initialization:
                        ms_info["initialization"] = initialization
                    else:
                        extract_Initialization(segment_template)
            return ms_info

        mpd_duration = parse_duration(mpd_doc.get("mediaPresentationDuration"))
        formats = []
        for period in mpd_doc.findall(_add_ns("Period")):
            period_duration = parse_duration(period.get("duration")) or mpd_duration
            period_ms_info = extract_multisegment_info(
                period,
                {
                    "start_number": 1,
                    "timescale": 1,
                },
            )
            for adaptation_set in period.findall(_add_ns("AdaptationSet")):
                if is_drm_protected(adaptation_set):
                    continue
                adaption_set_ms_info = extract_multisegment_info(
                    adaptation_set, period_ms_info
                )
                for representation in adaptation_set.findall(_add_ns("Representation")):
                    if is_drm_protected(representation):
                        continue
                    representation_attrib = adaptation_set.attrib.copy()
                    representation_attrib.update(representation.attrib)
                    # According to [1, 5.3.7.2, Table 9, page 41], @mimeType is mandatory
                    mime_type = representation_attrib["mimeType"]
                    content_type = mime_type.split("/")[0]
                    if content_type == "text" or content_type == "application":
                        # TODO implement WebVTT downloading
                        pass
                    elif content_type in ("video", "audio"):
                        base_url = ""
                        for element in (
                            representation,
                            adaptation_set,
                            period,
                            mpd_doc,
                        ):
                            base_url_e = element.find(_add_ns("BaseURL"))
                            if base_url_e is not None:
                                base_url = base_url_e.text + base_url
                                if re.match(r"^https?://", base_url):
                                    break
                        if mpd_base_url and not re.match(r"^https?://", base_url):
                            if not mpd_base_url.endswith(
                                "/"
                            ) and not base_url.startswith("/"):
                                mpd_base_url += "/"
                            base_url = mpd_base_url + base_url
                        representation_id = representation_attrib.get("id")
                        lang = representation_attrib.get("lang")
                        url_el = representation.find(_add_ns("BaseURL"))
                        filesize = int_or_none(
                            url_el.attrib.get(
                                "{http://youtube.com/yt/2012/10/10}contentLength"
                            )
                            if url_el is not None
                            else None
                        )
                        bandwidth = int_or_none(representation_attrib.get("bandwidth"))
                        f: Dict[str, Any] = {
                            "format_id": "%s-%s" % (mpd_id, representation_id)
                            if mpd_id
                            else representation_id,
                            "manifest_url": mpd_url,
                            "ext": mimetype2ext(mime_type),
                            "width": int_or_none(representation_attrib.get("width")),
                            "height": int_or_none(representation_attrib.get("height")),
                            "tbr": float_or_none(bandwidth, 1000),
                            "asr": int_or_none(
                                representation_attrib.get("audioSamplingRate")
                            ),
                            "fps": int_or_none(representation_attrib.get("frameRate")),
                            "language": lang
                            if lang not in ("mul", "und", "zxx", "mis")
                            else None,
                            "format_note": "DASH %s" % content_type,
                            "filesize": filesize,
                            "container": f'{mimetype2ext(mime_type)}' + "_dash",
                        }
                        f.update(parse_codecs(representation_attrib.get("codecs")))
                        representation_ms_info = extract_multisegment_info(
                            representation, adaption_set_ms_info
                        )

                        def prepare_template(template_name, identifiers):
                            tmpl = representation_ms_info[template_name]
                            # First of, % characters outside $...$ templates
                            # must be escaped by doubling for proper processing
                            # by % operator string formatting used further (see
                            # https://github.com/ytdl-org/youtube-dl/issues/16867).
                            t = ""
                            in_template = False
                            for c in tmpl:
                                t += c
                                if c == "$":
                                    in_template = not in_template
                                elif c == "%" and not in_template:
                                    t += c
                            # Next, $...$ templates are translated to their
                            # %(...) counterparts to be used with % operator
                            t = t.replace("$RepresentationID$", representation_id)
                            t = re.sub(
                                r"\$(%s)\$" % "|".join(identifiers), r"%(\1)d", t
                            )
                            t = re.sub(
                                r"\$(%s)%%([^$]+)\$" % "|".join(identifiers),
                                r"%(\1)\2",
                                t,
                            )
                            t.replace("$$", "$")
                            return t

                        # @initialization is a regular template like @media one
                        # so it should be handled just the same way (see
                        # https://github.com/ytdl-org/youtube-dl/issues/11605)
                        if "initialization" in representation_ms_info:
                            initialization_template = prepare_template(
                                "initialization",
                                # As per [1, 5.3.9.4.2, Table 15, page 54] $Number$ and
                                # $Time$ shall not be included for @initialization thus
                                # only $Bandwidth$ remains
                                ("Bandwidth",),
                            )
                            representation_ms_info[
                                "initialization_url"
                            ] = initialization_template % {
                                "Bandwidth": bandwidth,
                            }

                        def location_key(location):
                            return (
                                "url" if re.match(r"^https?://", location) else "path"
                            )

                        if (
                            "segment_urls" not in representation_ms_info
                            and "media" in representation_ms_info
                        ):

                            media_template = prepare_template(
                                "media", ("Number", "Bandwidth", "Time")
                            )
                            media_location_key = location_key(media_template)

                            # As per [1, 5.3.9.4.4, Table 16, page 55] $Number$ and $Time$
                            # can't be used at the same time
                            if (
                                "%(Number" in media_template
                                and "s" not in representation_ms_info
                            ):
                                segment_duration = None
                                if (
                                    "total_number" not in representation_ms_info
                                    and "segment_duration" in representation_ms_info
                                ):
                                    segment_duration = float_or_none(
                                        representation_ms_info["segment_duration"],
                                        representation_ms_info["timescale"],
                                    )
                                    representation_ms_info["total_number"] = int(
                                        math.ceil(
                                            float(period_duration) / segment_duration
                                        )
                                    )
                                representation_ms_info["fragments"] = [
                                    {
                                        media_location_key: media_template
                                        % {
                                            "Number": segment_number,
                                            "Bandwidth": bandwidth,
                                        },
                                        "duration": segment_duration,
                                    }
                                    for segment_number in range(
                                        representation_ms_info["start_number"],
                                        representation_ms_info["total_number"]
                                        + representation_ms_info["start_number"],
                                    )
                                ]
                            else:
                                # $Number*$ or $Time$ in media template with S list available
                                # Example $Number*$: http://www.svtplay.se/klipp/9023742/stopptid-om-bjorn-borg
                                # Example $Time$: https://play.arkena.com/embed/avp/v2/player/media/b41dda37-d8e7-4d3f-b1b5-9a9db578bdfe/1/129411
                                representation_ms_info["fragments"] = []
                                segment_time = 0
                                segment_d = None
                                segment_number = representation_ms_info["start_number"]

                                def add_segment_url():
                                    segment_url = media_template % {
                                        "Time": segment_time,
                                        "Bandwidth": bandwidth,
                                        "Number": segment_number,
                                    }
                                    representation_ms_info["fragments"].append(
                                        {
                                            media_location_key: segment_url,
                                            "duration": float_or_none(
                                                segment_d,
                                                representation_ms_info["timescale"],
                                            ),
                                        }
                                    )

                                for num, s in enumerate(representation_ms_info["s"]):
                                    segment_time = s.get("t") or segment_time
                                    segment_d = s["d"]
                                    add_segment_url()
                                    segment_number += 1
                                    for r in range(s.get("r", 0)):
                                        segment_time += segment_d
                                        add_segment_url()
                                        segment_number += 1
                                    segment_time += segment_d
                        elif (
                            "segment_urls" in representation_ms_info
                            and "s" in representation_ms_info
                        ):
                            # No media template
                            # Example: https://www.youtube.com/watch?v=iXZV5uAYMJI
                            # or any YouTube dashsegments video
                            fragments = []
                            segment_index = 0
                            timescale = representation_ms_info["timescale"]
                            for s in representation_ms_info["s"]:
                                duration = float_or_none(s["d"], timescale)
                                for r in range(s.get("r", 0) + 1):
                                    segment_uri = representation_ms_info[
                                        "segment_urls"
                                    ][segment_index]
                                    fragments.append(
                                        {
                                            location_key(segment_uri): segment_uri,
                                            "duration": duration,
                                        }
                                    )
                                    segment_index += 1
                            representation_ms_info["fragments"] = fragments
                        elif "segment_urls" in representation_ms_info:
                            # Segment URLs with no SegmentTimeline
                            # Example: https://www.seznam.cz/zpravy/clanek/cesko-zasahne-vitr-o-sile-vichrice-muze-byt-i-zivotu-nebezpecny-39091
                            # https://github.com/ytdl-org/youtube-dl/pull/14844
                            fragments = []
                            segment_duration = (
                                float_or_none(
                                    representation_ms_info["segment_duration"],
                                    representation_ms_info["timescale"],
                                )
                                if "segment_duration" in representation_ms_info
                                else None
                            )
                            for segment_url in representation_ms_info["segment_urls"]:
                                fragment = {
                                    location_key(segment_url): segment_url,
                                }
                                if segment_duration:
                                    fragment["duration"] = segment_duration
                                fragments.append(fragment)
                            representation_ms_info["fragments"] = fragments
                        # If there is a fragments key available then we correctly recognized fragmented media.
                        # Otherwise we will assume unfragmented media with direct access. Technically, such
                        # assumption is not necessarily correct since we may simply have no support for
                        # some forms of fragmented media renditions yet, but for now we'll use this fallback.
                        if "fragments" in representation_ms_info:
                            f.update(
                                {
                                    # NB: mpd_url may be empty when MPD manifest is parsed from a string
                                    "url": mpd_url or base_url,
                                    "fragment_base_url": base_url,
                                    "fragments": [],
                                    "protocol": "http_dash_segments",
                                }
                            )
                            if "initialization_url" in representation_ms_info:
                                initialization_url = representation_ms_info[
                                    "initialization_url"
                                ]
                                if not f.get("url"):
                                    f["url"] = initialization_url
                                f["fragments"].append(
                                    {
                                        location_key(
                                            initialization_url
                                        ): initialization_url
                                    }
                                )
                            f["fragments"].extend(representation_ms_info["fragments"])
                        else:
                            # Assuming direct URL to unfragmented media.
                            f["url"] = base_url

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
                            "Unknown MIME type %s in DASH manifest" % mime_type
                        )
        return formats

    def _fix_thumbnails(self, info):
        """ Fix thumbnails """
        thumbnails = []
        thumbnail = url_or_none(info.get("thumbnail"))

        if not thumbnail:
            return thumbnails

        # Try width/height from info first
        width = int_or_none(info.get("width"))
        height = int_or_none(info.get("height"))

        # Fallback: pick largest format that has width/height
        if not width or not height:
            _formats = info.get("formats") or []

            def _fmt_area(f):
                return (int_or_none(f.get("width")) or 0) * (int_or_none(f.get("height")) or 0)
            for f in sorted(_formats, key=_fmt_area, reverse=True):
                fw = int_or_none(f.get("width"))
                fh = int_or_none(f.get("height"))
                if fw and fh:
                    width, height = fw, fh
                    break

        # Fallback: try to parse size from thumbnail filename like _800x600
        if not width or not height:
            m = re.search(r"[_-](?P<w>\d{2,5})x(?P<h>\d{2,5})(?:\.[a-zA-Z]{2,4})?$", thumbnail)
            if m:
                width = int_or_none(m.group("w"))
                height = int_or_none(m.group("h"))
                thumbnail = thumbnail.replace(f"_{width}x{height}", "")

        # If we still don't have size info, return original thumbnail only
        if not width or not height:
            thumbnails.append({"url": thumbnail, "id": 0})
            return thumbnails

        new_url = f"{thumbnail}_{width}x{height}"
        thumbnails.append({"url": new_url, "id": 0, "width": width, "height": height})

        return thumbnails

    def _real_extract(self, url):
        playlist_id = None
        video_id = self._match_id(url)
        json_url = API_BASE_URL + "publicacion/?format=json&slug_url_raw=%s" % video_id
        video = self._download_json(json_url, video_id, "Downloading video JSON", headers=self._HEADERS)

        info = self._extract_video(video, video_id)
        if (
            info["playlist_channel"]
            and self.playlist_id is None
            and self._match_playlist_id(url) is None
        ):
            playlist_id = info["playlist_channel"].get("id")
            self.playlist_id = playlist_id
        # Download Playlist (--yes-playlist) in first place
        if (
            self.playlist_id is None
            and self._match_playlist_id(url)
            and not self._downloader.params.get("noplaylist")
        ):
            playlist_id = str(self._match_playlist_id(url))
            self.playlist_id = playlist_id
            self.to_screen(
                "Downloading playlist %s - add --no-playlist to just download video"
                % playlist_id
            )
            return self.url_result(
                ROOT_BASE_URL + "medias/" + video_id + "?" + "playlist=" + playlist_id,
                PictaUserPlaylistIE.ie_key(),
                playlist_id,
            )
        elif playlist_id and not self._downloader.params.get("noplaylist"):
            playlist_id = str(playlist_id)
            self.to_screen(
                "Downloading playlist %s - add --no-playlist to just download video"
                % playlist_id
            )
            return self.url_result(
                ROOT_BASE_URL + "medias/" + video_id + "?" + "playlist=" + playlist_id,
                PictaChannelPlaylistIE.ie_key(),
                playlist_id,
            )
        elif self._downloader.params.get("noplaylist"):
            self.to_screen(
                "Downloading just video %s because of --no-playlist" % video_id
            )

        formats = []
        # M3U8|MPD manifest
        manifest_url = info.get("manifest_url")
        src_ext = determine_ext(manifest_url)

        # Check for paid video
        price = info.get("precios")
        if isinstance(price, list) and price and not manifest_url:
            raise ExtractorError("This video is paid only", expected=True)

        if src_ext.startswith("m3u"):
            formats.extend(
                self._extract_m3u8_formats(manifest_url, video_id, "mp4", m3u8_id="hls")
            )
        elif src_ext == "mpd":
            formats.extend(
                self._extract_mpd_formats(manifest_url, video_id, mpd_id="dash")
            )

        if not formats:
            raise ExtractorError("Cannot find video formats", expected=True)

        info["formats"] = formats

        # subtitles (from API)
        subtitles = self.extract_subtitles(info)

        # Try to find an HLS subtitle playlist named 'text-spa-external.m3u8'
        # in the same directory as the video manifest. Some Picta manifests
        # provide video as MPD but place the subtitles alongside using that
        # filename. Build the candidate URL by joining the manifest URL with
        # the known subtitle filename and attempt to download it.
        subtitle_m3u8_url = None
        subtitle_url = url_or_none(info.get("subtitle_url"))
        lang = self._LANG_ES
        if subtitle_url:
            sub = self._request_webpage(
                subtitle_url,
                video_id,
                note="Checking subtitle url",
                errnote=False,
                fatal=False,
            )
            if not sub:
                subtitle_m3u8_url = urljoin(manifest_url, "text-spa-external.m3u8")

                if subtitle_m3u8_url:
                    try:
                        m3u8_doc = self._download_webpage(
                            subtitle_m3u8_url,
                            video_id,
                            note="Downloading m3u8 subtitle info",
                            errnote="Failed to download m3u8 information",
                            fatal=False,
                        )
                        if (
                            m3u8_doc
                            and "#EXTM3U" in m3u8_doc
                            and ".vtt" in m3u8_doc
                        ):
                            sub_info = {
                                "name": "Spanish",
                                "url": subtitle_m3u8_url,
                                "ext": "vtt",
                                "protocol": "m3u8_native"
                            }
                            subtitles.setdefault(lang, []).append(sub_info)
                            info["subtitle_url"] = None
                    except ExtractorError:
                        # Best-effort; do not break extraction if anything goes wrong here.
                        pass
            else:
                for ext in self._SUBTITLE_FORMATS:
                    sub_info = {
                        "name": "Spanish",
                        "url": subtitle_url,
                        "ext": ext
                    }
                subtitles.setdefault(lang, []).append(sub_info)

        info["subtitles"] = subtitles

        # Try fix thumbnails format scale
        thumbnails = self._fix_thumbnails(info)

        info['thumbnails'] = thumbnails

        return info


# noinspection PyAbstractClass
class PictaEmbedIE(InfoExtractor):
    IE_NAME = "picta:embed"
    IE_DESC = "Picta embedded videos"
    _VALID_URL = r"https?://www\.picta\.cu/embed/(?:\?v=)?(?P<id>[\d]+)"

    _TESTS = [
        {
            "url": "https://www.picta.cu/embed/?v=818",
            "file": "Orishas - Everyday-orishas-everyday-2019-01-16-16-36-42-443003.webm",
            "md5": "7ffdeb0043500c4bb660c04e74e90f7a",
            "info_dict": {
                "id": "818",
                "slug_url": "orishas-everyday-2019-01-16-16-36-42-443003",
                "ext": "webm",
                "title": "Orishas - Everyday",
                "thumbnail": r"re:^https?://.*imagen/img.*\.png$",
                "duration": 204,
                "upload_date": "20190116",
                "description": "Orishas - Everyday (Video Oficial)",
                "uploader": "admin",
                "timestamp": 1547656602,
            },
            "params": {"format": "4"},
        },
        {
            "url": (
                "https://www.picta.cu/embed/"
                "palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895"
            ),
            "file": (
                "Palmiche Galeno tercer lugar en torneo virtual de "
                "robótica-palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895.mp4"
            ),
            "md5": "6031b7a3add2eade9c5bef7ecf5d4b02",
            "info_dict": {
                "id": "3500",
                "slug_url": "palmiche-galeno-tercer-lugar-torneo-virtual-robotica-2020-05-21-16-15-31-431895",
                "ext": "mp4",
                "title": "Palmiche Galeno tercer lugar en torneo virtual de robótica",
                "thumbnail": r"re:^https?://.*imagen/img.*\.jpeg$",
                "duration": 252,
                "upload_date": "20200521",
                "description": (
                    "En esta emisión:\r\n"
                    "Iniciará en La Habana nuevo método para medir el consumo "
                    "eléctrico |  https://bit.ly/jtlecturacee\r\n"
                    "GICAcovid: nueva aplicación web para los centros de "
                    "aislamiento |  https://bit.ly/jtgicacovid\r\n"
                    "Obtuvo Palmiche tercer lugar en la primera competencia "
                    "virtual de robótica |  https://bit.ly/jtpalmichegaleno\r\n"
                    "\r\n"
                    "Síguenos en:\r\n"
                    "Facebook: http://www.facebook.com/JuventudTecnicaCuba\r\n"
                    "Twitter e Instagram: @juventudtecnica\r\n"
                    "Telegram: http://t.me/juventudtecnica"
                ),
                "uploader": "ernestoguerra21",
                "timestamp": 1590077731,
            },
        },
    ]

    def _real_extract(self, url):
        return self.url_result(url, PictaIE.ie_key())


# noinspection PyAbstractClass
class PictaPlaylistIE(PictaIE):
    API_PLAYLIST_ENDPOINT = API_BASE_URL + "lista_reproduccion_canal/"
    IE_NAME = "picta:playlist"
    IE_DESC = "Picta playlist"
    _VALID_URL = (
        r"https?://(?:www\.)?picta\.cu/(?:medias|movie|embed)/(?P<id>[\da-z-]+)"
        r"\?playlist=(?P<playlist_id>[\da-z-]+)$"
    )

    @classmethod
    def _match_playlist_id(cls, url):
        if "_VALID_URL_RE" not in cls.__dict__:
            cls._VALID_URL_RE = tuple(map(re.compile, variadic(cls._VALID_URL)))
        m = next(filter(None, (regex.match(url) for regex in cls._VALID_URL_RE)), None)
        assert m
        return m.group("playlist_id")

    def _extract_playlist(self, playlist, playlist_id=None, require_title=True):
        result = traverse_obj(playlist, ('results', 0), expected_type=dict)
        if not result:
            raise ExtractorError("Cannot find playlist!")

        title = (
            traverse_obj(result, ('nombre',))
            if require_title
            else traverse_obj(result, ('nombre',))
        )
        thumbnail = traverse_obj(result, ('url_imagen',))
        entries = traverse_obj(result, ('publicaciones',), expected_type=list)

        return {
            "id": traverse_obj(result, ('id',), expected_type=str) or playlist_id,
            "title": title,
            "thumbnail": thumbnail,
            "entries": entries,
        }

    def _entries(self, playlist_id):
        json_url = self.API_PLAYLIST_ENDPOINT + "?format=json&id=%s" % playlist_id
        playlist = {}
        try:
            playlist = self._download_json(
                json_url, playlist_id, "Downloading playlist JSON", headers=self._HEADERS
            )
            assert playlist.get("count", 0) >= 1
        except ExtractorError as e:
            if isinstance(e.cause, HTTPError) and e.cause.status in (403,):
                self.raise_login_required(
                    msg="This playlist is only available for registered users. Check your username and password"
                )
        except AssertionError:
            raise ExtractorError("Playlist no exists!")

        info_playlist = self._extract_playlist(playlist, playlist_id)
        playlist_entries = info_playlist.get("entries")
        entries: Dict[str, Any] = {}
        for video in playlist_entries:
            video_id = video.get("id")
            video_url = (
                ROOT_BASE_URL
                + "medias/"
                + video.get("slug_url")
            )
            video_title = video.get("nombre")
            duration = parse_duration(video.get("duracion"))
            entries = self.url_result(video_url, PictaIE.ie_key(), video_id, video_title)
            entries['duration'] = duration
            yield entries

    def _real_extract(self, url):
        playlist = {}
        info_playlist: Dict[str, Any] = {}
        playlist_id = self._match_playlist_id(url)
        entries = self._entries(playlist_id)
        json_url = self.API_PLAYLIST_ENDPOINT + "?format=json&id=%s" % playlist_id
        playlist = self._download_json(
            json_url, playlist_id, "Downloading playlist JSON", headers=self._HEADERS
        )
        info = self._extract_playlist(playlist, playlist_id)
        info_playlist = self.playlist_result(entries, playlist_id, info.get('title'))

        video_id = self._match_id(url)
        json_slug_url = API_BASE_URL + "publicacion/?format=json&slug_url_raw=%s" % video_id
        video = self._download_json(json_slug_url, video_id, "Downloading video JSON", headers=self._HEADERS)

        result = traverse_obj(video, ('results', 0))
        thumbnail = None
        if result:
            model = traverse_obj(result, ('categoria', 'tipologia', 'modelo'))
            if model == 'capitulo':
                thumbnail = traverse_obj(
                    result,
                    ('categoria', 'capitulo', 'temporada', 'serie', 'imagen_secundaria')
                )
            elif model == 'pelicula':
                thumbnail = traverse_obj(
                    result,
                    ('categoria', 'pelicula', 'imagen_secundaria')
                )
            else:
                thumbnail = traverse_obj(
                    result, ('url_imagen',)
                )

        if thumbnail:
            thumbnail = f'{str(thumbnail) + "_1280x720"}'
            thumbnails = []
            thumb_info = {
                "url": thumbnail,
                "id": 0,
                "width": 1280,
                "height": 720
            }
            thumbnails.append(thumb_info)
            info_playlist['thumbnail'] = thumbnail
            info_playlist["thumbnails"] = thumbnails

        return info_playlist


# noinspection PyAbstractClass
class PictaChannelPlaylistIE(PictaPlaylistIE):
    IE_NAME = "picta:channel:playlist"
    IE_DESC = "Picta channel playlist"

    _TEST_CHANNEL = {
        "url": (
            "https://www.picta.cu/medias/"
            "201-paradigma-devops-implementacion-tecnomatica-2020-07-05-22-44-41-299736"
        ),
        "info_dict": {
            "id": 4441,
            "title": "D\u00eda 2: Telecomunicaciones, Redes y Ciberseguridad",
            "thumbnail": r"re:^https?://.*imagen/img.*\.jpeg$",
        },
    }


# noinspection PyAbstractClass
class PictaUserPlaylistIE(PictaPlaylistIE):
    API_PLAYLIST_ENDPOINT = API_BASE_URL + "lista_reproduccion/"
    IE_NAME = "picta:user:playlist"
    IE_DESC = "Picta user playlist"

    _TEST_USER = {
        "url": "https://www.picta.cu/medias/fundamento-big-data-2020-08-09-19-47-15-230297?playlist=129",
        "info_dict": {
            "id": 129,
            "title": "picta-dl",
            "thumbnail": None,
        },
    }

    def _extract_playlist(self, playlist, playlist_id=None, require_title=True):
        if len(playlist["results"]) == 0:
            raise ExtractorError("Cannot find playlist!")

        title = (
            playlist["results"][0]["nombre"]
            if require_title
            else playlist.get("results")[0].get("nombre")
        )
        thumbnail = None
        entries = try_get(playlist, lambda x: x["results"][0]["publicacion"])
        # Playlist User need update slug_url video
        for entry in entries:
            video_id = entry.get("id")
            json_url = API_BASE_URL + "publicacion/?format=json&id=%s" % video_id
            video = self._download_json(json_url, video_id, "Downloading video JSON", headers=self._HEADERS)
            info = self._extract_video(video, video_id)
            entry["slug_url"] = info.get("slug_url")

        return {
            "id": try_get(playlist, lambda x: x["results"][0]["id"], str)
            or playlist_id,
            "title": title,
            "thumbnail": thumbnail,
            "entries": entries,
        }
