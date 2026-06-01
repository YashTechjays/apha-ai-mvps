"""One-time backfill: project existing PostgreSQL pharmacist profiles and
applications into the Neo4j graph (Enhancement #1).

Run inside the backend container:
    docker compose exec backend python -m backend.scripts.backfill_applications_to_graph
"""
from backend.db.session import SessionLocal
from backend.db.models.user import User, UserRole
from backend.db.models.pharmacist_profile import PharmacistProfile  # noqa: F401 — register mapper
from backend.db.models.application import Application
from backend.graph.pharmacist_graph import (
    sync_pharmacist_profile_to_graph,
    sync_application_to_graph,
)
from backend.utils.logger import get_logger

logger = get_logger("backfill_applications")


def run():
    db = SessionLocal()
    try:
        pharmacists = db.query(User).filter(User.role == UserRole.pharmacist).all()
        profiles_synced = 0
        for user in pharmacists:
            profile = user.profile
            if profile:
                sync_pharmacist_profile_to_graph(
                    user_id=user.id,
                    full_name=profile.full_name,
                    location_state=profile.location_state,
                    specialties=profile.specialties,
                    certifications=profile.certifications,
                )
                profiles_synced += 1

        apps = db.query(Application).all()
        apps_synced = 0
        for app in apps:
            sync_application_to_graph(
                user_id=app.user_id,
                rfp_id=app.rfp_id,
                status=app.status.value,
                applied_at=app.created_at.isoformat() if app.created_at else None,
            )
            apps_synced += 1

        logger.info(f"Backfill complete: {profiles_synced} profiles, {apps_synced} applications")
        return profiles_synced, apps_synced
    finally:
        db.close()


if __name__ == "__main__":
    run()
