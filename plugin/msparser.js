var msParser = (function() {
    function MsParser() {}

    MsParser.prototype = {

        parse: function(obj) {
            let customArg = [];
            if (msAbstractParser.isYoutubeSource(obj.url)) {
                customArg.push(
                    "--no-playlist", "--sub-format", "srt/vtt/best",
                    "--extractor-args", "youtube:skip=auto-gened_subs,translated_subs"
                );
            } else {
                customArg.push("--no-playlist");
            }
            return msAbstractParser.parse(obj, customArg)
            .then(this.parsecontent);
        },

        parsecontent: function(obj) {
            return new Promise(function(resolve, reject) {
                var myObj = obj;
                var url = myObj.webpage_url || undefined;

                try {
                    if (myObj.upload_date) {
                        const converted = convertUploadDate(myObj.upload_date);
                        myObj.upload_date = converted.iso8601;
                    }

                    if (!msAbstractParser.isYoutubeSource(url)) {
                        const categories = [/(?:Película|Documental|Video)/i]
                        if (myObj.category && categories.some(pattern => pattern.test(myObj.category)) && myObj.release_year) {
                            let year = String(myObj.release_year);
                            let title = String(myObj.title);
                            myObj.title = !title.includes(year) ? String(title + " (" + year +")") : title;
                        } else if (myObj.category === "Serie" && myObj.series && myObj.season_number && myObj.episode_number) {
                            let series = String(myObj.series);
                            let season_number = String(myObj.season_number);
                            let episode_number = String(myObj.episode_number);
                            let title = `${series} S${season_number.padStart(2, '0')}E${episode_number.padStart(2, '0')}`;
                            myObj.title = title ? title : myObj.title;
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