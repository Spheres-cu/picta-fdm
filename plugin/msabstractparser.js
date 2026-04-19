var msAbstractParser = (function() {
    function MsAbstractParser() {}

    MsAbstractParser.prototype = {

        parse: function(obj, customArgs) {
            console.log("parsing...");

            let args = [];
            let systemUserAgent = String(qtJsSystem.defaultUserAgent);
            let AllowWbCookies = Boolean(App.pluginsAllowWbCookies);
            let WebBrowser = String(qtJsSystem.defaultWebBrowser);
            let isYoutubeUrl = msAbstractParser.isYoutubeSource(obj.url);
            let proxyUrl = qtJsNetworkProxyMgr.proxyForUrl(obj.url).url();

            if (proxyUrl) {
                proxyUrl = proxyUrl.replace(/^https:\/\//i, 'http://'); // FDM bug workaround
                args.push("--proxy", proxyUrl);
            }

            args.push("-J", "--no-warnings");

            if (isYoutubeUrl) {
                 args.push("--ignore-config");
            }

            let userAgent = obj.userAgent || systemUserAgent;

            if (AllowWbCookies && isYoutubeUrl) {
                let osType = detectOSFromUserAgent(userAgent);
                if (osType !== "Unknown" && isSupportedBrowser(WebBrowser))
                    if (osType === "Linux" || WebBrowser.toLowerCase() === "firefox")
                        args.push('--cookies-from-browser', WebBrowser);
            }

            if (customArgs.length) {
                args = args.concat(customArgs);
            }

            args.push(obj.url);

            return launchPythonScript(obj.requestId, obj.interactive, "picta-dl/picta_dl/__main__.py", args)
            .then(function(obj) {
                Pythonlog(obj);

                return new Promise(function(resolve, reject) {
                    let output = obj.output.trim();
                    let isPlaylist = /\"_type\"\:\s*\"playlist\"/.test(output);

                    if (obj.errorOutput || output[0] !== '{') {
                        try {
                            var PluginError = /^ERROR:\s*(\[(?:picta(?::channel:playlist|:user:playlist)?|youtube|facebook)\])?/i.test(obj.errorOutput);
                            console.log("Plugin Error:", PluginError);
                            if (PluginError){
                                let ErrorMessage = isPlaylist ? parseErrorMessage(obj.errorOutput, {removePrefix: false}) : parseErrorMessage(obj.errorOutput);
                                reject({
                                    error: ErrorMessage,
                                    isParseError: false
                                });
                            }
                        } catch (e) {
                            let ErrorMessage = "Parse error: " + e.message;
                            reject({
                                error: ErrorMessage,
                                isParseError: !PluginError
                            });
                        }
                    }
                    resolve(JSON.parse(output));
                });
            });
        },

        isSupportedSource: function(url) {
            const SupportedSource = [
                /^https?:\/\/(?:www\.)?picta\.cu\/(?:medias|movie|documental|musical)\/(?<id>[\da-z-]+)(?:\?playlist=(?<playlist_id>[\da-z-]+))?/i,
                /https?:\/\/(?:www\.)?picta\.cu\/search\/(?<query>[^?#&]+)?/i,
                /^https?:\/\/(?:www\.)?youtube\.com\/watch\?v=[\w-]+/i,
                /^https?:\/\/(?:www\.)?youtube\.com\/playlist\?list=[\w-]+/i,
                /^https?:\/\/(?:www\.)?youtube\.com\/channel\/[\w-]+/i,
                /^https?:\/\/(?:www\.)?youtube\.com\/(?:results|search)\?([^#]+&)?(?:search_query|q)=(?:[^&]+)(?:[&#]|$)/i,
                /^https?:\/\/music\.youtube\.com\/search\?([^#]+&)?(?:search_query|q)=(?:[^&]+)(?:[&#]|$)/i,
                /^https?:\/\/(?:www\.)?youtu\.be\/[\w-]+/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/[^/]+\/videos\/[\dA-Za-z]+(?:\/)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/video\.php\?v=\d+(?:&.*)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/reel\/\d+(?:\/)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/watch\/live\/\?v=\d+(?:&.*)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/[^/]+\/posts\/[\dA-Za-z]+(?:\/)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/share\/[^/]+\/[\dA-Za-z]+(?:\/)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/story\.php\?story_fbid=[\dA-Za-z]+(?:&.*)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/permalink\.php\?story_fbid=[\dA-Za-z]+(?:&.*)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/groups\/[^/]+\/permalink\/\d+(?:\/)?$/i,
            ];
            return SupportedSource.some(pattern => pattern.test(url));
        },

        isYoutubeSource: function(url) {
            const SupportedSource = [
                /^https?:\/\/(?:www\.)?youtube\.com\/watch\?v=[\w-]+/i,
                /^https?:\/\/(?:www\.)?youtube\.com\/playlist\?list=[\w-]+/i,
                /^https?:\/\/(?:www\.)?youtube\.com\/channel\/[\w-]+/i,
                /^https?:\/\/(?:www\.)?youtube\.com\/(?:results|search)\?([^#]+&)?(?:search_query|q)=(?:[^&]+)(?:[&#]|$)/i,
                /^https?:\/\/music\.youtube\.com\/search\?([^#]+&)?(?:search_query|q)=(?:[^&]+)(?:[&#]|$)/i,
                /^https?:\/\/(?:www\.)?youtu\.be\/[\w-]+/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/[^/]+\/videos\/[\dA-Za-z]+(?:\/)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/video\.php\?v=\d+(?:&.*)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/reel\/\d+(?:\/)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/watch\/live\/\?v=\d+(?:&.*)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/[^/]+\/posts\/[\dA-Za-z]+(?:\/)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/share\/[^/]+\/[\dA-Za-z]+(?:\/)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/story\.php\?story_fbid=[\dA-Za-z]+(?:&.*)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/permalink\.php\?story_fbid=[\dA-Za-z]+(?:&.*)?$/i,
                /^https?:\/\/(?:www\.|m\.)?facebook\.com\/groups\/[^/]+\/permalink\/\d+(?:\/)?$/i,
            ];
            return SupportedSource.some(pattern => pattern.test(url));
        },

        supportedSourceCheckPriority: function() {
            return 65534;
        },

        isPossiblySupportedSource: function(obj) {
            return false;
        },

        overrideUrlPolicy: function(url) {
            return true;
        },

        minIntevalBetweenQueryInfoDownloads: function() {
            return 300;
        },
    };

    return new MsAbstractParser();
}());