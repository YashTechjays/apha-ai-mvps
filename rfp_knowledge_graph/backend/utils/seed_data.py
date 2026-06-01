import uuid
from backend.graph.queries import create_rfp_with_relations, get_graph_stats
from backend.utils.logger import get_logger
from backend.utils.sources import resolve_source

logger = get_logger("seed_data")

MOCK_RFPS = [
    {
        "id": str(uuid.uuid4()),
        "title": "Pharmacy Benefits Management Services for State Medicaid Program",
        "description": "The Department of Health seeks proposals from qualified pharmacy benefit managers to administer the state Medicaid prescription drug program. Services include claims processing, formulary management, drug utilization review, and rebate administration.",
        "deadline": "2026-07-15",
        "posted_date": "2026-05-01",
        "url": "https://www.pharmacist.com/rfp/pbm-medicaid-2026",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$5M - $10M annually",
        "contact_name": "Sarah Mitchell",
        "contact_email": "sarah.mitchell@health.state.gov",
        "status": "open",
        "organization": {"name": "California Department of Health Care Services", "type": "government", "website": "https://www.dhcs.ca.gov"},
        "location": {"name": "Sacramento, CA", "state": "California", "city": "Sacramento"},
        "categories": ["pharmacy-services", "medicaid", "pbm"],
        "requirements": ["Active pharmacy license in California", "5+ years PBM experience", "URAC accreditation", "HIPAA compliance certification"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Clinical Pharmacy Consulting for Veterans Affairs Medical Center",
        "description": "VA Medical Center is seeking licensed clinical pharmacists to provide medication therapy management, anticoagulation clinic services, and formulary consultation for veteran patients.",
        "deadline": "2026-08-01",
        "posted_date": "2026-05-10",
        "url": "https://www.pharmacist.com/rfp/va-clinical-pharmacy",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$500K - $1M",
        "contact_name": "Dr. James Chen",
        "contact_email": "james.chen@va.gov",
        "status": "open",
        "organization": {"name": "US Department of Veterans Affairs", "type": "government", "website": "https://www.va.gov"},
        "location": {"name": "Houston, TX", "state": "Texas", "city": "Houston"},
        "categories": ["clinical-pharmacy", "consulting", "veteran-care"],
        "requirements": ["PharmD degree", "Board-certified pharmacotherapy specialist (BCPS)", "3+ years clinical experience", "VA clearance eligible"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "340B Drug Pricing Program Compliance Audit",
        "description": "University hospital system seeks an experienced pharmacy consulting firm to conduct a comprehensive 340B compliance audit covering all covered entity types, contract pharmacy arrangements, and manufacturer rebate reconciliation.",
        "deadline": "2026-06-30",
        "posted_date": "2026-04-20",
        "url": "https://www.pharmacist.com/rfp/340b-audit-2026",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$200K - $400K",
        "contact_name": "Maria Rodriguez",
        "contact_email": "m.rodriguez@uhealth.edu",
        "status": "open",
        "organization": {"name": "University of Michigan Health System", "type": "academic", "website": "https://www.uofmhealth.org"},
        "location": {"name": "Ann Arbor, MI", "state": "Michigan", "city": "Ann Arbor"},
        "categories": ["340b-program", "compliance", "consulting"],
        "requirements": ["340B program expertise", "CPA certification", "Healthcare audit experience", "HRSA compliance knowledge"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Telepharmacy Services for Rural Health Clinics",
        "description": "State rural health office is seeking telepharmacy service providers to deliver remote pharmacist consultations, medication dispensing oversight, and patient counseling for 12 rural clinics across the state.",
        "deadline": "2026-07-30",
        "posted_date": "2026-05-15",
        "url": "https://www.pharmacist.com/rfp/telepharmacy-rural",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$1M - $2M",
        "contact_name": "Robert Thompson",
        "contact_email": "r.thompson@ruralhealth.mt.gov",
        "status": "open",
        "organization": {"name": "Montana Office of Rural Health", "type": "government", "website": "https://healthinfo.montana.edu"},
        "location": {"name": "Helena, MT", "state": "Montana", "city": "Helena"},
        "categories": ["telepharmacy", "rural-health", "pharmacy-services"],
        "requirements": ["Licensed pharmacist in Montana", "Telepharmacy platform capability", "Experience with rural populations", "DEA registration"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Pharmacy Automation and Robotics Implementation",
        "description": "Large hospital network seeks vendors to propose and implement pharmacy automation solutions including robotic dispensing systems, automated IV compounding, and barcode medication administration for 5 hospital locations.",
        "deadline": "2026-09-15",
        "posted_date": "2026-05-20",
        "url": "https://www.pharmacist.com/rfp/automation-robotics",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$3M - $8M",
        "contact_name": "Linda Park",
        "contact_email": "l.park@northwellhealth.org",
        "status": "open",
        "organization": {"name": "Northwell Health", "type": "nonprofit", "website": "https://www.northwell.edu"},
        "location": {"name": "New Hyde Park, NY", "state": "New York", "city": "New Hyde Park"},
        "categories": ["technology", "automation", "hospital-pharmacy"],
        "requirements": ["FDA 510(k) clearance for devices", "5+ hospital implementations", "USP 797/800 compliance", "HL7/FHIR integration capability"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Specialty Pharmacy Services for Oncology Center",
        "description": "Comprehensive cancer center seeks specialty pharmacy partner to manage oral oncolytic dispensing, patient assistance programs, prior authorization services, and outcomes tracking for 3,000+ oncology patients annually.",
        "deadline": "2026-08-20",
        "posted_date": "2026-05-12",
        "url": "https://www.pharmacist.com/rfp/specialty-oncology",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$2M - $5M",
        "contact_name": "Dr. Angela Foster",
        "contact_email": "a.foster@mdanderson.org",
        "status": "open",
        "organization": {"name": "MD Anderson Cancer Center", "type": "academic", "website": "https://www.mdanderson.org"},
        "location": {"name": "Houston, TX", "state": "Texas", "city": "Houston"},
        "categories": ["specialty-pharmacy", "oncology", "patient-care"],
        "requirements": ["URAC specialty pharmacy accreditation", "Oncology pharmacy expertise", "REMS program experience", "Patient assistance program management"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Pharmacy Workforce Development and Training Program",
        "description": "National pharmacy association seeks proposals for developing a comprehensive continuing education and workforce training platform targeting early-career pharmacists, covering clinical skills, leadership, and business management.",
        "deadline": "2026-07-01",
        "posted_date": "2026-04-25",
        "url": "https://www.pharmacist.com/rfp/workforce-training",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$300K - $600K",
        "contact_name": "David Kim",
        "contact_email": "d.kim@pharmacist.com",
        "status": "open",
        "organization": {"name": "American Pharmacists Association", "type": "nonprofit", "website": "https://www.pharmacist.com"},
        "location": {"name": "Washington, DC", "state": "District of Columbia", "city": "Washington"},
        "categories": ["education", "workforce-development", "continuing-education"],
        "requirements": ["ACPE accreditation provider", "LMS platform capability", "Pharmacy education experience", "Instructional design expertise"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Opioid Stewardship Program Development",
        "description": "County health department seeks pharmacy consultants to design and implement a county-wide opioid stewardship program including prescriber education, naloxone distribution, and PDMP integration for community pharmacies.",
        "deadline": "2026-06-15",
        "posted_date": "2026-04-10",
        "url": "https://www.pharmacist.com/rfp/opioid-stewardship",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$150K - $300K",
        "contact_name": "Jennifer Walsh",
        "contact_email": "j.walsh@franklin.oh.us",
        "status": "open",
        "organization": {"name": "Franklin County Public Health", "type": "government", "website": "https://myfcph.org"},
        "location": {"name": "Columbus, OH", "state": "Ohio", "city": "Columbus"},
        "categories": ["public-health", "opioid-stewardship", "community-pharmacy"],
        "requirements": ["Public health pharmacy experience", "PDMP integration knowledge", "Community outreach track record", "Grant management experience"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Compounding Pharmacy Services for Dermatology Clinic Network",
        "description": "Multi-state dermatology practice seeks a USP 795/800 compliant compounding pharmacy to provide custom dermatological preparations including hormone creams, specialty topicals, and pediatric formulations.",
        "deadline": "2026-08-10",
        "posted_date": "2026-05-18",
        "url": "https://www.pharmacist.com/rfp/compounding-derm",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$400K - $800K",
        "contact_name": "Dr. Patricia Nguyen",
        "contact_email": "p.nguyen@advancedderm.com",
        "status": "open",
        "organization": {"name": "Advanced Dermatology Partners", "type": "private", "website": "https://www.advancedderm.com"},
        "location": {"name": "Parsippany, NJ", "state": "New Jersey", "city": "Parsippany"},
        "categories": ["compounding", "dermatology", "specialty-pharmacy"],
        "requirements": ["USP 795/800 compliance", "PCAB accreditation preferred", "Multi-state shipping license", "Stability testing program"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Medication Therapy Management for Medicare Advantage Plan",
        "description": "Health insurance company seeks pharmacy providers for comprehensive medication therapy management (MTM) services for 50,000+ Medicare Advantage beneficiaries, including CMR, TMR, and adherence programs.",
        "deadline": "2026-09-01",
        "posted_date": "2026-05-22",
        "url": "https://www.pharmacist.com/rfp/mtm-medicare",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$1.5M - $3M",
        "contact_name": "Michael Bryant",
        "contact_email": "m.bryant@humana.com",
        "status": "open",
        "organization": {"name": "Humana Inc.", "type": "private", "website": "https://www.humana.com"},
        "location": {"name": "Louisville, KY", "state": "Kentucky", "city": "Louisville"},
        "categories": ["mtm", "medicare", "managed-care"],
        "requirements": ["MTM platform certified", "CMS Part D Star Rating experience", "URAC MTM accreditation", "Pharmacist workforce of 20+"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Pharmacy Informatics System Modernization",
        "description": "Academic medical center seeks proposals to modernize its pharmacy information system including EHR integration, clinical decision support, inventory management, and real-time analytics dashboard.",
        "deadline": "2026-10-01",
        "posted_date": "2026-05-25",
        "url": "https://www.pharmacist.com/rfp/informatics-modernization",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$2M - $4M",
        "contact_name": "Dr. Kevin Zhang",
        "contact_email": "k.zhang@clevelandclinic.org",
        "status": "open",
        "organization": {"name": "Cleveland Clinic", "type": "nonprofit", "website": "https://my.clevelandclinic.org"},
        "location": {"name": "Cleveland, OH", "state": "Ohio", "city": "Cleveland"},
        "categories": ["technology", "informatics", "hospital-pharmacy"],
        "requirements": ["Epic/Cerner integration experience", "HL7 FHIR R4 certified", "Pharmacy informatics team", "HITRUST CSF certification"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Community Pharmacy Immunization Program Expansion",
        "description": "State department of health seeks pharmacy partners to expand immunization services in underserved communities, including vaccine storage and handling, patient outreach, and CDC reporting integration.",
        "deadline": "2026-07-20",
        "posted_date": "2026-05-05",
        "url": "https://www.pharmacist.com/rfp/immunization-expansion",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$800K - $1.5M",
        "contact_name": "Rachel Adams",
        "contact_email": "r.adams@health.ga.gov",
        "status": "open",
        "organization": {"name": "Georgia Department of Public Health", "type": "government", "website": "https://dph.georgia.gov"},
        "location": {"name": "Atlanta, GA", "state": "Georgia", "city": "Atlanta"},
        "categories": ["immunization", "public-health", "community-pharmacy"],
        "requirements": ["CDC Vaccines for Children provider", "Immunization Information System reporting", "Cold chain management capability", "Multilingual patient education materials"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Long-Term Care Pharmacy Consultant Services",
        "description": "Nursing home chain with 25 facilities seeks a pharmacy consulting group for monthly drug regimen reviews, staff education, emergency medication supply management, and regulatory compliance support.",
        "deadline": "2026-06-25",
        "posted_date": "2026-04-15",
        "url": "https://www.pharmacist.com/rfp/ltc-pharmacy",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$600K - $1M",
        "contact_name": "Thomas Green",
        "contact_email": "t.green@sunrisesenior.com",
        "status": "open",
        "organization": {"name": "Sunrise Senior Living", "type": "private", "website": "https://www.sunriseseniorliving.com"},
        "location": {"name": "McLean, VA", "state": "Virginia", "city": "McLean"},
        "categories": ["long-term-care", "consulting", "geriatric-pharmacy"],
        "requirements": ["CGP certification preferred", "Long-term care pharmacy experience", "CMS F-tag compliance knowledge", "State surveyor relationship experience"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Pharmacogenomics Testing and Consultation Service",
        "description": "Integrated health system seeks partners to implement a pharmacogenomics clinical service including genetic testing, clinical decision support integration, and pharmacist-led medication optimization consultations.",
        "deadline": "2026-09-30",
        "posted_date": "2026-05-20",
        "url": "https://www.pharmacist.com/rfp/pharmacogenomics",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$1M - $2.5M",
        "contact_name": "Dr. Susan Park",
        "contact_email": "s.park@kaiserpermanente.org",
        "status": "open",
        "organization": {"name": "Kaiser Permanente", "type": "nonprofit", "website": "https://www.kaiserpermanente.org"},
        "location": {"name": "Oakland, CA", "state": "California", "city": "Oakland"},
        "categories": ["pharmacogenomics", "precision-medicine", "clinical-pharmacy"],
        "requirements": ["CLIA-certified lab partnership", "CPIC guideline implementation experience", "EHR CDS integration", "Board-certified pharmacogenomics pharmacist"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Hazardous Drug Handling Compliance Assessment",
        "description": "Multi-hospital system needs a qualified pharmacy consulting firm to assess USP 800 compliance across 8 facilities and develop remediation plans for hazardous drug handling, storage, and disposal.",
        "deadline": "2026-06-20",
        "posted_date": "2026-04-30",
        "url": "https://www.pharmacist.com/rfp/usp800-compliance",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$100K - $250K",
        "contact_name": "Amy Richardson",
        "contact_email": "a.richardson@commonspirit.org",
        "status": "open",
        "organization": {"name": "CommonSpirit Health", "type": "nonprofit", "website": "https://www.commonspirit.org"},
        "location": {"name": "Chicago, IL", "state": "Illinois", "city": "Chicago"},
        "categories": ["compliance", "hospital-pharmacy", "safety"],
        "requirements": ["USP 800 expertise", "Industrial hygiene assessment capability", "Multi-site assessment experience", "ASHP guideline familiarity"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Pharmacy Supply Chain Optimization Study",
        "description": "Hospital purchasing cooperative seeks a consulting firm to analyze and optimize pharmacy supply chain operations across 40 member hospitals, including GPO contract analysis, inventory optimization, and waste reduction strategies.",
        "deadline": "2026-08-30",
        "posted_date": "2026-05-08",
        "url": "https://www.pharmacist.com/rfp/supply-chain-optimization",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$300K - $500K",
        "contact_name": "William Harris",
        "contact_email": "w.harris@premierinc.com",
        "status": "open",
        "organization": {"name": "Premier Inc.", "type": "private", "website": "https://www.premierinc.com"},
        "location": {"name": "Charlotte, NC", "state": "North Carolina", "city": "Charlotte"},
        "categories": ["supply-chain", "consulting", "hospital-pharmacy"],
        "requirements": ["GPO contract analysis experience", "Pharmaceutical distribution knowledge", "Data analytics capability", "Six Sigma certification preferred"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Antimicrobial Stewardship Program for Community Hospital",
        "description": "Community hospital seeks infectious disease pharmacist consultants to establish and manage an antimicrobial stewardship program meeting Joint Commission requirements, including protocol development, education, and outcome tracking.",
        "deadline": "2026-07-10",
        "posted_date": "2026-05-02",
        "url": "https://www.pharmacist.com/rfp/antimicrobial-stewardship",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$150K - $250K",
        "contact_name": "Dr. Brian Moore",
        "contact_email": "b.moore@mercyhealth.com",
        "status": "open",
        "organization": {"name": "Mercy Health", "type": "nonprofit", "website": "https://www.mercy.com"},
        "location": {"name": "Cincinnati, OH", "state": "Ohio", "city": "Cincinnati"},
        "categories": ["antimicrobial-stewardship", "infectious-disease", "hospital-pharmacy"],
        "requirements": ["BCIDP certification", "ASP program development experience", "Joint Commission standards knowledge", "Antibiogram development expertise"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Cannabis Pharmacy Regulatory Consulting",
        "description": "State pharmacy board seeks consulting services to develop regulatory framework and pharmacist training requirements for the state's new medical cannabis dispensary program launching in 2027.",
        "deadline": "2026-08-15",
        "posted_date": "2026-05-14",
        "url": "https://www.pharmacist.com/rfp/cannabis-regulatory",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$200K - $350K",
        "contact_name": "Karen Lewis",
        "contact_email": "k.lewis@pharmacy.ky.gov",
        "status": "open",
        "organization": {"name": "Kentucky Board of Pharmacy", "type": "government", "website": "https://pharmacy.ky.gov"},
        "location": {"name": "Frankfort, KY", "state": "Kentucky", "city": "Frankfort"},
        "categories": ["regulatory", "cannabis", "consulting"],
        "requirements": ["Pharmacy regulatory experience", "Cannabis program knowledge", "State-level policy development", "Training curriculum design"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Pediatric Pharmacy Services for Children's Hospital",
        "description": "Children's hospital seeks specialized pediatric pharmacy staffing and consulting services including neonatal dosing protocols, pediatric compounding, and family medication education programs.",
        "deadline": "2026-09-10",
        "posted_date": "2026-05-19",
        "url": "https://www.pharmacist.com/rfp/pediatric-pharmacy",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$800K - $1.5M",
        "contact_name": "Dr. Emily Carter",
        "contact_email": "e.carter@childrens.harvard.edu",
        "status": "open",
        "organization": {"name": "Boston Children's Hospital", "type": "academic", "website": "https://www.childrenshospital.org"},
        "location": {"name": "Boston, MA", "state": "Massachusetts", "city": "Boston"},
        "categories": ["pediatric-pharmacy", "hospital-pharmacy", "clinical-pharmacy"],
        "requirements": ["PGY2 pediatric pharmacy residency", "Neonatal dosing expertise", "USP 797 compounding compliance", "Family-centered care experience"],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Disaster Preparedness Pharmaceutical Stockpile Management",
        "description": "FEMA regional office seeks proposals for managing the pharmaceutical component of strategic national stockpile readiness including inventory rotation, distribution planning, and pharmacist rapid-deployment team coordination.",
        "deadline": "2026-10-15",
        "posted_date": "2026-05-24",
        "url": "https://www.pharmacist.com/rfp/disaster-pharma-stockpile",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$1M - $3M",
        "contact_name": "Colonel Mark Stevens",
        "contact_email": "m.stevens@fema.dhs.gov",
        "status": "open",
        "organization": {"name": "FEMA Region IV", "type": "government", "website": "https://www.fema.gov"},
        "location": {"name": "Atlanta, GA", "state": "Georgia", "city": "Atlanta"},
        "categories": ["disaster-preparedness", "public-health", "supply-chain"],
        "requirements": ["Federal contracting experience", "SNS deployment knowledge", "Emergency pharmacy operations", "Security clearance eligible"],
    },
]


# ---------------------------------------------------------------------------
# Demo data for AI features (Foresight, Coalition, Simulator, Copilot, Win Room).
# All ids are deterministic so MERGE-based writes are fully idempotent across
# restarts (unlike MOCK_RFPS whose uuids regenerate per process).
# ---------------------------------------------------------------------------

def _hist_rfp(rfp_id, title, posted_date, org, org_type, state, categories, requirements):
    """Build a closed, historical RFP dict for repost-cadence forecasting."""
    return {
        "id": rfp_id,
        "title": title,
        "description": f"Historical solicitation: {title}.",
        "deadline": posted_date,
        "posted_date": posted_date,
        "url": f"https://www.pharmacist.com/rfp/{rfp_id}",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": None,
        "status": "closed",
        "organization": {"name": org, "type": org_type},
        "location": {"name": state, "state": state, "city": state},
        "categories": categories,
        "requirements": requirements,
    }


# Organizations with regular posting cadences -> Foresight can project the next
# window within the default 180-day horizon (today is mid-2026).
#
# IMPORTANT: these forecast agencies are intentionally DISTINCT from the
# MOCK_RFPS organizations. Reusing a MOCK org here would add a stray 2026 posting
# to its history, corrupting the cadence (e.g. two postings a few days apart ->
# a bogus "every 0.1 months" prediction). Keeping them separate gives each
# forecast org a clean, multi-year posting rhythm.
FORECAST_HISTORY = [
    # Oncology specialty pharmacy — yearly cadence (last 2025-07 -> predict ~2026-07).
    # Matches the demo pharmacist (oncology / specialty-pharmacy, Texas) for a
    # high-fit personalized prediction.
    _hist_rfp("seed-onc-2023", "Oncology Specialty Pharmacy Services (2023 cycle)", "2023-07-10",
              "Lone Star Oncology Pharmacy Network", "academic", "Texas",
              ["specialty-pharmacy", "oncology", "patient-care"],
              ["URAC specialty accreditation", "Oncology expertise"]),
    _hist_rfp("seed-onc-2024", "Oncology Specialty Pharmacy Services (2024 cycle)", "2024-07-08",
              "Lone Star Oncology Pharmacy Network", "academic", "Texas",
              ["specialty-pharmacy", "oncology", "patient-care"],
              ["URAC specialty accreditation", "Oncology expertise"]),
    _hist_rfp("seed-onc-2025", "Oncology Specialty Pharmacy Services (2025 cycle)", "2025-07-12",
              "Lone Star Oncology Pharmacy Network", "academic", "Texas",
              ["specialty-pharmacy", "oncology", "patient-care"],
              ["URAC specialty accreditation", "Oncology expertise"]),
    # State Medicaid PBM re-bid — yearly cadence (last 2025-09 -> predict ~2026-09).
    _hist_rfp("seed-dhcs-2022", "PBM Services for State Medicaid (2022 cycle)", "2022-09-01",
              "Pacific Medicaid Pharmacy Board", "government", "California",
              ["pharmacy-services", "medicaid", "pbm"], ["PBM experience", "URAC accreditation"]),
    _hist_rfp("seed-dhcs-2023", "PBM Services for State Medicaid (2023 cycle)", "2023-09-05",
              "Pacific Medicaid Pharmacy Board", "government", "California",
              ["pharmacy-services", "medicaid", "pbm"], ["PBM experience", "URAC accreditation"]),
    _hist_rfp("seed-dhcs-2024", "PBM Services for State Medicaid (2024 cycle)", "2024-09-03",
              "Pacific Medicaid Pharmacy Board", "government", "California",
              ["pharmacy-services", "medicaid", "pbm"], ["PBM experience", "URAC accreditation"]),
    _hist_rfp("seed-dhcs-2025", "PBM Services for State Medicaid (2025 cycle)", "2025-09-02",
              "Pacific Medicaid Pharmacy Board", "government", "California",
              ["pharmacy-services", "medicaid", "pbm"], ["PBM experience", "URAC accreditation"]),
    # Veterans clinical pharmacy — ~10-month cycle (last 2025-10 -> predict ~2026-08).
    _hist_rfp("seed-va-2024-02", "Clinical Pharmacy Consulting (early 2024)", "2024-02-01",
              "Federal Veterans Pharmacy Services", "government", "Texas",
              ["clinical-pharmacy", "consulting"], ["PharmD", "BCPS"]),
    _hist_rfp("seed-va-2024-12", "Clinical Pharmacy Consulting (late 2024)", "2024-12-01",
              "Federal Veterans Pharmacy Services", "government", "Texas",
              ["clinical-pharmacy", "consulting"], ["PharmD", "BCPS"]),
    _hist_rfp("seed-va-2025-10", "Clinical Pharmacy Consulting (late 2025)", "2025-10-01",
              "Federal Veterans Pharmacy Services", "government", "Texas",
              ["clinical-pharmacy", "consulting"], ["PharmD", "BCPS"]),
    # Public-health immunization — ~8-month cycle (last 2025-11 -> predict ~2026-07).
    _hist_rfp("seed-ga-2024-07", "Immunization Program Expansion (2024 H2)", "2024-07-01",
              "Southeast Public Health Pharmacy Consortium", "government", "Georgia",
              ["immunization", "public-health", "community-pharmacy"], ["VFC provider", "Cold chain"]),
    _hist_rfp("seed-ga-2025-03", "Immunization Program Expansion (2025 H1)", "2025-03-01",
              "Southeast Public Health Pharmacy Consortium", "government", "Georgia",
              ["immunization", "public-health", "community-pharmacy"], ["VFC provider", "Cold chain"]),
    _hist_rfp("seed-ga-2025-11", "Immunization Program Expansion (2025 H2)", "2025-11-01",
              "Southeast Public Health Pharmacy Consortium", "government", "Georgia",
              ["immunization", "public-health", "community-pharmacy"], ["VFC provider", "Cold chain"]),
]


def _open_rfp(rfp_id, title, org, org_type, state, categories, requirements):
    return {
        "id": rfp_id,
        "title": title,
        "description": f"Open solicitation: {title}.",
        "deadline": "2026-10-01",
        "posted_date": "2026-05-15",
        "url": f"https://www.pharmacist.com/rfp/{rfp_id}",
        "source_url": "https://www.pharmacist.com/rfp",
        "budget_range": "$500K - $1M",
        "status": "open",
        "organization": {"name": org, "type": org_type},
        "location": {"name": state, "state": state, "city": state},
        "categories": categories,
        "requirements": requirements,
    }


# Stable open RFPs the demo pharmacists apply to (enables peer recs + history).
DEMO_OPEN_RFPS = [
    _open_rfp("seed-open-340b", "340B Compliance Audit (open)", "University of Michigan Health System",
              "academic", "Michigan", ["340b-program", "compliance", "consulting"],
              ["340B expertise", "CPA certification", "HRSA compliance knowledge"]),
    _open_rfp("seed-open-onc", "Specialty Oncology Pharmacy (open)", "MD Anderson Cancer Center",
              "academic", "Texas", ["specialty-pharmacy", "oncology", "patient-care"],
              ["URAC specialty accreditation", "Oncology expertise", "REMS experience"]),
    _open_rfp("seed-open-mtm", "Medicare MTM Services (open)", "Humana Inc.",
              "private", "Kentucky", ["mtm", "medicare", "clinical-pharmacy"],
              ["MTM platform", "URAC MTM accreditation", "Star Rating experience"]),
    _open_rfp("seed-open-imm", "Community Immunization Program (open)", "Georgia Department of Public Health",
              "government", "Georgia", ["immunization", "public-health", "community-pharmacy"],
              ["VFC provider", "IIS reporting", "Cold chain management"]),
]


# Five demo pharmacists with complementary specialties/certs -> Coalition Finder,
# Simulator history, peer recommendations.
DEMO_PHARMACISTS = [
    {"user_id": "demo-pharm-1", "full_name": "Dr. Alice Lee", "location_state": "California",
     "specialties": ["340b-program", "compliance"], "certifications": ["PharmD", "CPA", "340B Certified"]},
    {"user_id": "demo-pharm-2", "full_name": "Dr. Raj Patel", "location_state": "Texas",
     "specialties": ["oncology", "specialty-pharmacy"], "certifications": ["PharmD", "BCOP"]},
    {"user_id": "demo-pharm-3", "full_name": "Dr. Maria Gomez", "location_state": "Ohio",
     "specialties": ["mtm", "medicare", "clinical-pharmacy"], "certifications": ["PharmD", "BCPS"]},
    {"user_id": "demo-pharm-4", "full_name": "Dr. Sam Wright", "location_state": "New York",
     "specialties": ["technology", "informatics", "automation"], "certifications": ["PharmD", "CPHIMS"]},
    {"user_id": "demo-pharm-5", "full_name": "Dr. Tara Nguyen", "location_state": "Georgia",
     "specialties": ["immunization", "public-health", "community-pharmacy"],
     "certifications": ["PharmD", "APhA Immunization"]},
]

# (user_id, rfp_id, status) — wins on closed history, submissions on open RFPs.
# Shared open RFPs (340b: pharm-1 & pharm-3; mtm: pharm-3 & pharm-4) drive peer recs.
DEMO_APPLICATIONS = [
    ("demo-pharm-1", "seed-dhcs-2024", "won"),
    ("demo-pharm-1", "seed-open-340b", "submitted"),
    ("demo-pharm-2", "seed-va-2025-10", "won"),
    ("demo-pharm-2", "seed-open-onc", "submitted"),
    ("demo-pharm-3", "seed-ga-2025-11", "won"),
    ("demo-pharm-3", "seed-open-mtm", "submitted"),
    ("demo-pharm-3", "seed-open-340b", "submitted"),
    ("demo-pharm-4", "seed-dhcs-2023", "lost"),
    ("demo-pharm-4", "seed-open-mtm", "submitted"),
    ("demo-pharm-5", "seed-ga-2024-07", "won"),
    ("demo-pharm-5", "seed-open-imm", "submitted"),
]


def seed_demo_ai_data():
    """Seed historical + demo data powering the AI features. Idempotent."""
    from backend.graph.pharmacist_graph import (
        sync_pharmacist_profile_to_graph,
        sync_application_to_graph,
    )

    logger.info("Seeding AI demo data (forecast history, pharmacists, applications)...")
    for rfp in FORECAST_HISTORY + DEMO_OPEN_RFPS:
        create_rfp_with_relations({**rfp, **resolve_source(rfp)})

    for p in DEMO_PHARMACISTS:
        sync_pharmacist_profile_to_graph(
            user_id=p["user_id"],
            full_name=p["full_name"],
            location_state=p["location_state"],
            specialties=p["specialties"],
            certifications=p["certifications"],
        )

    for user_id, rfp_id, status in DEMO_APPLICATIONS:
        sync_application_to_graph(user_id=user_id, rfp_id=rfp_id, status=status,
                                 applied_at="2026-01-15")
    logger.info("AI demo data seed complete")


def seed_graph():
    stats = get_graph_stats()
    if stats["total_rfps"] == 0:
        logger.info(f"Seeding {len(MOCK_RFPS)} mock RFPs into Neo4j...")
        for rfp in MOCK_RFPS:
            create_rfp_with_relations({**rfp, **resolve_source(rfp)})
        logger.info("Seed data complete")
    else:
        logger.info(f"Graph already has {stats['total_rfps']} RFPs, skipping mock seed")

    # AI demo data uses deterministic ids (idempotent) — always ensure present.
    try:
        seed_demo_ai_data()
    except Exception as e:
        logger.warning(f"AI demo data seed failed: {e}")
