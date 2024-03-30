# Usage Guide

To Start and run Airflow: start.sh

To Restart Airflow: restart.sh

To Stop Airflow: stop.sh

To remove everything(metadata): reset.sh

## Docker Reminder - Use Docker Compose for multi-container.

1. Docker file
2. Docker image
3. Docker Compose file(yaml file) descibing the services that we wnat to run for our app. (ex. webserver, scheduler, database)
   / All services are single application / All Containers will share the same network. So, they are able to communicate with each other.

## Flow Chart of the Forex Data Pipeline

1. Check availability of forex rates (V)
2. Check availability of the file having currencies to watch
3. Download forex rates with Python
4. Save the forex rates in HDFS(Hadoop Distributed File System)
5. Create a Hive table to store forex rates from the HDFS
6. Process forex rates with Spark
7. Send and Email Notification
8. Send a Slack Notification

## Operators

1. Action Operator: to execute something. ex. python operator, bash operator
2. Transfer Operator: to transfer data from a source to a destination. ex. presto to mysql operator, mysql to gcs operator
3. Censor Operator: to wait for something to happen before moving to the next tasks / For example, we want to wait for a file to land at a specific location in our file system => file censor operator

## Additional Things

```bash
export DOCKER_DEFAULT_PLATFORM=linux/amd64
```

- Apple 칩 이슈로 위의 명령어를 실행해야 한다.
- 클라우드 서버에 맞춰서 이미지를 빌드한 것이기에 로컬에서는 실행되지 않는다.

```bash
docker exec -it ${container_id} /bin/dash
```

run bash session in airflow container
"before running DAG, we should test task"

```bash
airflow tasks test ${dag_id} ${task_id} ${execution_date}
```

http://localhost:32762/ 으로 hue 접속

### Airflow Admin Connection 추가

1. forex_api

- Conn id: forex_api
- Conn type: HTTP
- Port: https://gist.github.com/

2. forex_path

- Conn id: forex path
- Conn type: File(path)
- Extra: {"path": "/opt/airflow/dags/files"}

3. hive_conn

- Conn id: hive_conn
- Conn type: hive server 2 thrift
- Host: hive-server
- Login: hive
- Password: hive
- Port: 10000

4. spark_conn

- Conn id: spark_conn
- Conn type: Spark
- Host: spark://spark-master
- Port: 7077

5. slack_conn

- Conn id: slack_conn
- Conn type: HTTP
- Password: {webhook URL from slack API}

### For Full Clean Up

1. Delete forex_rates.json at opt(mnt)/airflow/dags/files
2. Drop table forex_rates from HIVE by HUE
3. Run Following command to delete internal storage to prevent duplicates

```bash
hdfs dfs -rm -r -f /user/hive/warehouse/forex_rates
```
