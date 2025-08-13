var msParser = (function()
{
    function MsParser()
    {
    }

    MsParser.prototype = {

        parse: function (obj)
        {
            return msAbstractParser.parse(obj, ["--no-playlist"])
            .then(this.parsecontent);
        },

        parsecontent: function (obj)
        {
            return new Promise(function(resolve, reject)
            {
                var myObj = obj;

                try
                {
                    let sub_url = myObj.subtitle_url;

                    if (sub_url)
                    {
                        let Subtitles = {
                            "name": "Spanish",
                            "url": sub_url,
                            "ext": "srt"
                        };
                        myObj.subtitles = {"es": [Subtitles]};
                    }

                    let thumb_url = myObj.thumbnail;
                    if (thumb_url)
                    {
                        let height = Math.round(myObj.height / 4);
                        let width = Math.round(myObj.width / 4);

                        let Thumbnails = [
                        {
                            "url": thumb_url + "_" + width + "x" + height,
                            "height": height,
                            "width": width
                        }
                        ];

                        myObj.thumbnails = Thumbnails;
                    }

                    let Updl_date = myObj.upload_date
                    if (Updl_date) 
                    {
                        const converted = convertUploadDate(Updl_date);
                        myObj.upload_date = converted.iso8601;
                    }
                    resolve(myObj);
                }
                catch (e)
                {
                    reject({error: e.message, isParseError: true});
                }
            });
        },

        isSupportedSource: msAbstractParser.isSupportedSource,

        supportedSourceCheckPriority: msAbstractParser.supportedSourceCheckPriority,

        isPossiblySupportedSource: msAbstractParser.isPossiblySupportedSource,

        overrideUrlPolicy: msAbstractParser.overrideUrlPolicy,

        minIntevalBetweenQueryInfoDownloads: msAbstractParser.minIntevalBetweenQueryInfoDownloads
    };

    return new MsParser();
}());
