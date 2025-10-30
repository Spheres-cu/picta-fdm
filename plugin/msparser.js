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
                    let Updl_date = !msAbstractParser.isYoutubeSource(url) ? myObj.upload_date : undefined;
                    if (Updl_date) {
                        const converted = convertUploadDate(Updl_date);
                        myObj.upload_date = converted.iso8601;
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