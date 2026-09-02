from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "mlops-team",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="rideshare_surge_pricing_pipeline",
    default_args=default_args,
    description="End-to-end MLOps pipeline for dynamic surge pricing",
    schedule="*/15 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["mlops", "rideshare", "surge-pricing"],
) as dag:

    generate_data = BashOperator(
        task_id="ingest_spatial_temporal_data",
        bash_command="python /opt/project/scripts/generate_data.py",
    )

    validate = BashOperator(
        task_id="validate_data",
        bash_command="python /opt/project/scripts/validate_data.py",
    )

    features = BashOperator(
        task_id="feature_engineering_and_feature_store_update",
        bash_command="python /opt/project/scripts/feature_engineering.py",
    )

    train = BashOperator(
        task_id="train_model_and_track_with_wandb",
        bash_command="python /opt/project/scripts/train.py",
    )

    validate_model = BashOperator(
        task_id="validate_model",
        bash_command="python /opt/project/scripts/validate_model.py",
    )

    drift_check = BashOperator(
        task_id="monitor_drift",
        bash_command="python /opt/project/monitoring/check_drift.py",
    )

    generate_data >> validate >> features >> train >> validate_model >> drift_check
