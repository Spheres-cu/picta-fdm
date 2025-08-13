/* Parse playlists */

var msBatchVideoParser = (function()
{
    function MsBatchVideoParser()
    {
    }

    MsBatchVideoParser.prototype = {

        parse: function (obj)
        {
            return msAbstractParser.parse(obj, [])
            .then(function(res)
            {
                return new Promise(function(resolve, reject)
                {
                    var Thumbnails = [];
                    var entries = [];
                    var playlist = {};

                    try
                    {
                        if (res?.hasOwnProperty("entries"))
                        {
                            for (let i = 0; i <= res.entries.length; ++i)
                            {
                                if (res.entries[i] != null)
                                {
                                    if (!res.title && res.entries[i].playlist_channel.nombre) {
                                        playlist.title = res.entries[i].playlist_channel.nombre;
                                    }

                                    if (res.entries[i].thumbnail)
                                    {
                                        let thumb_url = res.entries[i].thumbnail;
                                        let height = Math.round(res.entries[i].height / 4);
                                        let width = Math.round(res.entries[i].width / 4);

                                        let Thumb =
                                        {
                                            "url": thumb_url + "_" + width + "x" + height,
                                            "height": height,
                                            "width": width,
                                            "id": i
                                        };

                                        Thumbnails.push(Thumb);
                                    }
                                    entries.push({
                                        _type: "url",
                                        url: res.entries[i].webpage_url,
                                        title: res.entries[i].title
                                    });
                                }
                            }
                            playlist._type = res._type;
                            playlist.id = res.id;
                            playlist.webpage_url = res.webpage_url;
                            playlist.thumbnails = Thumbnails;
                            playlist.entries = entries;
                        }
                        else if (res)
                        {
                            entries.push({
                                _type: "url",
                                url: res.webpage_url,
                                title: res.title
                            });

                            let thumb_url = res.thumbnail;
                            if (thumb_url)
                            {
                                let height = Math.round(res.height / 4);
                                let width = Math.round(res.width / 4);

                                Thumbnails = [
                                {
                                    "url": thumb_url + "_" + width + "x" + height,
                                    "height": height,
                                    "width": width
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
                        console.log("Playlist results: ", JSON.stringify(playlist, null, " "));
                        resolve(playlist);
                    }
                    catch (e)
                    {
                        reject({error: e.message, isParseError:true});
                    }
                });
            });
        },

        isSupportedSource: msAbstractParser.isSupportedSource,

        supportedSourceCheckPriority: function()
        {
            return msAbstractParser.supportedSourceCheckPriority() + 1;
        },
 
        isPossiblySupportedSource: msAbstractParser.isPossiblySupportedSource,

        overrideUrlPolicy: msAbstractParser.overrideUrlPolicy,

        minIntevalBetweenQueryInfoDownloads: msAbstractParser.minIntevalBetweenQueryInfoDownloads
    };

    return new MsBatchVideoParser();
}());
