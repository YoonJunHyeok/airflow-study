## What is Airflow

- Airflow is an open source platform to programmatically author, schedule and monitor workflows

### Core Components

- Web Server: serves UI.
- Scheduler: Heart of Airflow, In charge of scheduling your task and your data pipelines.
- MetaDatabase: metadata related to tasks, data pipelines and so on will be stored
- Triggerer: Manage deferrable operators, which is task that has ability to suspend itself and resume itself
- Executor: Class defining how tasks should be executed
- Worker: Process or machine where the tasks are executed

Task is an Operator
There are Action, Transfer, Sensor, Deferrable Operator.

## How Airflow works
