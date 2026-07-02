# Data Engineer Interview Questions & Answers
### Based on Skills from Nagarjuna's Resume

---

## 1. AWS Glue, EMR, EC2, S3, Lambda, MWAA, IAM, SQS, Redshift

**Q1. What is AWS Glue, and how does it work?**
AWS Glue is a serverless data integration service. It helps extract data from source systems, transform it using PySpark or Python scripts, and load it into a target like S3 or Redshift. Since it's serverless, we don't need to manage servers — AWS handles the infrastructure, and we just pay for the time the job runs.

**Q2. What is the difference between AWS Glue and Amazon EMR?**
Glue is serverless and best for simple to medium ETL jobs — you just write the script and Glue manages the cluster automatically. EMR gives more control — we can configure our own Hadoop/Spark cluster, choose node types, and tune performance. EMR is better for heavy, complex big data workloads where we need more control.

**Q3. How do Glue jobs get triggered? Can you schedule them?**
Yes. Glue jobs can be triggered in a few ways: on a schedule (like a cron expression), based on an event (like a new file arriving in S3), or manually. In my projects, we mostly used Apache Airflow (MWAA) to orchestrate and trigger Glue jobs as part of a larger pipeline.

**Q4. What is a Glue Data Catalog, and why is it needed?**
It's a central metadata repository that stores table definitions, schema, and location of data (like S3 paths). It works like a metadata layer so that Glue, Athena, Redshift Spectrum, and other AWS services can all understand the structure of the data without scanning it every time.

**Q5. What is the difference between S3 storage classes (Standard, IA, Glacier)?**
Standard is for frequently accessed data and costs more. Infrequent Access (IA) is for data accessed occasionally — cheaper storage but a retrieval cost applies. Glacier is for long-term archival, very cheap to store but slow and costly to retrieve. We choose based on how often the data is accessed.

**Q6. What is IAM, and how do you manage permissions for a Glue job to access S3?**
IAM (Identity and Access Management) controls who or what can access AWS resources. For a Glue job to read/write S3, we attach an IAM role to the Glue job with a policy that grants specific S3 permissions (like GetObject, PutObject) only on the required buckets — following the principle of least privilege.

**Q7. What is Lambda, and have you used it to trigger any pipeline?**
Lambda is a serverless compute service that runs code in response to events, without provisioning servers. It's commonly used to trigger a Glue job when a new file lands in S3, or to run small automation scripts — for example, sending an alert when a pipeline fails.

**Q8. What is SQS, and how is it different from SNS?**
SQS (Simple Queue Service) is a message queue — messages wait in the queue until a consumer picks them up, which is useful for decoupling systems. SNS (Simple Notification Service) is a publish-subscribe service — a message is sent to multiple subscribers at once (like email or SMS alerts). In short: SQS is pull-based (one consumer), SNS is push-based (many subscribers).

**Q9. What is MWAA (Managed Airflow), and why choose it over self-hosted Airflow?**
MWAA is AWS's managed version of Apache Airflow. Instead of setting up and maintaining our own Airflow servers, AWS manages the infrastructure, scaling, and patching for us. This saves operational effort and lets the team focus on building DAGs instead of managing servers.

**Q10. What is Amazon Redshift, and how is it different from a normal database?**
Redshift is a cloud data warehouse designed for large-scale analytics and reporting. Unlike a normal transactional database (like MySQL) which is row-based and optimized for quick reads/writes of single records, Redshift is columnar and optimized for running heavy aggregate queries across millions of rows.

**Q11. Have you faced any issue with Glue job failures? How did you debug it?**
Yes. Usually I check CloudWatch logs first to find the exact error — it could be a schema mismatch, memory issue, or a bad file. I also check job bookmarks to see if it's reprocessing old data unnecessarily. For data-level issues, I check our rejection logs and dead-letter S3 path to see which records failed and why.

---

## 2. PySpark, Hive, Hadoop, Databricks, Informatica BDM

**Q1. What is PySpark, and how is it different from normal Python?**
PySpark is the Python API for Apache Spark, a distributed computing engine. Normal Python runs on a single machine, but PySpark can process huge datasets across multiple machines in parallel, which makes it suitable for big data processing.

