"""
Full NPI import pipeline:
  1. Fetch from NPI API (or use mock data for MVP)
  2. Parse records
  3. Cross-reference against existing APhA members (exclude)
  4. Check suppression list (exclude)
  5. Upsert to prospects table
"""
from sqlalchemy.orm import Session
from db.models.prospect import Prospect
from db.models.suppression import Suppression
from pipeline.connectors.npi_connector import fetch_all_states, parse_npi_record
from utils.logger import get_logger
from utils.seed_data import generate_mock_prospects

logger = get_logger(__name__)


def run_npi_import(db: Session, use_mock: bool = True, max_per_state: int = 100) -> dict:
    """
    Main NPI import function.
    use_mock=True for development (uses generated data, no API calls).
    """
    if use_mock:
        logger.info("Using mock prospect data (development mode)")
        raw_prospects = generate_mock_prospects(500)
        parsed = raw_prospects
    else:
        logger.info("Fetching from NPI Registry API...")
        raw_records = fetch_all_states(max_per_state=max_per_state)
        parsed = [p for r in raw_records if (p := parse_npi_record(r)) is not None]
        logger.info(f"Parsed {len(parsed)} valid records from {len(raw_records)} NPI records")

    # Load suppression list
    suppressed_emails = {
        s.email.lower() for s in db.query(Suppression).all()
    }

    # Load existing prospects (by NPI or email)
    existing_npis = {
        p.npi_number for p in db.query(Prospect.npi_number).all()
        if p.npi_number
    }

    imported = updated = skipped = 0

    for prospect_data in parsed:
        email = (prospect_data.get("email") or "").lower()
        if email and email in suppressed_emails:
            skipped += 1
            continue

        npi = prospect_data.get("npi_number")
        if npi and npi in existing_npis:
            existing = db.query(Prospect).filter(Prospect.npi_number == npi).first()
            if existing:
                existing.specialty = prospect_data.get("specialty") or existing.specialty
                existing.practice_setting = prospect_data.get("practice_setting") or existing.practice_setting
                updated += 1
            continue

        prospect = Prospect(**{
            k: v for k, v in prospect_data.items()
            if hasattr(Prospect, k)
        })
        db.add(prospect)
        if npi:
            existing_npis.add(npi)
        imported += 1

    db.commit()
    result = {"imported": imported, "updated": updated, "skipped": skipped}
    logger.info(f"NPI import complete: {result}")
    return result


def crossref_with_member_list(db: Session, member_emails: list) -> int:
    """
    Mark prospects who are already APhA members as excluded.
    """
    excluded = 0
    member_email_set = {e.lower() for e in member_emails}
    prospects = db.query(Prospect).filter(
        Prospect.status.notin_(["excluded", "unsubscribed", "bounced"])
    ).all()

    for p in prospects:
        if (p.email or "").lower() in member_email_set:
            p.status = "excluded"
            p.do_not_contact = True
            excluded += 1

    db.commit()
    logger.info(f"Cross-reference complete: {excluded} prospects excluded (already APhA members)")
    return excluded
