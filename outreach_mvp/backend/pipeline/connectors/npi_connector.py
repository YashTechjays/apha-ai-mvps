"""
NPI Registry API connector.
Public API: https://npiregistry.cms.hhs.gov/api/
Taxonomy codes for pharmacy:
  183500000X  Pharmacist
  1835G0000X  General Practice Pharmacist
  1835P1300X  Nuclear Pharmacist
  1835P0018X  Pharmacist Prescriber
"""
import httpx
import time
from typing import List, Optional
from utils.logger import get_logger
from utils.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

NPI_API_URL = "https://npiregistry.cms.hhs.gov/api/"

PHARMACY_TAXONOMY_CODES = [
    "183500000X",
    "1835G0000X",
    "1835P1300X",
    "1835P0018X",
]

PHARMACY_TECH_CODES = ["3336T0002X"]


def fetch_pharmacists_by_state(
    state: str,
    taxonomy_code: str = "183500000X",
    limit: int = 200,
    skip: int = 0,
) -> List[dict]:
    """
    Fetch pharmacists from NPI registry for a given state.
    Returns list of raw NPI result dicts.
    """
    params = {
        "version": "2.1",
        "taxonomy_description": "Pharmacist",
        "state": state,
        "limit": min(limit, 200),
        "skip": skip,
    }

    try:
        logger.info(f"Fetching NPI records: state={state}, skip={skip}")
        with httpx.Client(timeout=30) as client:
            response = client.get(NPI_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            logger.info(f"NPI: {len(results)} records returned for {state}")
            return results
    except Exception as e:
        logger.error(f"NPI API error for state {state}: {e}")
        return []


def parse_npi_record(record: dict) -> Optional[dict]:
    """
    Parse a raw NPI API result into a prospect-ready dict.
    Extracts: NPI, name, credential, address, taxonomy/specialty.
    """
    try:
        basic = record.get("basic", {})
        addresses = record.get("addresses", [])
        taxonomies = record.get("taxonomies", [])

        practice_addr = next(
            (a for a in addresses if a.get("address_purpose") == "LOCATION"),
            addresses[0] if addresses else {}
        )

        primary_tax = next(
            (t for t in taxonomies if t.get("primary")),
            taxonomies[0] if taxonomies else {}
        )

        first_name = basic.get("first_name", "").strip()
        last_name = basic.get("last_name", "").strip()

        if not first_name or not last_name:
            return None

        credential = basic.get("credential", "").strip()
        state = practice_addr.get("state", "").upper()
        city = practice_addr.get("city", "").title()
        zip_code = practice_addr.get("postal_code", "")[:5]
        taxonomy_desc = primary_tax.get("desc", "")

        practice_setting = _infer_practice_setting(taxonomy_desc, record)

        license_type = "pharmacist"
        if "Technician" in taxonomy_desc:
            license_type = "technician"

        return {
            "npi_number": record.get("number"),
            "first_name": first_name,
            "last_name": last_name,
            "credential": credential,
            "license_type": license_type,
            "specialty": taxonomy_desc,
            "practice_setting": practice_setting,
            "state": state,
            "city": city,
            "zip_code": zip_code,
            "source": "npi_registry",
            "email": None,
        }
    except Exception as e:
        logger.warning(f"Failed to parse NPI record: {e}")
        return None


def _infer_practice_setting(taxonomy_desc: str, record: dict) -> str:
    """Infer practice setting from taxonomy and org name."""
    desc_lower = taxonomy_desc.lower()
    org = " ".join([
        record.get("basic", {}).get("organization_name", ""),
        " ".join(a.get("address_1", "") for a in record.get("addresses", []))
    ]).lower()

    if "hospital" in desc_lower or "hospital" in org or "health system" in org:
        return "Hospital/Health-System"
    if "community" in desc_lower or "retail" in org:
        return "Community Pharmacy"
    if "ambulatory" in desc_lower or "clinic" in org:
        return "Ambulatory Care"
    if "long-term" in desc_lower or "ltc" in org or "nursing" in org:
        return "Long-Term Care"
    if "mail" in desc_lower or "specialty" in desc_lower:
        return "Specialty/Mail Order"
    return "General Pharmacy"


def fetch_all_states(
    states: List[str] = None,
    max_per_state: int = 1000,
) -> List[dict]:
    """
    Fetch pharmacist NPI records across all specified states.
    Respects NPI API rate limits with backoff.
    """
    states = states or [
        "CA", "TX", "FL", "NY", "IL", "PA", "OH", "GA", "NC", "MI",
        "NJ", "VA", "WA", "AZ", "MA", "TN", "IN", "MO", "MD", "WI",
        "CO", "MN", "SC", "AL", "LA", "KY", "OR", "OK", "CT", "UT",
    ]

    all_records = []
    for state in states:
        skip = 0
        state_count = 0
        while state_count < max_per_state:
            batch = fetch_pharmacists_by_state(state, skip=skip)
            if not batch:
                break
            all_records.extend(batch)
            state_count += len(batch)
            skip += len(batch)
            if len(batch) < 200:
                break
            time.sleep(0.5)

        logger.info(f"State {state}: {state_count} total records")
        time.sleep(1.0)

    logger.info(f"NPI fetch complete: {len(all_records)} total records")
    return all_records
