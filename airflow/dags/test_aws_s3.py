
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


BUCKET_NAME = "spotify-data-engineering-334116998170-us-east-2"


def list_s3_directories():
    s3_hook = S3Hook(aws_conn_id="aws_spotify")

    directories = s3_hook.list_prefixes(
        bucket_name=BUCKET_NAME,
        prefix="bronze/",
        delimiter="/"
    )

    print(f"Diretórios encontrados no bucket {BUCKET_NAME}:")

    for directory in directories:
        print(directory)


with DAG(
    dag_id="test_aws_s3",
    description="Test AWS S3 connection through Airflow",
    start_date=datetime(2026, 11, 10),
    schedule=None,
    catchup=False,
    tags=["aws", "s3", "test"],
) as dag:

    list_directories = PythonOperator(
        task_id="list_s3_directories",
        python_callable=list_s3_directories,
    )
