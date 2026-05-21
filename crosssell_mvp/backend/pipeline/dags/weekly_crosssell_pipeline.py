"""
Weekly Cross-Sell Pipeline DAG.
Schedule: Every Tuesday at 7 AM UTC (day after churn scoring on Monday).
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "techjays",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["ai-team@techjays.com"],
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="weekly_crosssell_engine",
    default_args=default_args,
    description="Weekly AI cross-sell scoring and nudge delivery for APhA members",
    schedule_interval="0 7 * * 2",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["apha", "crosssell", "ml"],
) as dag:

    def task_pull_usage(**ctx):
        from backend.db.session import SessionLocal
        from backend.pipeline.connectors.usage_connector import pull_all_product_usage
        db = SessionLocal()
        try:
            pull_all_product_usage(db)
        finally:
            db.close()

    def task_run_scoring(**ctx):
        from backend.db.session import SessionLocal
        from backend.ml.score import run_batch_scoring
        db = SessionLocal()
        try:
            summary = run_batch_scoring(db)
            ctx["ti"].xcom_push(key="scoring_summary", value=summary)
        finally:
            db.close()

    def task_send_nudges(**ctx):
        from backend.nudge_engine.tasks import send_batch_email_nudges
        send_batch_email_nudges.delay()

    def task_report(**ctx):
        summary = ctx["ti"].xcom_pull(key="scoring_summary", task_ids="run_scoring")
        print(f"[REPORT] Cross-sell scoring complete: {summary}")

    pull_usage = PythonOperator(task_id="pull_usage", python_callable=task_pull_usage)
    run_scoring = PythonOperator(task_id="run_scoring", python_callable=task_run_scoring)
    send_nudges = PythonOperator(task_id="send_nudges", python_callable=task_send_nudges)
    report = PythonOperator(task_id="report", python_callable=task_report)

    pull_usage >> run_scoring >> send_nudges >> report
