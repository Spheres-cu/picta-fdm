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
                        let height = myObj.height;
                        let width = myObj.width;
                        height = Math.round(height / 4);
                        width = Math.round(width / 4);

                        let Thumbnails = [
                        {
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

                        myObj.thumbnails = Thumbnails;
                    }

                    let Updl_date = myObj.upload_date
                    if (Updl_date) 
                    {
                        const converted = convertUploadDate(Updl_date);
                        myObj.upload_date = converted.iso8601;
                    }

                    // console.log("Media results: ", JSON.stringify(myObj, null));
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
