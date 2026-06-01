// Friendly citation label for an RFP: prefers the stored source_name, falls back
// to the source_url hostname (without "www."). Never throws on a bad URL.
export function sourceLabel(rfp) {
  if (!rfp) return null
  if (rfp.source_name) return rfp.source_name
  if (!rfp.source_url) return null
  try {
    return new URL(rfp.source_url).hostname.replace(/^www\./, '')
  } catch {
    return rfp.source_url
  }
}
