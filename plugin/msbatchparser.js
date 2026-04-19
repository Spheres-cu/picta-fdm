/* Parse playlists */

var msBatchVideoParser = (function() {
    function MsBatchVideoParser() {}

    MsBatchVideoParser.prototype = {

        parse: function(obj) {
            let customArg = [];
            customArg = msAbstractParser.isYoutubeSource(obj.url) ? ["--flat-playlist", "-I", "1:1000"] : ["--flat-playlist"];
            return msAbstractParser.parse(obj, customArg)
            .then(function(res) {
                return new Promise(function(resolve, reject) {
                    let entries = [];
                    let playlist = {};
                    let isYTChannel = /^https?:\/\/(?:www\.)?youtube\.com\/channel\/[\w-]+/i.test(obj.url);

                    try {
                        if (isYTChannel && res.channel_id) {
                            if (res.entries && Array.isArray(res.entries) && res.entries.length > 1) {
                               let mapped_entries = mapEntries(res.entries);
                                entries = parseYTentries(mapped_entries) || [];
                                playlist._type = "playlist";
                                playlist.id = res.id;
                                playlist.title = res.title;
                                playlist.webpage_url = res.webpage_url;
                                playlist.thumbnails = !playlist.thumbnails ? res.thumbnails : playlist.thumbnails;
                                playlist.entries = entries;
                                resolve(playlist);
                                return;
                            }
                        }

                        if (res.entries && Array.isArray(res.entries)) {
                            if (res.entries.length > 0) {
                                playlist = res;
                                if (msAbstractParser.isYoutubeSource(obj.url)) {
                                    entries = parseYTentries(res.entries)
                                    playlist.entries = entries;
                                }
                                resolve(playlist);
                                return;
                            }
                        }

                        if (res) {
                            entries.push({
                                _type: "url",
                                url: res.webpage_url,
                                title: res.title,
                                duration: res.duration
                            });
                            playlist._type = "playlist";
                            playlist.id = res.id;
                            playlist.title = res.title;
                            playlist.webpage_url = res.webpage_url;
                            playlist.entries = entries;
                            playlist.thumbnails = res.thumbnails;
                        }
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