**Q2. Explain transformations vs actions in Spark.**
Transformations (like `filter`, `map`, `select`) define what operation should happen to the data, but they don't run immediately — they just build a plan. Actions (like `count`, `collect`, `write`) actually trigger the execution of that plan. This separation allows Spark to optimize the whole chain of operations before running anything.

**Q3. What is lazy evaluation in Spark?**
Lazy evaluation means Spark doesn't execute transformations right away. It waits until an action is called, then it looks at all the transformations together and creates the most efficient execution plan. This avoids unnecessary computation and improves performance.

**Q4. What are broadcast joins? Why do you use them?**
A broadcast join is used when joining a large table with a small table. Instead of shuffling the large table across the cluster (which is expensive), Spark sends ("broadcasts") a copy of the small table to every node, so the join happens locally without heavy data movement. I used this to speed up joins in my pipelines and reduce shuffle time.

**Q5. What is partitioning in Spark, and why does it improve performance?**
Partitioning splits data into smaller chunks based on a column (like date or region), so Spark can process them in parallel and skip irrelevant partitions during a query. For example, if data is partitioned by date, a query filtering for one month only reads that month's partition, not the entire dataset.

**Q6. What is the difference between Hive and Hadoop?**
Hadoop is the overall big data framework that includes distributed storage (HDFS) and processing (MapReduce). Hive is a data warehouse layer built on top of Hadoop that lets us write SQL-like queries (HQL) instead of writing complex MapReduce code directly.

**Q7. What is a Hive metastore?**
It's a database that stores metadata about Hive tables — like schema, column names, data types, and storage location. It allows query engines to understand the structure of the data without scanning the actual files first.

**Q8. What is Databricks, and how is it different from EMR?**
Databricks is a managed platform built on top of Apache Spark, offering a collaborative notebook environment, job scheduling, and an optimized Spark runtime (Delta Lake). EMR is AWS's own managed Hadoop/Spark cluster service. Databricks generally offers a smoother developer experience and better performance tuning out of the box, while EMR gives more low-level infrastructure control.

**Q9. Have you used Informatica BDM? What was your use case?**
Yes, I worked on migrating pipelines built in Informatica BDM to AWS Glue. Before migration, Informatica BDM was used for our on-prem/legacy ETL workflows. As part of modernization, we rebuilt that logic using PySpark and AWS-native services.

---

## 3. Apache Airflow (MWAA), IBM TWS

**Q1. What is a DAG in Airflow?**
DAG stands for Directed Acyclic Graph. It represents a workflow as a series of tasks with dependencies — meaning task order matters, and there are no circular dependencies. Each node is a task, and the edges define the order of execution.

**Q2. How do you handle task failures or retries in Airflow?**
Airflow allows us to configure retry settings per task — like number of retries and delay between retries. We can also set up alerts (email/SNS) on failure, and use trigger rules to control what happens to downstream tasks if an upstream task fails.

**Q3. What is the difference between Airflow and traditional schedulers like IBM TWS?**
TWS is a traditional time-based job scheduler — mainly focused on running jobs at fixed times. Airflow is more flexible — it supports dependency-based, event-driven scheduling, has a rich UI to monitor DAGs, and integrates well with cloud-native services through operators.

**Q4. Why did your team move from TWS to Airflow?**
We wanted event-driven orchestration instead of just time-based scheduling, better visibility into pipeline status through Airflow's UI, and easier integration with AWS services like Glue and S3. It also made it easier to manage dependencies between tasks.

**Q5. What are Airflow operators? Which ones have you used?**
Operators define what a task actually does. I've used the GlueJobOperator to trigger Glue jobs, PythonOperator for custom logic, and S3 sensors to wait for a file to arrive before starting a task.

---

## 4. Python, SQL, HQL

**Q1. Write a SQL query to find duplicate records in a table.**
```sql
SELECT employee_id, COUNT(*) 
FROM employees
GROUP BY employee_id
HAVING COUNT(*) > 1;
```

**Q2. Write a SQL query to find the second highest salary.**
```sql
SELECT MAX(salary) AS second_highest_salary
FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);
```

**Q3. What is the difference between WHERE and HAVING?**
WHERE filters rows before grouping happens, and it cannot be used with aggregate functions like COUNT or SUM directly. HAVING filters groups after the GROUP BY is applied, and it's used specifically to filter based on aggregate results.

