var msAbstractParser = (function() {
    function MsAbstractParser() {}

    MsAbstractParser.prototype = {

        parse: function(obj, customArgs) {
            console.log("parsing...");

            let args = [];
            let systemUserAgent = String(qtJsSystem.defaultUserAgent);
            let AllowWbCookies = Boolean(App.pluginsAllowWbCookies);
            let WebBrowser = String(qtJsSystem.defaultWebBrowser);
            let isYoutubeUrl = UrlSource(obj.url).isYoutubeUrl || msAbstractParser.isPossiblySupportedSource(obj);
            let proxyUrl = qtJsNetworkProxyMgr.proxyForUrl(obj.url).url();

            if (proxyUrl) {
                proxyUrl = proxyUrl.replace(/^https:\/\//i, 'http://'); // FDM bug workaround
                args.push("--proxy", proxyUrl);
            }

            args.push("-J", "--no-warnings");

            if (isYoutubeUrl)
                args.push("--ignore-config");

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

                    if (obj.exitCode !== 0) {
                        try {
                            var PluginError = /\bERROR:\s*(\[(?:picta(?::channel:playlist|:user:playlist)?|youtube|facebook)\])?/i.test(obj.errorOutput);
                            console.log("Plugin Error:", PluginError);
                            if (PluginError){
                                let ErrorMessage = isPlaylist ? parseErrorMessage(obj.errorOutput, {removePrefix: false}) : parseErrorMessage(obj.errorOutput);
                                reject({
                                    error: ErrorMessage,
                                    isParseError: false
                                });
                            }
                        } catch (e) {
                            let ErrorMessage = "Parse error: " + e.error;
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
            return UrlSource(url).isSupportedSource
        },

        supportedSourceCheckPriority: function() {
            return 65534;
        },

        isPossiblySupportedSource: function(obj) {
            return PossiblySupportedSource(obj.url);
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
