"""
Weekly Outreach Automation Pipeline DAG.
Schedule: Every Sunday at 4 AM UTC.

Steps:
  1. Pull latest APhA member list (exclude from prospects)
  2. Fetch new NPI records and upsert to prospects
  3. Run ICP scoring on all unscored prospects
  4. Queue top-scoring prospects into active campaigns
  5. Trigger email generation for newly queued prospects
  6. Generate weekly performance report
"""
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    HAS_AIRFLOW = True
except ImportError:
    HAS_AIRFLOW = False

from datetime import datetime, timedelta

if HAS_AIRFLOW:
    default_args = {
        "owner": "techjays",
        "depends_on_past": False,
        "email_on_failure": True,
        "email": ["ai-team@techjays.com"],
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    }

    with DAG(
        dag_id="weekly_outreach_automation",
        default_args=default_args,
        description="Weekly AI outreach pipeline for APhA non-member acquisition",
        schedule_interval="0 4 * * 0",
        start_date=datetime(2026, 1, 1),
        catchup=False,
        tags=["apha", "outreach", "acquisition"],
    ) as dag:

        def task_refresh_member_exclusions(**ctx):
            from db.session import SessionLocal
            from pipeline.connectors.crm_connector import pull_member_emails
            from pipeline.npi_importer import crossref_with_member_list
            db = SessionLocal()
            try:
                emails = pull_member_emails()
                excluded = crossref_with_member_list(db, emails)
                ctx["ti"].xcom_push(key="excluded_count", value=excluded)
            finally:
                db.close()

        def task_import_npi(**ctx):
            from db.session import SessionLocal
            from pipeline.npi_importer import run_npi_import
            db = SessionLocal()
            try:
                result = run_npi_import(db, use_mock=True)
                ctx["ti"].xcom_push(key="import_result", value=result)
            finally:
                db.close()

        def task_score_prospects(**ctx):
            from db.session import SessionLocal
            from ml.icp_score import run_icp_scoring
            db = SessionLocal()
            try:
                result = run_icp_scoring(db)
                ctx["ti"].xcom_push(key="scoring_result", value=result)
            finally:
                db.close()

        def task_queue_prospects(**ctx):
            from db.session import SessionLocal
            from db.models.prospect import Prospect
            from db.models.campaign import Campaign
            from delivery.tasks import generate_sequence_for_prospect
            from utils.config import get_settings

            settings = get_settings()
            db = SessionLocal()
            try:
                active_campaign = db.query(Campaign).filter(
                    Campaign.status == "active",
                    Campaign.is_dry_run == False,
                ).first()

                if not active_campaign:
                    active_campaign = db.query(Campaign).filter(
                        Campaign.status == "active"
                    ).first()

                if not active_campaign:
                    print("No active campaign found -- skipping queue step")
                    return

                top_prospects = db.query(Prospect).filter(
                    Prospect.status == "scored",
                    Prospect.icp_score >= settings.min_icp_score_to_contact,
                    Prospect.email != None,
                    Prospect.do_not_contact == False,
                ).order_by(Prospect.icp_score.desc()).limit(50).all()

                queued = 0
                for p in top_prospects:
                    generate_sequence_for_prospect.delay(
                        str(p.id), str(active_campaign.id)
                    )
                    queued += 1

                print(f"Queued {queued} prospects for campaign {active_campaign.id}")
                ctx["ti"].xcom_push(key="queued_count", value=queued)
            finally:
                db.close()

        def task_report(**ctx):
            import_r = ctx["ti"].xcom_pull(key="import_result", task_ids="import_npi")
            score_r = ctx["ti"].xcom_pull(key="scoring_result", task_ids="score_prospects")
            queued = ctx["ti"].xcom_pull(key="queued_count", task_ids="queue_prospects")
            print(f"[WEEKLY REPORT] Import: {import_r} | Scoring: {score_r} | Queued: {queued}")

        refresh_members = PythonOperator(task_id="refresh_members", python_callable=task_refresh_member_exclusions)
        import_npi = PythonOperator(task_id="import_npi", python_callable=task_import_npi)
        score_prospects = PythonOperator(task_id="score_prospects", python_callable=task_score_prospects)
        queue_prospects = PythonOperator(task_id="queue_prospects", python_callable=task_queue_prospects)
        report = PythonOperator(task_id="report", python_callable=task_report)

        refresh_members >> import_npi >> score_prospects >> queue_prospects >> report