**Q4. What are Python decorators?**
A decorator is a function that wraps another function to add extra behavior without changing its original code. For example, I could use a decorator to log how long a function takes to run, or to handle errors automatically before/after the main function executes.

**Q5. Explain error handling in Python (try/except) — how did you use it in your log management project?**
`try` lets us run code that might fail, and `except` catches the error so the program doesn't crash. In my log management project, I used try/except blocks around file operations to catch issues like missing files or permission errors, log the exact error, and continue processing other files instead of stopping the whole pipeline.

**Q6. What is HQL, and how is it different from SQL?**
HQL (Hive Query Language) is very similar to SQL in syntax, but it's designed to run on top of Hadoop and translates queries into MapReduce or Spark jobs behind the scenes. Standard SQL usually runs directly against a relational database.

---

## 5. SQL (PostgreSQL, MySQL), NoSQL (DynamoDB, MongoDB)

**Q1. What is the difference between SQL and NoSQL databases?**
SQL databases are relational, store data in structured tables with fixed schema, and are good for complex queries with joins. NoSQL databases are non-relational, allow flexible/dynamic schema, and are better suited for unstructured or fast-changing data, and horizontal scaling.

**Q2. When would you choose DynamoDB over PostgreSQL?**
I'd choose DynamoDB when I need very fast read/write performance at large scale, flexible schema, and low-latency access for simple key-based lookups — like storing session data or event logs. PostgreSQL is better when I need complex queries, joins, and strong data consistency.

**Q3. What is a primary key vs a foreign key?**
A primary key uniquely identifies each record in a table. A foreign key is a column in one table that refers to the primary key in another table, used to create a relationship between the two tables.

**Q4. What is indexing, and why does it improve query speed?**
An index is a data structure that helps the database find rows faster, similar to an index in a book. Without an index, the database scans every row (a full table scan). With an index, it can jump directly to the relevant rows, making lookups much faster — especially on large tables.

**Q5. What is the difference between DynamoDB and MongoDB?**
DynamoDB is a fully managed AWS NoSQL service, works on key-value and document model, and scales automatically with minimal setup. MongoDB is a document-based NoSQL database that can be self-hosted or managed, and offers more flexible querying capabilities out of the box.

---

## 6. Redshift, Databricks Lakehouse, Dimensional Modelling, Star Schema

**Q1. What is a star schema? Can you explain fact tables and dimension tables?**
A star schema is a way of organizing data for reporting. It has one central fact table (containing measurable data, like sales amount or transaction count) surrounded by multiple dimension tables (containing descriptive data, like customer, product, or date details). It's called a "star" because of how the fact table connects to each dimension table like rays from a center.

**Q2. What is the difference between a data warehouse and a data lake?**
A data warehouse stores structured, processed data, optimized for reporting and analytics (like Redshift). A data lake stores raw data in any format — structured, semi-structured, or unstructured — and is more flexible but needs more processing before it's ready for analysis (like our S3-based Medallion architecture).

**Q3. What is a Lakehouse, and how is it different from a normal data warehouse?**
A Lakehouse combines the flexibility of a data lake (storing raw, low-cost data in any format) with the performance and reliability features of a data warehouse (like ACID transactions and schema enforcement). Databricks Lakehouse is a common example — it lets us run both raw data storage and structured analytics on the same platform.

**Q4. Why is dimensional modelling important for reporting?**
It organizes data in a way that's easy and fast to query for business reporting — separating "what happened" (facts) from "who/what/when it happened to" (dimensions). This structure makes it simpler for BI tools and analysts to build dashboards and run aggregate queries efficiently.

**Q5. Have you designed a star schema? Can you walk through an example?**
Yes, in our reporting layer, we had a fact table for transactions (with amount, transaction ID, and foreign keys), connected to dimension tables like Customer, Product, and Date. This allowed the reporting team to easily calculate things like "total sales by customer by month" through simple joins.

---

## 7. Data Quality — Schema Validation, Rejection Logging, Audit/Reconciliation

**Q1. How do you validate incoming data before loading it?**
I check that incoming data matches the expected schema — correct column names, data types, and required fields. I also apply null checks and business rule validations (like checking valid value ranges) before allowing data into the pipeline.

**Q2. What is rejection logging, and how did you implement it in your pipelines?**
Rejection logging captures records that fail validation instead of silently dropping them. In my pipelines, I wrote failed records to a separate "dead-letter" path in S3, along with the reason for rejection, so the team could review and fix the issue without losing any data.

