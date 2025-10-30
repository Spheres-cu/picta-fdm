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
                        if (isYTChannel && res?.hasOwnProperty("channel_id")) {
                            if (res?.hasOwnProperty("entries") && Array.isArray(res.entries) && res.entries.length > 1) {
                               let mapped_entries = mapEntries(res.entries);
                                entries = parseYTentries(mapped_entries) || [];

                                playlist._type = "playlist";
                                playlist.id = res.id;
                                playlist.title = res.title;
                                playlist.webpage_url = res.webpage_url;
                                playlist.thumbnails = !playlist.thumbnails ? res.thumbnails : playlist.thumbnails;
                                playlist.entries = entries;
                                resolve(playlist);
                                console.log("PlaylistYTChannel results: ", JSON.stringify(playlist, null));
                                return;
                            }
                        }

                        if (res?.hasOwnProperty("entries") && Array.isArray(res.entries)) {
                            if (res.entries.length > 0) {
                                playlist = res;
                                if (msAbstractParser.isYoutubeSource(obj.url)) {
                                    entries = parseYTentries(res.entries)
                                    playlist.entries = entries;
                                }

                                resolve(playlist);
                                return;
                            } else if (res.entries.length === 0) {
                                msAbstractParser.parse(obj, ["--no-playlist"]).then(function(detail) {
                                    try {
                                        entries.push({
                                            _type: "url",
                                            url: detail.webpage_url,
                                            title: detail.title,
                                            duration: detail.duration
                                        });

                                        playlist._type = "playlist";
                                        playlist.id = detail.id || res.id;
                                        playlist.title = detail.title || res.title;
                                        playlist.webpage_url = detail.webpage_url || res.webpage_url;
                                        playlist.entries = entries;
                                        playlist.thumbnails = detail.thumbnails;                                    
                                        resolve(playlist);
                                    } catch (e) {
                                        reject({
                                            error: e.message,
                                            isParseError: true
                                        });
                                    }

                                    }).catch(function(err) {
                                        console.log("Detailed parse fails:", err.error);
                                        try {
                                            playlist = res || {};
                                            resolve(playlist);
                                        } catch (e) {
                                            reject({
                                                error: e.message,
                                                isParseError: true
                                            });
                                        }
                                    });
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
                    console.log("Playlist results: ", JSON.stringify(playlist, null))                  
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