# -- Touch 1: Introduction ---------------------------------------------------
TOUCH1_PROMPT = """You are writing a personalized outreach email on behalf of the
American Pharmacists Association (APhA).

Prospect profile:
- Name: {first_name} {last_name}
- License type: {license_type}
- Specialty / Practice setting: {specialty}
- State: {state}
- Career stage: {career_stage}
- Credential: {credential}

Campaign context:
- Outreach tier: {tier}
- Key value proposition for this tier: {value_prop}

Write a personalized cold email. Rules:
1. Subject line: max 50 chars, no "free", no "join now", no spam words
   Make it feel like a peer or colleague reaching out, not a marketing team.
   Reference something specific to their role or state.
2. Body: 100-140 words, plain text
   - Open with a specific observation about pharmacists in their specialty/state
   - One clear, specific value statement (NOT a list of everything APhA offers)
   - A genuine question OR a single low-friction CTA
   - CAN-SPAM compliant footer will be added automatically -- do not add it
3. Tone: colleague-to-colleague, not corporate sales
4. Do NOT use: "I hope this email finds you well", "I wanted to reach out",
   "synergize", "leverage", "take your career to the next level"
5. Do NOT mention the unsubscribe link -- it is added automatically

Respond ONLY as JSON:
{{"subject": "...", "body": "..."}}
"""

# -- Touch 2: Value Deepening ------------------------------------------------
TOUCH2_PROMPT = """Write a follow-up email (touch 2 of 3) to a pharmacist who opened
but did not respond to a previous APhA outreach email.

Prospect: {first_name}, {license_type}, {specialty}, {state}
Touch 1 subject was: "{touch1_subject}"
Days since touch 1: {days_since_touch1}

This email should:
1. Reference the previous email naturally (1 sentence max -- not "just following up")
2. Go deeper on ONE specific benefit -- choose the most relevant to their specialty:
   - Hospital pharmacist -> CPE + clinical decision support tools
   - Community pharmacist -> advocacy + career advancement
   - New practitioner -> mentorship + NP LIFE conference
   - Student -> NAPLEX prep + chapter leadership
3. Include one concrete data point (e.g., "300+ ACPE-accredited CPE hours",
   "8% salary premium")
4. Soft CTA -- ask a question or offer something, don't demand action
5. Body: 80-110 words

Respond ONLY as JSON:
{{"subject": "...", "body": "..."}}
"""

# -- Touch 3: Closing / Last Ask ---------------------------------------------
TOUCH3_PROMPT = """Write the final email (touch 3 of 3) in an APhA outreach sequence.
This is the last email -- make it count but don't be desperate.

Prospect: {first_name}, {license_type}, {specialty}, {state}
Sequence context: They received 2 previous emails, did not respond.
Previous subjects: "{touch1_subject}" / "{touch2_subject}"

This email should:
1. Be the shortest of the 3 (60-90 words)
2. Open with a "closing the loop" framing that respects their time
3. Make one final, specific value offer -- ideally tied to a time-sensitive
   APhA benefit (e.g., upcoming Annual Meeting early registration,
   CPE deadline for their state renewal)
4. End with a clean, warm sign-off without being pushy

Respond ONLY as JSON:
{{"subject": "...", "body": "..."}}
"""

# -- Tier-specific value propositions -----------------------------------------
TIER_VALUE_PROPS = {
    "student": (
        "APhA-ASP chapter membership, NAPLEX prep through PharmacyLibrary, "
        "discounted Annual Meeting registration, leadership opportunities, "
        "and a peer network across 145 pharmacy schools."
    ),
    "new_practitioner": (
        "APhA ADVANCE mentorship platform, NP LIFE conference, "
        "New Practitioner Network, career development tools, "
        "and 300+ CPE hours -- all at a discounted rate for your first 3 years."
    ),
    "pharmacist": (
        "300+ ACPE-accredited CPE hours (enough to meet most state requirements "
        "in one membership), JAPhA and Pharmacy Today journals, Annual Meeting access, "
        "advocacy representation in Washington DC, and APhA ENGAGE community."
    ),
    "technician": (
        "Pharmacy technician certification resources, Pharmacy Today newsletter, "
        "career advancement resources, advocacy support, "
        "and a national community of pharmacy professionals."
    ),
}
