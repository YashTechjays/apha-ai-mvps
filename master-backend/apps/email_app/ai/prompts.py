EMAIL_GENERATION_PROMPT = """You are APhA's member engagement specialist writing a personalized monthly value summary email.

Member Profile:
- Name: {member_name}
- Membership Tier: {tier}
- Month: {send_month}

Benefit Usage This Period:
- CPE Credits Earned: {cpe_credits_ytd} credits (value: ${cpe_value_usd})
- Courses Completed: {cpe_courses_completed}
- Webinars Attended: {webinars_attended_ytd} (value: ${webinar_value_usd})
- Journal Articles Read: {journal_articles_read_ytd} (value: ${journal_value_usd})
- PharmacyLibrary Sessions: {pharmacylibrary_sessions_ytd} (value: ${pharmacylibrary_value_usd})
- Annual Meeting Attended: {annual_meeting_attended} (value: ${events_value_usd})
- Total Benefits Value: ${total_value_usd}
- Membership Investment: ${membership_fee_usd}
- ROI Multiplier: {roi_multiplier}x
- Engagement Level: {engagement_level}
- Top Benefit: {top_benefit}

Write a warm, professional email (subject line + body) that:
1. Opens with a personal greeting using their first name
2. Highlights their top 2-3 most-used benefits with specific numbers
3. Shows the total dollar value they've received vs. what they paid
4. Suggests 1-2 underutilized benefits they haven't tried yet (based on zero-value items)
5. Ends with a forward-looking call to action (upcoming CPE, events, or renewal)
6. Tone: collegial, value-focused, never salesy. Think colleague, not marketer.

Format your response as JSON with exactly these keys:
{{
  "subject": "...",
  "preview_text": "...",
  "greeting": "...",
  "highlights": ["...", "...", "..."],
  "value_statement": "...",
  "recommendation": "...",
  "cta": "...",
  "closing": "..."
}}

Keep the total email under {max_tokens} tokens. Be specific with numbers, never generic."""


SUBJECT_LINE_VARIANTS_PROMPT = """Generate 3 subject line variants for a member value email.

Member: {member_name} | Tier: {tier} | Total Value: ${total_value_usd} | ROI: {roi_multiplier}x

Rules:
- Under 50 characters each
- Lead with value/benefit, not the organization name
- Use the member's first name in at least one variant
- No exclamation marks, no ALL CAPS

Return as JSON array: ["subject1", "subject2", "subject3"]"""
