from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.apache.hive.operators.hive import HiveOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

from datetime import datetime, timedelta

import csv
import json
import requests

default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "admin@localhost.com",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

'''
Download forex rates according to the currencies we want to watch
described in the file forex_currencies.csv
'''
@task(task_id="download_rates")
def download_rates():
    BASE_URL = "https://gist.githubusercontent.com/marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b/raw/"
    ENDPOINTS = {
        'USD': 'api_forex_exchange_usd.json',
        'EUR': 'api_forex_exchange_eur.json'
    }
    with open('/opt/airflow/dags/files/forex_currencies.csv') as forex_currencies:
        reader = csv.DictReader(forex_currencies, delimiter=';')
        for idx, row in enumerate(reader):
            base = row['base']
            with_pairs = row['with_pairs'].split(' ')
            indata = requests.get(f"{BASE_URL}{ENDPOINTS[base]}").json()
            outdata = {'base': base, 'rates': {}, 'last_update': indata['date']}
            for pair in with_pairs:
                outdata['rates'][pair] = indata['rates'][pair]
            with open('/opt/airflow/dags/files/forex_rates.json', 'a') as outfile:
                json.dump(outdata, outfile)
                outfile.write('\n')

def _get_message() -> str:
    return "Hi from forex_data_pipeline"

with DAG(
    "forex_data_pipeline", 
    start_date=datetime(2024, 1 ,1), 
    schedule_interval="@daily", 
    catchup=False,
    default_args=default_args, 
) as dag:
    # check availability of forex rates
    is_forex_rates_available = HttpSensor(
        task_id="is_forex_rates_available",
        http_conn_id="forex_api",
        endpoint="marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b",
        response_check=lambda response: "rates" in response.text,
        poke_interval=5,
        timeout=20
    )

    # check availability of the file having currencies to watch
    is_forex_currencies_file_available = FileSensor(
        task_id="is_forex_currencies_file_available",
        fs_conn_id="forex_path",
        filepath="forex_currencies.csv",
        poke_interval=5,
        timeout=20
    )

    # donwload forex rates with python to local file system
    # download_rates = PythonOperator(
    #     task_id="download_rates",
    #     python_callable=download_rates
    # )
    # without @task decorator
    download_rates = download_rates()

    # save the forex rates in HDFS
    save_rates = BashOperator(
        task_id="save_rates",
        bash_command="""
            hdfs dfs -mkdir -p /forex && \
            hdfs dfs -put -f $AIRFLOW_HOME/dags/files/forex_rates.json /forex
        """
    )

    # create a Hive table to store forex rates from the HDFS
    # hql is hibernate query language.
    creat_forex_rates_table = HiveOperator(
        task_id="creat_forex_rates_table",
        hive_cli_conn_id="hive_conn",
        hql="""
            CREATE EXTERNAL TABLE IF NOT EXISTS forex_rates(
                base STRING,
                last_update DATE,
                eur DOUBLE,
                usd DOUBLE,
                nzd DOUBLE,
                gbp DOUBLE,
                jpy DOUBLE,
                cad DOUBLE
                )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
        """
    )

    # Process forex rates with Spark
    # Airflow로 대용량 데이터 작업을 하지 않는다. 대신 그 작업을 하는 Spark를 Trigger한다.
    # Airflow는 Processing framework가 아니라, Orchestrator이다.
    # application은 실행할 path of script이다.
    process_forex_rates = SparkSubmitOperator(
        task_id="process_forex_rates",
        conn_id="spark_conn",
        application="/opt/airflow/dags/scripts/forex_processing.py",
        verbose=False
    )

    # Send an Email Notification
    send_email_notification = EmailOperator(
        task_id="send_email_notification",
        to="junhy1607@naver.com",
        subject="forex_data_pipeline",
        html_content="<h3>forex_data_pipeline</h3>"
    )

    # Send a Slack Notification
    send_slack_notification = SlackWebhookOperator(
        task_id="send_slack_notification",
        http_conn_id="slack_conn",
        message=_get_message(),
        channel="#monitoring"
    )

    # Add dependencies between Tasks
    is_forex_rates_available >> is_forex_currencies_file_available >> download_rates >> save_rates 
    save_rates >> creat_forex_rates_table >> process_forex_rates 
    process_forex_rates >> [send_email_notification, send_slack_notification]