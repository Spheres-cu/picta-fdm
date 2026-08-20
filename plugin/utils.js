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

function mapEntries(items) { 
  if (Array.isArray(items) && items.every(item => item.entries)) {
    let entries = [];
    items
    .filter(item => item.title && !/\bShorts\b/i.test(item.title))
    .map((item) => {
      entries = entries.concat(item.entries);
    });
    return entries;
  }
  return items;
}

function parseYTentries(entries) {
  if (Array.isArray(entries)) {
    let arrays = entries.filter(item => item.title && !/\[(?:Private|Deleted) video\]/i.test(item.title))
    return arrays;
  }
  return entries;
}

function detectOSFromUserAgent(userAgent) {
  const ua = new String(userAgent).toLowerCase();

  // Windows detection
  if (ua.includes('windows nt 10.0'))
    return 'Windows';

  // macOS detection
  if (ua.includes('macintosh') || ua.includes('mac os x'))
    return 'macOS';

  // Linux detection
  if (ua.includes('linux'))
    return 'Linux';

  // Default unknown
  return 'Unknown';
}

function isSupportedBrowser(browser) {
  const SupportedBrowsers = [/(?:brave|firefox|chrome|chromium|edge|opera|safari|vivaldi|whale)/i]
  return SupportedBrowsers.some(pattern => pattern.test(browser));
}

function Pythonlog(obj) {
  let errLog = String(obj.errorOutput)
  // let outputLog = String(obj.output)
  if (errLog.length)
    console.log("Python error log:", errLog);

  // if (outputLog.length)
  //   console.log("Python output log:", outputLog);
}

function parseErrorMessage(log, options = {}) {
  const {
    removePrefix = true,
    removeCausedBy = true,
    removeReportSection = true
  } = options;

  if (!log.startsWith('ERROR:')) {
    return String(log);
  }

  let message = String(log);

  // Remove the ERROR prefix with service and identifier
  if (removePrefix) {
    message = message.replace(/\bERROR:\s*\[[^\]]+\]\s*[^:]+:\s*/, '');
  }

  // Clean up
  if (removeCausedBy) {
    message = message.split(' (caused by')[0];
  }

  if (removeReportSection) {
    message = message.split('; please report')[0];
    message = message.split(' please report')[0];
  }

  message = message.trim();
  message = message.replace(/\s*\(caused by.*$/, '');
  message = message.replace(/\s*Failed to download MPD manifest:\s*/, '');
  message = message.replace(/\s*Failed to download m3u8 information:\s*/, '');
  message = message.replace(/\s*Unable to download JSON metadata:\s*/, '');
  message = message.replace(/\s*This video is available in\s*.*\./,'.');
  message = message.replace(/:\s*$/, '');

  return message;
}

function UrlSource(url){
  const SupportedSource = [
    /^https?:\/\/(?:www\.)?picta\.cu\/(?:medias|movie|documental|musical|short)\/(?<id>[\da-z-]+)(?:\?playlist=(?<playlist_id>[\da-z-]+))?/i,
    /^https?:\/\/(?:www\.)?picta\.cu\/search\/(?<query>[^?#&]+)?/i,
    /^https?:\/\/(?:www\.)?picta\.cu\/serie\/(?<query>[^?#&]+)?/i,
    /^https?:\/\/(?:www\.|m\.|music\.)?youtube\.com\/watch\?v=[\w-]+/i,
    /^https?:\/\/(?:www\.|m\.|music\.)?youtube\.com\/playlist\?list=[\w-]+/i,
    /^https?:\/\/(?:www\.|m\.|music\.)?youtube\.com\/channel\/[\w-]+/i,
    /^https?:\/\/(?:www\.|m\.|music\.)?youtu\.be\/[\w-]+/i,
    /^https?:\/\/(?:www\.|m\.|music\.)?youtube\.com\/(?:results|search)\?([^#]+&)?(?:search_query|q)=(?:[^&]+)(?:[&#]|$)/i,
    /^https?:\/\/music\.youtube\.com\/browse\/[\w-]+/i,
    /^https?:\/\/(?:www\.|m\.)?facebook\.com\/[^/]+\/videos\/[\dA-Za-z]+(?:\/)?$/i,
    /^https?:\/\/(?:www\.|m\.)?facebook\.com\/video\.php\?v=\d+(?:&.*)?$/i,
    /^https?:\/\/(?:www\.|m\.)?facebook\.com\/reel\/\d+(?:\/)?$/i,
    /^https?:\/\/(?:www\.|m\.)?facebook\.com\/watch\/live\/\?v=\d+(?:&.*)?$/i,
    /^https?:\/\/(?:www\.|m\.)?facebook\.com\/[^/]+\/posts\/[\dA-Za-z]+(?:\/)?$/i,
    /^https?:\/\/(?:www\.|m\.)?facebook\.com\/share\/[^/]+\/[\dA-Za-z]+(?:\/)?$/i,
    /^https?:\/\/(?:www\.|m\.)?facebook\.com\/story\.php\?story_fbid=[\dA-Za-z]+(?:&.*)?$/i,
    /^https?:\/\/(?:www\.|m\.)?facebook\.com\/permalink\.php\?story_fbid=[\dA-Za-z]+(?:&.*)?$/i,
    /^https?:\/\/(?:www\.|m\.)?facebook\.com\/groups\/[^/]+\/permalink\/\d+(?:\/)?$/i,
    /^https?:\/\/(?:www\.|m\.)?facebook\.com\/watch\/\?v=\d+(?:&.*)?$/i
  ];

  const YTpatterns = SupportedSource.slice(3, SupportedSource.length)
  const isSupportedSource = SupportedSource.some(pattern => pattern.test(url));
  const isYoutubeUrl = YTpatterns.some(patterns => patterns.test(url))

  return {
    isSupportedSource: isSupportedSource,
    isYoutubeUrl: isYoutubeUrl
  }
}

function PossiblySupportedSource(url){
  return /^https?:\/\/(?:www\.|m\.|music\.)?(youtube\.com|youtu\.be|facebook\.com).*$/i.test(url);
}
