"""
Weekly Churn Prediction Pipeline DAG.
Schedule: Every Monday at 6 AM UTC.

Steps:
  1. Pull latest data from CRM, LMS, email platform (mocked for MVP)
  2. Update member feature table in PostgreSQL
  3. Run batch scoring on all active members
  4. Generate alerts for high/critical members
  5. Send summary report
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from apps.churn.pipeline.connectors.crm_connector import pull_crm_data
from apps.churn.pipeline.connectors.lms_connector import pull_lms_data
from apps.churn.pipeline.connectors.email_connector import pull_email_data
from apps.churn.db.session import SessionLocal
from apps.churn.ml.score import run_batch_scoring
from apps.churn.utils.logger import get_logger

logger = get_logger("weekly_churn_dag")

default_args = {
    "owner": "techjays",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["ai-team@techjays.com"],
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="weekly_churn_prediction",
    default_args=default_args,
    description="Weekly member churn prediction pipeline for APhA",
    schedule_interval="0 6 * * 1",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["apha", "churn", "ml"],
) as dag:

    def task_pull_crm(**context):
        logger.info("Pulling CRM data...")
        db = SessionLocal()
        try:
            pull_crm_data(db)
        finally:
            db.close()

    def task_pull_lms(**context):
        logger.info("Pulling LMS/CPE data...")
        db = SessionLocal()
        try:
            pull_lms_data(db)
        finally:
            db.close()

    def task_pull_email(**context):
        logger.info("Pulling email engagement data...")
        db = SessionLocal()
        try:
            pull_email_data(db)
        finally:
            db.close()

    def task_run_scoring(**context):
        logger.info("Running batch churn scoring...")
        db = SessionLocal()
        try:
            summary = run_batch_scoring(db)
            context["ti"].xcom_push(key="scoring_summary", value=summary)
            logger.info(f"Scoring summary: {summary}")
        finally:
            db.close()

    def task_send_report(**context):
        summary = context["ti"].xcom_pull(key="scoring_summary", task_ids="run_scoring")
        logger.info(f"[REPORT] Weekly churn scoring complete:\n{summary}")
        # TODO: Integrate with APhA's email platform to send report

    pull_crm = PythonOperator(task_id="pull_crm", python_callable=task_pull_crm)
    pull_lms = PythonOperator(task_id="pull_lms", python_callable=task_pull_lms)
    pull_email = PythonOperator(task_id="pull_email", python_callable=task_pull_email)
    run_scoring = PythonOperator(task_id="run_scoring", python_callable=task_run_scoring)
    send_report = PythonOperator(task_id="send_report", python_callable=task_send_report)

    [pull_crm, pull_lms, pull_email] >> run_scoring >> send_report
