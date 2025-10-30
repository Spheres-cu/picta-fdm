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
  if (Array.isArray(items) && items.every(item => item.hasOwnProperty("entries"))) {
    let entries = [];
    items
    .filter(item => item?.hasOwnProperty("title") && !/\bShorts\b/i.test(item.title))
    .map((item) => {
      entries = entries.concat(item.entries);
    });
    return entries;
  }
  return items;
}

function parseYTentries(entries) {
  if (Array.isArray(entries)) {
    let arrays = entries.filter(item => item.hasOwnProperty("title") && !/\[(?:Private|Deleted) video\]/i.test(item.title))
    return arrays;
  }
  return entries;
}

function Pythonlogs(obj)
{
  if (obj.output)
    console.log("Python result: ", obj.output);
    
  if (obj.errorOutput)
    console.log("Python Errors: ", obj.errorOutput);
}
