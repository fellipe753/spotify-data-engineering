
from datetime import datetime
from pathlib import Path
import subprocess
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


# Configuration
BUCKET_NAME = "spotify-data-engineering-334116998170-us-east-2"
AWS_CONN_ID = "aws_spotify"

PROJECT_DIR = Path("/opt/airflow")
DATA_DIR = PROJECT_DIR / "data"

JSON_FILES = [
    "artists/artists.json",
    "albums/albums.json",
    "tracks/tracks.json",
]

CSV_FILES = [
    "artists.csv",
    "albums.csv",
    "tracks.csv",
]


def extract_spotify_data():

    script_path = PROJECT_DIR / "src/spotify/extract.py"

    print("Starting Spotify extraction...")

    subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_DIR),
        check=True
    )

    print("Spotify extraction completed successfully.")


def upload_json_to_s3():

    s3_hook = S3Hook(aws_conn_id=AWS_CONN_ID)

    for file_name in JSON_FILES:

        local_path = DATA_DIR / "bronze" / file_name
        s3_key = f"bronze/{file_name}"

        if not local_path.exists():
            raise FileNotFoundError(
                f"JSON file not found: {local_path}"
            )

        s3_hook.load_file(
            filename=str(local_path),
            key=s3_key,
            bucket_name=BUCKET_NAME,
            replace=True
        )

        print(f"Uploaded JSON: {s3_key}")


def upload_csv_to_s3():

    s3_hook = S3Hook(aws_conn_id=AWS_CONN_ID)

    for file_name in CSV_FILES:

        local_path = DATA_DIR / "processed" / file_name
        s3_key = f"silver/{file_name}"

        if not local_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {local_path}"
            )

        s3_hook.load_file(
            filename=str(local_path),
            key=s3_key,
            bucket_name=BUCKET_NAME,
            replace=True
        )

        print(f"Uploaded CSV: {s3_key}")


with DAG(
    dag_id="spotify_data_pipeline",
    description="Extract Spotify data and upload JSON and CSV files to AWS S3",
    start_date=datetime(2026, 11, 20),
    schedule=None,
    catchup=False,
    tags=["spotify", "aws", "s3", "data-engineering"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract_spotify_data",
        python_callable=extract_spotify_data,
    )

    upload_json_task = PythonOperator(
        task_id="upload_json_to_s3",
        python_callable=upload_json_to_s3,
    )

    upload_csv_task = PythonOperator(
        task_id="upload_csv_to_s3",
        python_callable=upload_csv_to_s3,
    )

    extract_task >> [upload_json_task, upload_csv_task]
