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
