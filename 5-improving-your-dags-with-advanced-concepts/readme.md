# Section 5

```bash
docker-compose -f docker-compose-CeleryExecutor.yml up -d

docker-compose -f docker-compose-CeleryExecutor.yml down
```

## Minimising Repetitive Patterns With SubDAGs

- The main DAG manages all the subDAGs as normal tasks
- Airflow UI only shows the main DAG
- SubDAGs must be scheduled the same as their parent DAG
- Use SubDAGs with caution

  - DeadLock can happen: subdag도 하나의 instance로 취급되는데, subdag가 4개가 있고, worker가 4개 있는 상황에서 celery로 실행한 경우에 각각의 subdag가 worker를 하나씩 잡으므로, subdag들 안에 task들이 실행될 worker가 없어서 deadlock이 발생한다.
  - SubDagoOperator의 Queue를 추가하여 해결할 수 있다.

- subDAG must return dag to mainDAG
- subdag operator uses sequential executor by default(even if main dag's executor is celery)

## Making different paths in DAGs with Branching

### Branching

- Mechanism allowing DAG to choose between different paths according to the result of a specific task(Usually Upstream Task)
- BranchPythonOperator that returns task_id of the task to execute next. Others will be skipped
- depends_on_past can be used for branching

## Trigger rules for tasks

- default로는 바로 위 parent들이 succeeded일 때만 exectue
- trigger_rule로 조건 선택.
  - all_success / all_failed
  - all_done
    - upstream이 running일 때 wait
  - one_success / one_failed
    - 하나라도 조건 만족하면, running인 parent 있어도 running 된다.
  - none_failed
    - failed나 upstream_failed만 아니면
  - none_skipped
- **direct** parent task들에 따른 상태이다.

## Avoid Hard Coding

- Idempotency
  - Date

### Variables

- Values stored in the metadata DB
- Three columns
  - Key
  - Value
  - Is encrypted
- Can create custom variable from airflow UI - Admin - Variables

### Templating

- Replace placeholders by values at runtime
- Based on Jinja Templating which is template engine for python
- Placeholder: {{}}

### Macros

- Predefined variables
- {{ds}}: execution date of current DagRun
- {{prev_ds}}
- {{next_ds}}
- {{dag}}
- {{params}}
- {{var.value.key_of_your_var}}

## How to share data between tasks with XCOM

- Allow multipe tasks to exchange messages between them.
- Key, Value, Timestamp로 구성되어 있다.
  - task_id와 dag_id도 있다.
- Value가 너무 크면 안된다.

### Metadata DB에 넣는 방법

1. xcom_push
2. return at PythonOperator

- key는 자동으로 "return_value"

### 불러오는 방법

- xcom_pull

  1. xcom_pull(key=ret)
  2. xcom_pull(key=None, task_ids["Task1"])

  - list로 넘겨서 여러 task들의 return value 부를 수 있다.
  - 그러기 위해서는 key가 None으로 설정되어 있어야 한다.

- XCOM 값들을 자동으로 삭제해주지 않아서, 용량 부족이 일어나지 않도록 잘 관리해야 한다.

### XCOM with Large Value

- 가능은 하지만 권장되지 않는다.
- Spark와 같은 데이터 프로세싱 프레임워크를 사용해라.

## TriggerDagRunOperator

- Start a DAG from another DAG base on conditions
- Controller DAG에서 target DAG를 실행.
- Controller does not wait for target to finish
- Controller and target are independent
- Target의 trigger가 on이어야 한다.
- No visualisation from the controller neither history
- Both DAGs must be scheduled
- Target DAG schedule interval = None 권장

## Dependencies between DAGs with the ExternalTaskSensor

- Allows to wait for an external task (in another dag) to complete
- Should keep the same schedule_interval between DAGs
- Or use execution_delta **or** executio_date_fn parameters
- Using both ExternalTaskSensor and TriggerDagRunOperator usually lead to get the sensor stuck
- Mode "poke" used by default
  - "reschedule" if needed

## Troubleshooting of this section

1. import error

```
ImportError: libpq.so.5: cannot open shared object file: No such file or directory
```

> docker-compose up 후에 webserver service에서 위와 같은 에러가 뜨면서 시작되지 않았다.
> Dockerfile의 apt-get install 부분에서 libpq5을 추가하는 것으로 해결되었다.
