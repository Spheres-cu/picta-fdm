var msAbstractParser = (function() {
    function MsAbstractParser() {}

    MsAbstractParser.prototype = {

        parse: function(obj, customArgs) {
            console.log("parsing...");

            let args = [];
            let systemUserAgent = new String(qtJsSystem.defaultUserAgent);
            let AllowWbCookies = new Boolean(App.pluginsAllowWbCookies);
            let WebBrowser = new String(qtJsSystem.defaultWebBrowser);
            let isYoutubeUrl = msAbstractParser.isYoutubeSource(obj.url);

            let proxyUrl = qtJsNetworkProxyMgr.proxyForUrl(obj.url).url();
            if (proxyUrl) {
                proxyUrl = proxyUrl.replace(/^https:\/\//i, 'http://'); // FDM bug workaround
                args.push("--proxy", proxyUrl);
            }

            args.push("-J", "--verbose");

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

                    if (!output || output[0] !== '{') {
                        try {
                            var isUnsupportedUrl = /ERROR:\s*\[generic\]\s*Unsupported URL:/.test(obj.errorOutput);
                            let NotFound = /ERROR:\s*\[picta\]\s*.*: (?:Cannot find video!|HTTP Error 404: Not Found)/i.test(obj.errorOutput);
                            let Forbidden = /ERROR:\s*\[picta\]\s*.*: HTTP Error 403: Forbidden/.test(obj.errorOutput);
                            let TimeoutError = /ERROR:\s*\[picta\]\s*.*: (?:HTTP Error 408|Read timed out)/i.test(obj.errorOutput);
                            let BadCredentials = /ERROR:\s*\[picta\]\s*.*: HTTP Error (?:400|401)|This video is only available for registered users/i.test(obj.errorOutput);
                            let PaidVideo = /ERROR:\s*\[picta\]\s*.*: This video is paid only/i.test(obj.errorOutput);
                            let YTNotFound = /ERROR:\s*\[youtube\]\s*\w+:\s*Video unavailable/i.test(obj.errorOutput);

                            if (TimeoutError || BadCredentials) {
                                let errorMsg = TimeoutError ? "Read timed out" : "Crendenciales no validas, revise usuario y contraseña o netrc (picta)"
                                reject({
                                    error: errorMsg,
                                    isParseError: false
                                })
                                return;
                            }

                            if (YTNotFound) {
                                let errorMsg = "This video has been removed by the uploader";
                                console.log("Error:", errorMsg);
                                reject({
                                    error: errorMsg,
                                    isParseError: false                                            
                                })
                                return;
                            }

                            if (!isPlaylist && !isYoutubeUrl) {
                                if (NotFound || Forbidden || PaidVideo) {
                                    let errorMsg = new String
                                    if (PaidVideo) {
                                        errorMsg = "Este vídeo es sólo por pago"
                                    } else {
                                        errorMsg = NotFound ? "Error HTTP 404: No encontrado" : "Error HTTP 403: Prohibido"
                                    }
                                    console.log("Error:", errorMsg);
                                    reject({
                                        error: errorMsg,
                                        isParseError: false
                                    })
                                    return;
                                }
                            }
                        } catch (e) {
                            let ErrorMessage = "Parse error: " + e.message;
                            reject({
                                error: isUnsupportedUrl ? "Unsupported URL" : ErrorMessage,
                                isParseError: !isUnsupportedUrl
                            });
                        }
                    }

                    resolve(JSON.parse(output));
                });
            });
        },

        isSupportedSource: function(url) {
            const SupportedSource = [
                /^https?:\/\/(?:www\.)?picta\.cu\/(?:medias|movie|embed)\/(?:\?v=)?(?<id>[\da-z-]+)(?:\?playlist=(?<playlist_id>[\da-z-]+))?/i,
                /^https?:\/\/(?:www\.)?youtube\.com\/watch\?v=[\w-]+/i,
                /^https?:\/\/(?:www\.)?youtube\.com\/playlist\?list=[\w-]+/i,
                /^https?:\/\/(?:www\.)?youtube\.com\/channel\/[\w-]+/i,
                /^https?:\/\/(?:www\.)?youtu\.be\/[\w-]+/i,
                /^https?:\/\/(?:www\.)?facebook\.com\/[^/]+\/videos\/\d+/i,
            ];
            return SupportedSource.some(pattern => pattern.test(url));
        },

        isYoutubeSource: function(url) {
            const SupportedSource = [
                /^https?:\/\/(?:www\.)?youtube\.com\/watch\?v=[\w-]+/i,
                /^https?:\/\/(?:www\.)?youtube\.com\/playlist\?list=[\w-]+/i,
                /^https?:\/\/(?:www\.)?youtube\.com\/channel\/[\w-]+/i,
                /^https?:\/\/(?:www\.)?youtu\.be\/[\w-]+/i,
                /^https?:\/\/(?:www\.)?facebook\.com\/[^/]+\/videos\/\d+/i
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
            return 500;
        },
    };

    return new MsAbstractParser();
}());