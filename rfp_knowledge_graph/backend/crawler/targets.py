# All URLs below are verified accessible static-HTML procurement pages
# as of 2026-05-28. Each has been confirmed to contain pharmacy/Medicaid RFP content.

CRAWL_TARGETS = [
    # NY State DOH — RFP/RFA/IFB tables including EPIC pharmacy program
    {
        "url": "https://www.health.ny.gov/funding/",
        "include_patterns": ["rfp", "rfa", "ifb", "bid", "proposal", "pharmacy", "drug", "epic"],
        "max_pages": 20,
    },
    # Mississippi DOH — open RFP/RFQ solicitations
    {
        "url": "https://msdh.ms.gov/page/19,0,205.html",
        "include_patterns": ["rfp", "rfq", "bid", "proposal", "procurement"],
        "max_pages": 15,
    },
    # Mississippi Medicaid — Pharmacy Benefit Administrator audit RFP
    {
        "url": "https://medicaid.ms.gov/resources/procurement/",
        "include_patterns": ["rfp", "rfq", "bid", "pharmacy", "pbm", "medicaid"],
        "max_pages": 15,
    },
    # Georgia DCH — Pharmacy Benefit Manager IFP (State Health Benefit Plan)
    {
        "url": "https://dch.georgia.gov/divisionsoffices/office-procurement-services/bidding-opportunities",
        "include_patterns": ["rfp", "ifp", "bid", "pharmacy", "pbm", "proposal"],
        "max_pages": 15,
    },
    # Washington State HCA — RFP/RFA/RFI for Medicaid health and pharmacy services
    {
        "url": "https://www.hca.wa.gov/about-hca/bids-and-contracts",
        "include_patterns": ["rfp", "rfa", "rfi", "bid", "pharmacy", "medicaid", "proposal"],
        "max_pages": 20,
    },
    # Tennessee TennCare — live Pharmacy AAC Program RFP + upcoming Medicaid procurements
    {
        "url": "https://www.tn.gov/tenncare/information-statistics/upcoming-procurements.html",
        "include_patterns": ["rfp", "rfq", "pharmacy", "pbm", "medicaid", "procurement"],
        "max_pages": 15,
    },
    # North Carolina Medicaid — RFPs and RFIs
    {
        "url": "https://medicaid.ncdhhs.gov/requests-proposals-rfps-and-requests-information-rfis",
        "include_patterns": ["rfp", "rfi", "bid", "pharmacy", "medicaid", "proposal"],
        "max_pages": 15,
    },
]
