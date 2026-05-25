NUDGE_EMAIL_PROMPT = """You are writing a personalized cross-sell email for an APhA member.

Member profile:
- Name: {first_name} {last_name}
- Tier: {tier}
- Specialty: {specialty}
- Member for: {years_as_member} years
- Currently active on: {active_streams}
- Currently NOT using: {target_product}

Why this member is a good candidate for {target_product}:
{reasons}

Product being promoted: {target_product}
Product description: {product_description}
CTA URL: {cta_url}

Write a short, warm, personalized email (120–180 words). Rules:
1. Start with their first name
2. Reference something specific about their current usage pattern
3. Make one clear, specific value statement about the product
4. Single CTA — no more than one link
5. Conversational tone — not salesy, not generic
6. Do NOT use subject line in body — only body text
7. Plain text only — no HTML, no markdown

Also write a subject line (max 50 chars) — separate from body.

Respond ONLY as JSON:
{{"subject": "...", "body": "..."}}
"""

BANNER_PROMPT = """Write a personalized in-portal banner message for an APhA member.

Member: {first_name}, {tier}, {specialty}
Target product: {target_product}
Reason they'd benefit: {top_reason}

Write:
- headline: 6–8 words, specific to them
- body: 1 sentence, 15–20 words
- cta_label: 3–4 words (button text)

JSON only: {{"headline": "...", "body": "...", "cta_label": "..."}}
"""

PRODUCT_DESCRIPTIONS = {
    "education": (
        "APhA's Learning Library includes 300+ ACPE-accredited CPE hours, free with membership. "
        "Certificate programs in Immunization, Diabetes Care, HIV Prevention, MTM, and more. "
        "All credits report automatically to CPE Monitor."
    ),
    "publications": (
        "Members get full access to the Journal of the American Pharmacists Association (JAPhA), "
        "Pharmacy Today, and PharmacyLibrary — APhA's digital textbook and drug reference platform "
        "with the Drug Information Handbook and NAPLEX review."
    ),
    "events": (
        "APhA hosts the Annual Meeting & Exposition (~10,000 attendees), NP LIFE for new "
        "practitioners, the Institute on Substance Use Disorders, and monthly live webinars — "
        "all with member discounts."
    ),
    "career": (
        "APhA's career platform includes a pharmacy-specific job board, APhA ADVANCE mentorship "
        "network, Career Pathways Program, residency and fellowship resources, and resume tools "
        "tailored to pharmacy careers."
    ),
    "advocacy": (
        "APhA advocates for pharmacists at the federal and state level. The Advocacy Action Center "
        "lets you contact legislators in seconds. APhA PAC amplifies pharmacists' political voice. "
        "APhA SmartBrief delivers personalized policy updates."
    ),
}

PRODUCT_CTA_URLS = {
    "education": "https://learn.pharmacist.com",
    "publications": "https://pharmacylibrary.com",
    "events": "https://www.pharmacist.com/events",
    "career": "https://www.pharmacist.com/career",
    "advocacy": "https://www.pharmacist.com/advocacy",
}
