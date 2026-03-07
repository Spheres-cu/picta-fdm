var msParser = (function() {
    function MsParser() {}

    MsParser.prototype = {

        parse: function(obj) {
            return msAbstractParser.parse(obj, ["--no-playlist"])
            .then(this.parsecontent);
        },

        parsecontent: function(obj) {
            return new Promise(function(resolve, reject) {
                var myObj = obj;
                var url = myObj.webpage_url || undefined;

                try {
                    if (myObj.hasOwnProperty("upload_date") && myObj.upload_date) {
                        const converted = convertUploadDate(myObj.upload_date);
                        myObj.upload_date = converted.iso8601;
                    }

                    if (!msAbstractParser.isYoutubeSource(url) && myObj.hasOwnProperty("release_year") && myObj.release_year) {
                        if (myObj.hasOwnProperty("category") && myObj.category[0] === "Película") {
                            let year = String(myObj.release_year);
                            let title = String(myObj.title);
                            myObj.title = !title.includes(year) ? String(title + " (" + year +")") : title;
                        }
                    }
                    resolve(myObj);
                } catch (e) {
                    reject({
                        error: e.message,
                        isParseError: true
                    });
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