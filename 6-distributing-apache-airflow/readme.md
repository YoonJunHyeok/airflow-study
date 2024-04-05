# Section 6

## How a task gets executed ?

1. When a DAG is scheduled, each task has a record with its status(queued, scheduled, running, success, failed) stored into the metadata DB.
2. The Scheduler periodically reads from the metedata DB to check if there is any task to run.
3. The Executor gets the tasks to run from its internal queue and specify how to execute it (Sequential, Local, Celery, K8s)

## Sequential Executor

- Most basic executor
- Only run one task at a time
- Only executor to use with SQLite
- Default configuration
- Should no use in production

## Local Executor

- Run multipel tasks in parallel
- Base on the python module: multiprocessing
- Spawn processes to execute tasks
- Easy to set up
- Resource light
- Vertical Scaling
- Single point of failure
- SQLite doesn't supprot concurrent, we need other database such as PostgreSQL, MySQl, Oracle.

### parallelism & dag_concurrency

- parallelism 값만큼 task가 동시에 수행될 수 있다.
- dag_concurrency 값만큼 하나의 DAGRun 내에서 Task들이 동시에 수행될 수 있다.
- parallelism 3이고, dag_concurrency가 2이고 하나의 DAG내에서 3개의 task들이 동시에 수행될 수 있다고 할 때, dag_concurrency 값에 의해 2개만 병렬적으로 수행된다.

### max_active_runs_per_dag

- 각각의 DAG 별로 생성할 수 있는 최대 DAGRun의 개수

### Ad Hoc Queries with the metadata database

- Connection

```yaml
Conn Id: postgres_1
Conn Type: Postgres
Host: postgres # Airflow와 Metadata DB를 docker contianer 안에서 실행 중이기에, host는 docker-compose 내 service이름이다.
Schema: airflow
Login: airflow
password: airflow
```

#### Queries

- At Data Profiling - Ad Hoc Queries
- List the Airflow tables in PostgreSQL

```sql
SELECT *
FROM pg_catalog.pg_tables
WHERE schemaname != 'pg_catalog'
    AND schemaname != 'information_schema'
    AND tableowner = 'airflow';
```

- List the task instances

```sql
SELECT * FROM task_instance;
```

- List the dag runs

```sql
SELECT * FROM dag_run;
```

- Get total completed task count

```sql
SELECT COUNT(1)
FROM task_instance
WHERE state IS NOT NULL
    AND state NOT IN ('scheduled', 'queued');
```

#### security

- begin able to extract data directly from Airflow is insecure and not desirable
- can turn off this feature by changing the parameter `secure_mode`
- 2.0에서는 True가 default 값.

## Celery Executor

- Scale out Apache Airflow
- Backed by Celery: Asynchronous Distributed Task Queue
- Distribute tasks among worker nodes
- `airflow worker`: Create a worker to execute tasks
- Horizontal Scaling
- High Availability: If one worker goes down, Airflow can still schedule tasks
- Need a message broker: RabbitMQ/Redis
- Can set different queues

### Adding new worker nodes with the Celery Executor Manually

1. node 생성

```bash
docker run --network 6-distributing-apache-airflow_default --expose 8793 -v /Users/junhyeok/Documents/Udemy/Airflow_The_Hands-On_Guide/airflow-study/6-distributing-apache-airflow/mnt/airflow/dags:/usr/local/airflow/dags -v /Users/junhyeok/Documents/Udemy/Airflow_The_Hands-On_Guide/airflow-study/6-distributing-apache-airflow/mnt/airflow/airflow.cfg:/usr/local/airflow/airflow.cfg -dt python:3.7
```

2.

```bash
docker exec -it {{container id}} /bin/bash
```

```bash
export AIRFLOW_HOME=/usr/local/airflow/

useradd -ms /bin/bash -d $AIRFLOW_HOME airflow

pip install "apache-airflow[celery, crypto, postgres, redis]==1.10.12"
```

```bash
pip install MarkupSafe==1.1.1
pip install WTForms==2.3.3
pip install werkzeug==0.16.0
pip install sqlalchemy==1.3.23
```

downgrade these because of error

```bash
airflow initdb
```

```bash
chown -R airflow: $AIRFLOW_HOME

su - airflow
```

#### change metadata DB from sqlite to postgres

- At airflow.cfg

```yaml
sql_alchemy_conn = postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
executor = CeleryExecutor
result_backend = db+postgresql://airflow:airflow@postgres:5432/airflow
broker_url = redis://:redispass@redis:6379/1
```

으로 변경

후에

```bash
export AIRFLOW_HOME=/usr/local/airflow/
```

#### Add new node to the cluster by starting a celery worker

```bash
airflow worker
```

#### 주의사항

- spark나 hive 쓴다면 새로운 worker에도 dependency들 설치해줘야 함.

### Adding new worker nodes with the Celery Executor With docker-compose

```bash
docker-compose -f docker-compose-CeleryExecutor.yml up -d --scale worker=3
```

### Sending tasks to a specific worker with queues

- at docker-compose yaml

```yaml
services:
  worker:
    command: worker -q worker_ssd,worker_cpu,worker_spark,default
```

위 4개의 이름의 queue들을 생성한다. (default는 기존에 사용되던 queue인데, option을 주는 것으로 default가 생성이 안 돼서 추가해준다.)

- at operator from dag

```
queue='worker_ssd'
```

를 operator에 추가해준다.

### Drawbacks of the Celery Executor

- Need to set up tier applicatioins(ex. RabbitMQ, Redis, Celery, Flower)
- Deal with missing dependencies
- Wasting resources: airflow workers stay idle when no workload
- Worker nodes are not as resilient(회복력 있는) as you think

## Kubernetes Executor

- Runs your tasks on K8s
- One task = One Pod
- Task-level pod configuration
- Expands and shrinks cluster according to the workload
- Pods run to completion
- Scheduler subscribes to K8s event stream
- DAG distribution
  - Git clonew with init-container for each pod
  - Mount volume with DAGs
  - Build image with the DAG codes