**Q3. What is data reconciliation, and why is it important?**
Data reconciliation is the process of comparing source and target data counts (or values) to make sure nothing was lost or duplicated during processing. It's important because it builds trust in the pipeline — we can confirm that what went in matches what came out, which is critical for compliance and audit needs.

**Q4. How do you handle bad or corrupt records in a pipeline?**
I catch them using validation checks and error handling, log the error with details, move the bad record to a rejection/dead-letter location, and send an alert (via SNS or email) so the issue can be reviewed — while letting the rest of the good data continue processing.

**Q5. What is data profiling?**
Data profiling means analyzing a dataset to understand its structure, patterns, and quality — like checking for missing values, duplicate records, value distributions, and data types. It helps us understand the data before designing validation rules or transformations.

---

## 8. File Formats — Parquet, ORC, Avro, JSON, CSV, XML

**Q1. Why Parquet over CSV?**
Parquet is a columnar format, so it only reads the columns needed for a query, compresses better, and supports predicate pushdown, which makes it much faster and cheaper for analytics compared to CSV, which is row-based and uncompressed.

**Q2. When would you use Avro instead of Parquet?**
I'd use Avro for streaming use cases (like Kafka) or when the schema changes frequently, since Avro handles schema evolution well and is optimized for fast writes. Parquet is better for analytical reads, not fast, frequent writes.

*(See our earlier conversation for a full breakdown of CSV, JSON, XML, Parquet, ORC, and Avro if you'd like to review the details again.)*

---

## 9. Git, Azure DevOps, Jenkins, Jira, Confluence, ServiceNow

**Q1. What is the difference between Git merge and Git rebase?**
Merge combines two branches and creates a new merge commit, keeping the full history of both branches. Rebase moves your branch's commits on top of another branch, creating a cleaner, linear history but rewriting commit history in the process.

**Q2. What is a CI/CD pipeline? Have you built one?**
CI/CD stands for Continuous Integration and Continuous Deployment. CI means automatically testing and validating code changes, and CD means automatically deploying those changes to different environments. In my project, we used Azure DevOps pipelines to deploy Glue job scripts and configuration files across dev, UAT, and prod environments.

**Q3. How do you use Azure DevOps in your project?**
We used Azure DevOps for source control, work item tracking, and CI/CD pipelines — automating the deployment of PySpark scripts and YAML configuration files across different environments in a consistent, repeatable way.

**Q4. What is ServiceNow used for in your team?**
ServiceNow is mainly used for incident and ticket management — for example, if a production pipeline fails, an incident ticket is raised, tracked, and resolved through ServiceNow.

**Q5. How do you track your sprint tasks in Jira?**
We create user stories and tasks in Jira for each sprint, update their status (To Do, In Progress, Done) as we work, and review them during daily standups and sprint reviews.

---

## 10. Agile/Scrum, CI/CD, Code Reviews

**Q1. What is the difference between Agile and Scrum?**
Agile is a broad philosophy/methodology for iterative software development. Scrum is a specific framework that implements Agile principles through defined roles (Scrum Master, Product Owner), events (sprint planning, standups, retrospectives), and artifacts (backlog, sprint board).

**Q2. What happens in a sprint retrospective?**
The team looks back at the completed sprint and discusses what went well, what didn't go well, and what can be improved in the next sprint. It's focused on continuous improvement of the team's process, not just the product.

**Q3. What do you look for while doing a code review?**
I check for code correctness, adherence to coding standards, proper error handling, performance considerations (like avoiding unnecessary loops or shuffles in Spark), readability, and whether the code follows the modular design patterns our team agreed on.

**Q4. What is CI/CD, and why is it important in data engineering?**
CI/CD automates testing and deployment of code changes. In data engineering, it's important because it lets us deploy pipeline changes (like Glue jobs) safely and consistently across environments, reducing manual errors and speeding up delivery.

---

## Tips for Using This Guide
- Practice saying answers out loud, don't just read them — this builds natural delivery.
- Where possible, connect answers back to your own resume projects (Medallion migration, Informatica-to-Glue migration, log management system) to make answers feel personal, not memorized.
- For coding questions (SQL/Python), practice writing them by hand or in a text editor — interviewers often ask you to write code live.
