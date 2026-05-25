"""
SendGrid - 3 tailored nurture sequences, one per acquisition funnel.
Each sequence is personalized with the lead's specific data.
"""
from apps.acquisition.db.models.lead import AcquisitionLead
from core.config import get_settings
from core.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def trigger_nurture_sequence(lead: AcquisitionLead):
    """Route lead to the right email sequence based on source tool."""
    sequences = {
        "salary": _salary_sequence,
        "interaction": _interaction_sequence,
        "career": _career_sequence,
    }
    handler = sequences.get(lead.source_tool, _generic_sequence)
    handler(lead)


def _salary_sequence(lead: AcquisitionLead):
    """
    3-email salary nurture sequence:
    Email 1 (instant): Full salary report PDF + "How APhA members earn more"
    Email 2 (day 3):   "5 pharmacists in {state} who grew their salary with APhA"
    Email 3 (day 7):   Membership offer with salary-angle CTA
    """
    gap = lead.salary_gap_usd or 0
    percentile = lead.salary_percentile or 50
    logger.info(
        f"[SENDGRID MOCK] Salary sequence -> {lead.email} | "
        f"State: {lead.state} | Percentile: {percentile}th | Gap: ${gap:,}"
    )


def _interaction_sequence(lead: AcquisitionLead):
    """
    3-email interaction nurture sequence:
    Email 1 (instant): "Your APhA Drug Reference bookmark" + top 10 interaction pairs
    Email 2 (day 2):   Clinical case study featuring a real interaction
    Email 3 (day 5):   "Unlimited checks + 300 CPE hours - APhA membership"
    """
    logger.info(f"[SENDGRID MOCK] Interaction sequence -> {lead.email}")


def _career_sequence(lead: AcquisitionLead):
    """
    3-email career nurture sequence:
    Email 1 (instant): Full action plan PDF + score breakdown
    Email 2 (day 3):   "How pharmacists at your stage are using APhA to close {top_gap}"
    Email 3 (day 7):   Membership offer highlighting resources for their specific gap
    """
    score = lead.career_score or 0
    gap = lead.top_gap_dimension or "professional development"
    logger.info(
        f"[SENDGRID MOCK] Career sequence -> {lead.email} | "
        f"Score: {score} | Top gap: {gap}"
    )


def _generic_sequence(lead: AcquisitionLead):
    logger.info(f"[SENDGRID MOCK] Generic sequence -> {lead.email}")
