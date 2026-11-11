
FROM apache/airflow:3.4.0-python3.12

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir \
    "apache-airflow==3.4.0" \
    -r /requirements.txt
