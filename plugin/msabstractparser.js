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
            let tmpCookies;
            let systemUserAgent;
            //let systemBrowser;
            
            try
            {
                systemUserAgent = qtJsSystem.defaultUserAgent;
                // systemBrowser = qtJsSystem.defaultWebBrowser;
            }
            catch(e) {}

            let proxyUrl = qtJsNetworkProxyMgr.proxyForUrl(obj.url).url();
            if (proxyUrl)
            {
                proxyUrl = proxyUrl.replace(/^https:\/\//i, 'http://'); // FDM bug workaround
                args.push("--proxy", proxyUrl);
            }

            args.push("-J", "--flat-playlist", "--no-warnings");
            
            if (obj.cookies && obj.cookies.length)
            {
                tmpCookies = qtJsTools.createTmpFile("request_" + obj.requestId + "_cookies");
                if (tmpCookies && tmpCookies.writeText(cookiesToNetscapeText(obj.cookies)))
                    args.push("--cookies", tmpCookies.path);
            }

            let userAgent = obj.userAgent || systemUserAgent;
            if (userAgent)
                args.push('--user-agent', userAgent);

            if (customArgs.length)
                args = args.concat(customArgs);

            args.push(obj.url);

            return launchPythonScript(obj.requestId, obj.interactive, "picta-dl/picta_dl/__main__.py", args)
            .then(function(obj)
            {
                console.log("Python result: ", obj.output);

                return new Promise(function (resolve, reject)
                {
                    var output = obj.output.trim();
                    if (!output || output[0] !== '{')
                    {   try 
                        {
                            var isUnsupportedUrl = /ERROR:\s*\[generic\]\s*Unsupported URL:/.test(output);
                        }
                        catch(e){}
                        reject({
                                error: isUnsupportedUrl ? "Unsupported URL" : "Parse error:" + e.message,
                                isParseError: !isUnsupportedUrl
                            });
                    }
                    else
                    {
                        var myObj = JSON.parse(output);

                        var sub_url = myObj.subtitle_url;
                        if (sub_url) {
                            let Subtitles = {
                                "name": "Spanish",
                                "url": sub_url,
                                "ext": "srt"
                            };
                            myObj.subtitles = {"es": [Subtitles]};
                            // console.log("Subtitles: ", Object.values(myObj.subtitles.es[0]))
                        }

                        var thumb_url = myObj.thumbnail;
                        if (thumb_url) {
                            let Thumbnails = [
                                {"url": myObj.thumbnail + "_100x150",
                                "height": "150",
                                "width": "100"
                                }
                            ]
                            myObj.thumbnails = Thumbnails;
                            // console.log("Thumbnails: ", Object.values(myObj.thumbnails[0]))
                        }
                        
                        resolve(myObj);
                    }
                });
            });
        },

        isSupportedSource: function(url)
        {
            return false;
        },

        supportedSourceCheckPriority: function()
        {
            return 1010;
        },

        isPossiblySupportedSource: function(obj)
        {
			if (!obj.url.includes('picta.cu'))
				return false;
            if (obj.contentType && !/^text\/html(;.*)?$/.test(obj.contentType))
                return false;
            if (obj.resourceSize !== -1 &&
                    (obj.resourceSize === 0 || obj.resourceSize > 3*1024*1024))
            {
                return false;
            }
            return /^https?:\/\//.test(obj.url);
        },

        overrideUrlPolicy: function(url)
        {
            return true;
        },
    };

    return new MsAbstractParser();
}());
