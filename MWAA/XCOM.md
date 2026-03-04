Airflow MWAA Glue Job with XCom Flag

This document explains how to run an AWS Glue job in MWAA (Managed Workflows for Apache Airflow), capture its response, and use XComs to pass a file presence flag to downstream tasks such as an SSHOperator.

🧩 GlueJobOperator Basics

Airflow provides the GlueJobOperator to trigger AWS Glue jobs.

When executed, it returns a JobRunId, which is automatically stored in XCom.

You can use this JobRunId to query Glue for job status or custom metadata.

    from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

    glue_task = GlueJobOperator(
        task_id="run_glue_job",
        job_name="my_glue_job",
        script_location="s3://my-bucket/scripts/my_script.py",
        region_name="us-east-1",
        iam_role_name="my-glue-role",
        dag=dag
    )

⚙️ Checking Glue Job Status

Use a PythonOperator with boto3 to query Glue for the job’s final state and push a flag into XCom.

    import boto3
    from airflow.operators.python import PythonOperator

    def check_glue_status(**kwargs):
        job_run_id = kwargs['ti'].xcom_pull(task_ids='run_glue_job')
        glue = boto3.client('glue', region_name='us-east-1')

        response = glue.get_job_run(JobName='my_glue_job', RunId=job_run_id)
        state = response['JobRun']['JobRunState']

        # Example: push a flag if file exists logic is inside Glue
        file_exists = (state == 'SUCCEEDED')
        kwargs['ti'].xcom_push(key='file_presence', value=file_exists)

    check_task = PythonOperator(
        task_id='check_glue_status',
        python_callable=check_glue_status,
        provide_context=True,
        dag=dag
    )

📡 Using XCom Flag in SSHOperator

The downstream SSHOperator can pull the flag and conditionally execute commands.

    from airflow.providers.ssh.operators.ssh import SSHOperator

    ssh_task = SSHOperator(
        task_id='ssh_task',
        ssh_conn_id='my_ssh_connection',
        command="""
        {% if ti.xcom_pull(task_ids='check_glue_status', key='file_presence') %}
            echo "File exists, running command..."
        # your command here
        {% else %}
            echo "File not found, skipping..."
        {% endif %}
        """,
        dag=dag
    )

🔑 Key Points

GlueJobOperator → JobRunId (stored in XCom).

PythonOperator → boto3.get_job_run() to check status or custom metadata.

Push flag into XCom for downstream tasks.

SSHOperator → Jinja template to conditionally run commands based on flag.

🚀 Workflow Summary

Trigger Glue job with GlueJobOperator.

Use PythonOperator to query Glue job status and push a file presence flag into XCom.

Downstream SSHOperator pulls the flag and executes commands conditionally.

This pattern makes your MWAA DAGs dynamic and data-driven, enabling Glue jobs to influence subsequent tasks.

📖 Additional Notes

Monitoring Glue Jobs

Use CloudWatch Logs to monitor Glue job execution details.

Airflow’s UI shows task status, but Glue logs provide deeper insights.

Error Handling

You can add retries to the GlueJobOperator.

In the PythonOperator, handle exceptions from boto3 gracefully:

try:
    response = glue.get_job_run(JobName='my_glue_job', RunId=job_run_id)
except Exception as e:
    kwargs['ti'].xcom_push(key='file_presence', value=False)
    raise e

Alternatives to XCom

For larger data, store results in S3 or a database instead of XCom.

XCom is best for small flags, IDs, or metadata.

Scaling Considerations

MWAA with CeleryExecutor allows distributed task execution.

Ensure your Glue job IAM role has correct permissions for S3, logs, and any other resources.

Example DAG Structure

check_task.set_upstream(glue_task)
ssh_task.set_upstream(check_task)

This ensures the DAG runs Glue → Check → SSH in sequence.

✅ Best Practices

Keep Glue scripts modular and lightweight.

Use XCom only for small metadata, not large payloads.

Always monitor Glue logs for debugging.

Secure SSH connections with proper Airflow connection management.

By combining Glue jobs with XCom flags and downstream operators, you can build robust, scalable, and conditional workflows in MWAA.
