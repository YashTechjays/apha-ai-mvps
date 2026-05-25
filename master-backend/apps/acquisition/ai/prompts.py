# -- Salary Benchmarker --------------------------------------------------------

SALARY_ANALYSIS_PROMPT = """You are an APhA career advisor analyzing salary data for a pharmacist.

Member profile:
- License type: {license_type}
- Specialty: {specialty}
- State: {state_name}
- Years of experience: {years_experience}
- Current salary (if provided): ${current_salary}

Benchmark data:
- 25th percentile for their profile: ${p25}
- 50th percentile (median): ${p50}
- 75th percentile: ${p75}
- 90th percentile: ${p90}
- Their estimated percentile: {percentile}th

Write a personalized, 3-paragraph salary analysis (150-200 words total):
1. Paragraph 1: What their salary position means in context of their specific market
   (reference their state and specialty specifically)
2. Paragraph 2: Key factors driving salary in their specialty + 1-2 specific actions
   to increase earning potential
3. Paragraph 3: How APhA membership correlates with salary outcomes (cite the 8% premium
   naturally, not as a sales pitch)

Keep it honest, specific, and data-driven. If no current salary provided, focus on
what the benchmarks mean for their profile.
Plain text only - no markdown, no bullet points.
"""

SALARY_QUICK_INSIGHT_PROMPT = """In exactly 1 sentence (max 20 words), give a sharp insight
about this pharmacist's salary situation:
- Specialty: {specialty}, State: {state}, Percentile: {percentile}th
Example: "Hospital pharmacists in Texas are seeing 12% faster wage growth than the national average."
"""

# -- Drug Interaction Checker --------------------------------------------------

INTERACTION_ANALYSIS_PROMPT = """You are a clinical pharmacist explaining a drug interaction.

Drug A: {drug_a}
Drug B: {drug_b}
Known interaction data: {interaction_data}

Write a clinical interaction summary for a pharmacist audience (120-160 words):
1. Severity assessment with clear rationale
2. Mechanism explanation (1-2 sentences, clinical level)
3. Clinical significance - what actually happens to the patient
4. Specific management recommendation

If the combination is MAJOR severity: start with "MAJOR INTERACTION -"
If MODERATE: start with "MODERATE INTERACTION -"
If MINOR or none: start with "MINOR/NO SIGNIFICANT INTERACTION -"

If no known interaction data is provided for this pair, say so clearly
and note that absence of data does not equal absence of interaction; always verify
with current clinical resources.

Plain text only. Clinical, precise, actionable.
"""

# -- Career Readiness Scorer ---------------------------------------------------

CAREER_SCORE_PROMPT = """You are a pharmacy career expert scoring a pharmacist's
career readiness across 6 dimensions.

Pharmacist profile:
{profile_json}

Based on the responses, score each dimension 0-100 and provide analysis.
Be honest - not everyone scores high, and realistic scores are more valuable.

Scoring guide:
- 80-100: Strong - exceeds expectations for career stage
- 60-79: Solid - meets expectations, room for targeted growth
- 40-59: Developing - clear gaps, high opportunity
- 0-39: Early stage - significant development needed (normal for students/new practitioners)

Respond ONLY as valid JSON (no backticks, no preamble):
{{
  "overall_score": 68,
  "scores": {{
    "clinical_knowledge": 72,
    "patient_care": 65,
    "professional_development": 58,
    "leadership": 45,
    "business_acumen": 70,
    "networking": 50
  }},
  "summary": "2-sentence personalized summary of their overall profile",
  "top_strength": "clinical_knowledge",
  "top_strength_note": "1 sentence about what they're doing well",
  "top_gap": "leadership",
  "top_gap_note": "1 sentence about the gap - honest but constructive",
  "peer_comparison": "You score higher than X% of pharmacists at your career stage",
  "trajectory": "On track | Ahead of curve | Behind curve"
}}
"""

CAREER_ACTION_PLAN_PROMPT = """Based on this pharmacist's career assessment scores, write a
personalized 90-day action plan.

Profile: {profile_summary}
Scores: {scores_json}
Top gap: {top_gap} (score: {gap_score}/100)
Career stage: {career_stage}

Write 3 specific, actionable items for the next 90 days. For each:
- Action: Specific step (not generic advice)
- Why: 1 sentence on how it closes their gap
- APhA resource: Which specific APhA benefit helps (be specific: course name, program name)

This plan should make them feel that APhA membership directly addresses their gaps.
Be genuinely helpful - don't force APhA if it doesn't fit.

Respond ONLY as JSON:
{{
  "headline": "Your 90-day plan for {top_gap_label} development",
  "actions": [
    {{
      "title": "Specific action title",
      "description": "What to do and why",
      "apha_resource": "Specific APhA resource name",
      "apha_resource_url": "https://pharmacist.com/...",
      "timeline": "Week 1-2"
    }}
  ]
}}
"""
