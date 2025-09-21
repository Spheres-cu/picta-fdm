/* Parse playlists */

var msBatchVideoParser = (function() {
    function MsBatchVideoParser() {}

    MsBatchVideoParser.prototype = {

        parse: function(obj) {
            return msAbstractParser.parse(obj, ["--flat-playlist"])
                .then(function(res) {
                    return new Promise(function(resolve, reject) {
                        var entries = [];
                        var playlist = {};

                        try {
                            if (res?.hasOwnProperty("entries")) {
                                let thumb_url = res.thumbnail;
                                if (thumb_url) {
                                    let Thumb = [{
                                            "url": thumb_url + "_" + 1280 + "x" + 720,
                                            "height": 720,
                                            "width": 1280
                                        },
                                        {
                                            "url": thumb_url + "_" + 720 + "x" + 1280,
                                            "height": 1280,
                                            "width": 720
                                        }
                                    ];
                                    res.thumbnails = Thumb;
                                }

                                playlist = res;
                            } else if (res) {
                                entries.push({
                                    _type: "url",
                                    url: res.webpage_url,
                                    title: res.title,
                                    duration: res.duration
                                });

                                let thumb_url = res.thumbnail;
                                if (thumb_url) {

                                    let height = Math.round(res.height / 4);
                                    let width = Math.round(res.width / 4);

                                    var Thumbnails = [{
                                            "url": thumb_url + "_" + width + "x" + height,
                                            "height": height,
                                            "width": width,
                                            "preference": 3
                                        },
                                        {
                                            "url": thumb_url + "_" + 220 + "x" + 180,
                                            "height": 180,
                                            "width": 220,
                                            "preference": 2
                                        },
                                        {
                                            "url": thumb_url + "_" + 180 + "x" + 220,
                                            "height": 180,
                                            "width": 220,
                                            "preference": 1
                                        }

                                    ];
                                }

                                playlist._type = "playlist";
                                playlist.id = res.id;
                                playlist.title = res.title;
                                playlist.webpage_url = res.webpage_url;
                                playlist.thumbnails = Thumbnails;
                                playlist.entries = entries;
                            }
                            // console.log("Playlist results: ", JSON.stringify(playlist, null));
                            resolve(playlist);
                        } catch (e) {
                            reject({
                                error: e.message,
                                isParseError: true
                            });
                        }
                    });
                });
        },

        isSupportedSource: msAbstractParser.isSupportedSource,

        supportedSourceCheckPriority: function() {
            return msAbstractParser.supportedSourceCheckPriority() + 1;
        },

        isPossiblySupportedSource: msAbstractParser.isPossiblySupportedSource,

        overrideUrlPolicy: msAbstractParser.overrideUrlPolicy,

        minIntevalBetweenQueryInfoDownloads: msAbstractParser.minIntevalBetweenQueryInfoDownloads
    };

    return new MsBatchVideoParser();
}());