function convertUploadDate(upload_date) {
  // Extract year, month, and day from the string
  const upld_date = new String (upload_date)
  const year = upld_date.substring(0, 4);
  const month = upld_date.substring(4, 6);
  const day = upld_date.substring(6, 8);

  // Create a Date object (note: months are 0-indexed in JavaScript)
  const date = new Date(`${year}-${month}-${day}T00:00:00Z`);

  // Convert to ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
  const iso8601 = date.toISOString();

  // Convert to RFC 2822 format (EEE, dd MMM yyyy HH:mm:ss GMT)
  const rfc2822 = date.toUTCString();

  return {
    iso8601: iso8601,
    rfc2822: rfc2822,
    dateObject: date  // optional: return the Date object as well
  };
}

// function msToEpochSeconds(ms) {
//   return Math.floor(ms / 1000);
// }

function Pythonlogs(obj)
{
  if (obj.output)
    console.log("Python result: ", obj.output);
    
  if (obj.errorOutput)
    console.log("Python Errors: ", obj.errorOutput);
}

function downloadUrlAsUtf8Text(url, cookies, headers, postData) {
    cookies = cookies || '';
    headers = headers || [];

    return new Promise(function(resolve, reject) {
        // console.log("[downloadUrlAsUtf8Text]: Downloading", url);

        var download = qtJsDownloadsFactory.create();

        download.url = url;
        download.cookies = cookies;
        if (typeof(postData) === "string")
            download.postDataAsUtf8String = postData;
        else if (postData instanceof ArrayBuffer)
            download.postData = postData;

        for (var i in headers) {
          if (headers.hasOwnProperty(i)) {
            download.setCustomHeader(i, headers[i]);
          }
        }
        
        download.finished.connect(function() {
            // console.log("[downloadUrlAsUtf8Text]: Finished downloading", url);
            var error = download.error;

            if (error) {
                reject({
                    error: error,
                    isParseError: !download.isNetworkError && !download.isInternalError
                });
            } else {
                resolve({
                    url: url,
                    body: download.dataAsUtf8Text(),
                    cookies: download.cookies,
                    error:error
                });
            }
        });

        download.start();
    });
}