"""Source citation helpers — resolve a human-readable "where did this RFP come
from" label + link for every RFP.

Provenance already flows through the system as ``source_url`` (the page an RFP was
crawled from). This module turns that into a friendly, attestable citation:

- ``friendly_source_name`` maps a URL's hostname to a readable site name.
- ``ORG_SOURCE_MAP`` gives credible, source-specific citations to the seeded demo
  organizations that lack an ``organization.website`` (the AI-feature seed orgs).
- ``resolve_source`` picks the best ``(source_url, source_name)`` for an RFP dict,
  preferring an explicit source, then the org map, then the org website.
"""
from typing import Optional
from urllib.parse import urlparse


# Hostname (sans leading "www.") -> friendly site name. Covers the live crawl
# targets in ``backend/crawler/targets.py`` plus common seed domains, so crawled
# RFPs get a readable citation without per-RFP configuration.
SOURCE_SITE_NAMES: dict[str, str] = {
    "tn.gov": "Tennessee TennCare",
    "medicaid.ncdhhs.gov": "NC Medicaid",
    "hca.wa.gov": "Washington State HCA",
    "health.ny.gov": "New York State DOH",
    "msdh.ms.gov": "Mississippi State DOH",
    "medicaid.ms.gov": "Mississippi Medicaid",
    "dch.georgia.gov": "Georgia DCH",
    "dph.georgia.gov": "Georgia Dept. of Public Health",
    "pharmacist.com": "APhA (pharmacist.com)",
    "dhcs.ca.gov": "California DHCS",
    "va.gov": "U.S. Dept. of Veterans Affairs",
    "hhs.texas.gov": "Texas HHS",
    "mdanderson.org": "MD Anderson Cancer Center",
    "humana.com": "Humana Inc.",
    "uofmhealth.org": "University of Michigan Health",
}


# Seed organizations that have no ``organization.website`` (the AI-feature demo
# orgs) — give each a credible, source-specific citation. Real orgs point at
# their own site; the fictional forecast orgs point at the authoritative
# governing body so the citation link still resolves.
ORG_SOURCE_MAP: dict[str, tuple[str, str]] = {
    # Real organizations also used by the open demo RFPs.
    "MD Anderson Cancer Center": ("https://www.mdanderson.org", "MD Anderson Cancer Center"),
    "Humana Inc.": ("https://www.humana.com", "Humana Inc."),
    "University of Michigan Health System": ("https://www.uofmhealth.org", "University of Michigan Health"),
    "Georgia Department of Public Health": ("https://dph.georgia.gov", "Georgia Dept. of Public Health"),
    # Forecast-history orgs (fictional) -> authoritative governing body.
    "Lone Star Oncology Pharmacy Network": ("https://www.hhs.texas.gov", "Texas HHS (Pharmacy)"),
    "Pacific Medicaid Pharmacy Board": ("https://www.dhcs.ca.gov", "California DHCS (Medicaid Pharmacy)"),
    "Federal Veterans Pharmacy Services": ("https://www.va.gov", "U.S. Dept. of Veterans Affairs"),
    "Southeast Public Health Pharmacy Consortium": ("https://dph.georgia.gov", "Southeast Public Health (GA DPH)"),
}

# A generic seed placeholder that should never be shown as a real citation.
_GENERIC_SOURCE = "pharmacist.com/rfp"


def friendly_source_name(url: Optional[str]) -> str:
    """Readable site name for a URL. Falls back to the bare hostname, then "".

    Never raises on empty or malformed input.
    """
    if not url:
        return ""
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return ""
    if not host:
        return ""
    host = host[4:] if host.startswith("www.") else host
    if host in SOURCE_SITE_NAMES:
        return SOURCE_SITE_NAMES[host]
    # Match registrable suffixes (e.g. a subdomain of a known host).
    for known, name in SOURCE_SITE_NAMES.items():
        if host == known or host.endswith("." + known):
            return name
    return host


def resolve_source(rfp_data: dict) -> dict:
    """Best ``{source_url, source_name}`` citation for an RFP dict.

    Priority: explicit non-generic source already on the dict -> per-org map ->
    organization website -> existing source_url -> empty.
    """
    org = rfp_data.get("organization") or {}
    org_name = org.get("name")
    existing_url = rfp_data.get("source_url") or ""
    existing_name = rfp_data.get("source_name") or ""

    if existing_name and existing_url and _GENERIC_SOURCE not in existing_url:
        return {"source_url": existing_url, "source_name": existing_name}

    if org_name and org_name in ORG_SOURCE_MAP:
        url, label = ORG_SOURCE_MAP[org_name]
        return {"source_url": url, "source_name": label}

    website = org.get("website")
    if website:
        return {"source_url": website, "source_name": org_name or friendly_source_name(website)}

    if existing_url:
        return {"source_url": existing_url, "source_name": existing_name or friendly_source_name(existing_url)}

    return {"source_url": "", "source_name": existing_name or org_name or ""}
