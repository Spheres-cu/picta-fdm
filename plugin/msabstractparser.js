var msAbstractParser = (function()
{
    function MsAbstractParser()
    {
    }

    MsAbstractParser.prototype = {

        parse: function (obj, customArgs)
        {
            console.log("parsing...");

            let args = [];
            let systemUserAgent;
            
            try
            {
                systemUserAgent = qtJsSystem.defaultUserAgent;
            }
            catch (e) {}

            let proxyUrl = qtJsNetworkProxyMgr.proxyForUrl(obj.url).url();
            if (proxyUrl)
            {
                proxyUrl = proxyUrl.replace(/^https:\/\//i, 'http://'); // FDM bug workaround
                args.push("--proxy", proxyUrl);
            }

            args.push("-J", "--no-warnings");

            let userAgent = obj.userAgent || systemUserAgent;
            if (userAgent)
                args.push('--user-agent', userAgent);

            if (customArgs.length)
                args = args.concat(customArgs);

            args.push(obj.url);

            return launchPythonScript(obj.requestId, obj.interactive, "picta-dl/picta_dl/__main__.py", args)
            .then(function(obj)
            {
                Pythonlogs(obj);

                return new Promise(function (resolve, reject)
                {
                    let output = obj.output.trim();
                    let isUnsupportedFormat = /http_dash_segments\+http_dash_segments/.test(output);
                    let isPlaylist = /\"_type\"\:\s*\"playlist\"/.test(output);

                    try
                    {
                        if (!output || output[0] !== '{')
                        {
                            var isUnsupportedUrl = /ERROR:\s*\[generic\]\s*Unsupported URL:/.test(output);
                        }

                        if (isUnsupportedFormat && !isPlaylist)
                        {
                            console.log("Is Unsupported Format: ", isUnsupportedFormat);
                            reject({error: "Unsupported Format", isParseError: false})
                        }
                    }   
                    catch(e)
                    {
                        let ErrorMessage = "Parse error:" + e.message;
                        reject({
                            error: isUnsupportedUrl ? "Unsupported URL" : ErrorMessage,
                            isParseError: !isUnsupportedUrl
                        });
                    }
                    resolve(JSON.parse(output));
                });
            });
        },

        isSupportedSource: function(url)
        {
            return /^https?:\/\/(?:www\.)?picta\.cu\/(?:medias|movie|embed)\/(?:\?v=)?(?<id>[\da-z-]+)(?:\?playlist=(?<playlist_id>[\da-z-]+))?/i.test(url);
        },

        supportedSourceCheckPriority: function()
        {
            return 65534;
        },

        isPossiblySupportedSource: function(obj)
        {
            return false;
        },

        overrideUrlPolicy: function(url)
        {
            return true;
        },

        minIntevalBetweenQueryInfoDownloads: function()
        {
            return 500;
        },
    };

    return new MsAbstractParser();
}());
