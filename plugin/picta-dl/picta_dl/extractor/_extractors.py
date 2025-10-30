# flake8: noqa: F401
# isort: off

from .youtube import (  # Youtube is moved to the top to improve performance
    YoutubeIE,
    YoutubeClipIE,
    YoutubeFavouritesIE,
    YoutubeNotificationsIE,
    YoutubeHistoryIE,
    YoutubeTabIE,
    YoutubeLivestreamEmbedIE,
    YoutubePlaylistIE,
    YoutubeRecommendedIE,
    YoutubeSearchDateIE,
    YoutubeSearchIE,
    YoutubeSearchURLIE,
    YoutubeMusicSearchURLIE,
    YoutubeSubscriptionsIE,
    YoutubeTruncatedIDIE,
    YoutubeTruncatedURLIE,
    YoutubeYtBeIE,
    YoutubeYtUserIE,
    YoutubeWatchLaterIE,
    YoutubeShortsAudioPivotIE,
    YoutubeConsentRedirectIE,
)

# isort: on

from .commonprotocols import (
    MmsIE,
    RtmpIE,
    ViewSourceIE,
)
from .facebook import (
    FacebookAdsIE,
    FacebookIE,
    FacebookPluginsVideoIE,
    FacebookRedirectURLIE,
    FacebookReelIE,
)
from .generic import GenericIE
from .genericembeds import (
    HTML5MediaEmbedIE,
    QuotedHTMLIE,
)
from .picta import PictaIE, PictaChannelPlaylistIE, PictaUserPlaylistIE
