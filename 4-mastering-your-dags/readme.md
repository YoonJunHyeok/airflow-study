# Airflow Parameters

## start_date and schedule_interval

- start_date: The date from which tasks of your DAG can be scheduled and triggered.
- schedule_interval: The interval of time from the min(start_date) at which your DAG should be triggered.

> The DAG starts being scheduled from the **start_date** and will be triggered after every **schedule_interval**

> execution_date is **NOT** the date when the DAG has been run.
> Corresponds to the **beginning of the processed period** (start_date - schedule_interval)

> A DAG with a start_date at 10 AM and a schedule_interval of 10 minutes, gets **really** executed at 10:10 for data coming from 10 AM.
>
> > **AFTER** start_Date + schedule_interval at the **END** of the period.
> >
> > > But this DagRun has execution_date of 10 AM.

### How to define the start_date

- With python datetime object.
- If it's future, scheduler will wait until that date.
- Else if it's past, scheduler can be runned right away. But should be careful about catchup parameter. It is False by default.
- Reconmmend to use static value, not dynamic values as datetime.now or timedelta.
- Also, set it globally at the DAG level through default_args.

### How to define schedule_interval

- Either with

  > cron expressions (ex: 0 \* \* \* \*) => recommended

  > Timedelta objects (ex: datetime.timedelta(days=1))

| Preset   | Meaning                                                    | Cron Expression |
| -------- | ---------------------------------------------------------- | --------------- |
| None     | Don't Schedule. Manually triggered                         | x               |
| @once    | Schedule once and only once                                | x               |
| @hourly  | Run once an hour at the beginning of the hour              | 0 \* \* \* \*   |
| @daily   | Run once a day at midnight                                 | 0 0 \* \* \*    |
| @weekly  | Run once a week at midnight on sunday morning              | 0 0 \* \* 0     |
| @monthly | Run once a month at midnight of the first day of the month | 0 0 1 \* \*     |
| @yearly  | Run once a year at midnight of January 1st                 | 0 0 1 1 \*      |

### end_date

- The date at which my DAG/Task should stop being scheduled
- Set to None by default

## Backfill and Catchip

### What is DagRun

- The scheduler creates a DagRun object.
- Describes an instance of a given DAG in time.
- Contains tasks to execute
- Atomic(It won't share resources with other DagRun)
- Idempotent(It can be restarted again and again and it will always produce same result.)

### Catchup Process

- It is set to True by default
- 중간에 DAG가 trigger false 됐다가 나중에 true되면 그 동안에 실행됐어야 할 DagRun 실행할지 말지.

```bash
airflow backfill -s 2024-03-02 -e 2024-04-02 --rerun_failed_tasks -B backfill
```

CatchUP 옵션이 False여도 명령어로 실행할 수 있다.

## Timezone

- Should always use **aware datetime object**, which means should set timezone info of python datetime.datetime() by importing airflow.timezone.
- UTC is default. We update 'default_timezone' in airflow.cfg.
- Airflow uses the pendulum python library to deal with timezone.

## Dependecy between current DAGRun and previous DAGRun

### depends_on_past

- defined at task level(task마다 할 수도 있고, default args로 DAG 내에 모든 task에 할당할 수도 있다.)
- If previous **task instance** failed(upstream task가 아니라, 이전 DAGRun의 같은 task), the current task is not executed
- Consequently, the current task has **no status**
- First task instance with start_date allowed to run

### wait_for_downstream

- Defined at task level(same as depends_on_past)
- An instance of task X will wait for tasks immediately downstream of the previous instance of task X to finish successfully before it runs.
- 이전 DAGRun에서 어떤 Task의 직후 하위 Task가 아직 끝나지 않았다면, 그 task가 끝날 때 까지 기다린 후에, 현재 DAGRun의 task 실행한다.

## How to structure DAG folder

### First way: zip

- Create a zip file packing DAGs and its unpacked extra files
- The DAGs must be in the root of the zip file
- Airflow will scan and load the zip file for DAGs
- If module dependencies needed, use virtualenv and pip

### Second way: DagBag

- A DagBag is a collection of DAGs, parsed out of a folder tree and has a high level configuration settings.
- Make easier to run distinct environemnts (dev/staging/prod)
- One system can run multiple independent settings set
- Allow to add new DAG folders by creating a script in the default DAGs folder
- If a DAG is loaded with a new DagBag and is broken
  - Errors are **not displayed** from the UI
  - Can't use the command 'airflow list_dags'
  - Sill able to see the errors from the web server logs
- 여러 파일에 DAG를 둘 수 있다는 장점

### .airflowignore

- Airflow가 무시한 파일아나 경로 적어둠.
- 주로 DAGs 폴더에 위치한다.

### \_\_init\_\_.py

- 파이썬이 이 파일이 있는 폴더를 모듈로 인식하도록 함.

### To package

1. zip으로

```bash
zip -rm package_dag.zip packaged_dag.py functions/
```

2. DagBag으로

'add_dagbags.py' script 확인.

## How to deal with filures in DAGs

### DAG failure detections

- DAG level

  - dagrun_timeout
  - sla_miss_callback
  - on_failure_callback
  - on_success_callback

- Task level
  - email
  - email_on_failure
  - email_on_retry
    - Have to configure smtp settings in airflow.cfg
  - retires
  - retry_delay
  - retry_exponential_backoff
  - max_retry_delay
  - execution_timeout
  - on_failure_callback
  - on_success_callback
  - on_retry_callback

## How to text DAGs

### Unit Test

- 여기서는 Pytest 사용

#### 5 Categories

- DAG Validation Tests
- DAG/Pipeline Definition Tests
- Unit Tests
- Integration Tests
- End to End Pipeline Tests

Airflow Commands

```bash
airflow run
# Run a single task instance

airflow list_dags
# List all the DAGs

airflow dag_state
# Get the status of a DAG run

airflow task_state
# Get the status of a Task instance

airflow test
# Test a task instance without checking dependencies or recording its state in the db
```
