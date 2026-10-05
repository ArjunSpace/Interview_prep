# Databricks & Delta Lake Senior Interview Preparation Guide

This comprehensive guide covers foundational, intermediate, and advanced Databricks, Delta Lake, Unity Catalog, and Delta Live Tables (DLT) interview questions, paired with professional responses and real-world scenario breakdowns to help you project senior-level expertise.

---

## Part 1: Basic Questions (Foundations & Architecture)

### Q1: What is the Databricks Lakehouse Platform, and how does Delta Lake fit into it?
* **What they want to hear:** You understand that Databricks bridges data lakes and data warehouses. Delta Lake is an open-source storage layer sitting on top of cloud object storage (S3/ADLS/GCS).
* **Professional Answer:** 
  > "Databricks provides a unified analytics platform built on Apache Spark. Delta Lake is the transactional engine of the Lakehouse. It brings ACID transactions, scalable metadata handling, and unified batch/streaming to standard object storage by introducing an open-format transaction log (`_delta_log`) built on top of Parquet files."

### Q2: Explain the difference between All-Purpose Clusters and Job Clusters.
* **Professional Answer:**
  > "All-Purpose (Interactive) clusters are meant for collaborative development, running notebooks, and ad-hoc debugging; they stay alive until manually terminated or timed out, making them expensive if left idle. **Job clusters**, on the other hand, are ephemeral—they spin up automatically to execute a specific scheduled workflow (via Databricks Workflows), and terminate immediately upon completion. For cost optimization, production pipelines should always run on Job clusters."

### Q3: How do you handle sensitive configurations, like database credentials or API keys, in Databricks?
* **Professional Answer:**
  > "Never hardcode credentials. I use **Databricks Secret Scopes**, which can be backed natively by Databricks or integrated with external key vaults like Azure Key Vault or AWS Secrets Manager. Inside notebooks or jobs, they are retrieved securely using `dbutils.secrets.get(scope = 'my-scope', key = 'my-key')`, masking the values automatically in logs."

---

## Part 2: Medium Questions (Performance & Lakehouse Mechanics)

### Q4: What is the "Small File Problem" in data lakes, and how does Databricks solve it?
* **Professional Answer:**
  > "Constantly writing streaming data or micro-batches creates thousands of tiny Parquet files, bloating the file metadata and destroying Spark scan performance due to high I/O overhead. Databricks solves this natively using the `OPTIMIZE` command (which runs bin-packing to merge small files into larger ~1GB files). Furthermore, features like **Auto Loader** (`cloudFiles`) have built-in queue management to optimize file listing and reduce directory listing costs."

### Q5: Explain the difference between `OPTIMIZE` with Z-Ordering and traditional database indexing.
* **Professional Answer:**
  > "Unlike traditional relational databases that use B-Trees, Delta Lake uses **Z-Ordering** as a multi-dimensional clustering technique. When you run `OPTIMIZE table ZORDER BY (col1, col2)`, it co-locates related information within the same physical files based on specified columns. This drastically improves **data skipping** metrics; Spark can read the Delta transaction log statistics (min/max values per file) to completely bypass reading irrelevant files during a query."

### Q6: How does Auto Loader (`cloudFiles`) work, and why should you use it over standard file ingestion?
* **Professional Answer:**
  > "Standard `spark.read.load()` lists an entire cloud directory every time it runs, which becomes exponentially slow and expensive as file counts grow into millions. Auto Loader (`format('cloudFiles')`) uses a directory listing mode or, preferably, a **notification mode** (leveraging cloud services like AWS SNS/SQS or Azure Event Grid). It incrementally detects and ingests new files as they arrive, maintaining its own state in a RocksDB-backed checkpoint location to track processed files reliably."

---

## Part 3: Hard Questions (Advanced Spark & Internals)

### Q7: How does Delta Lake Time Travel work under the hood? Can it be used for disaster recovery?
* **Professional Answer:**
  > "Time travel is powered by the Delta transaction log (`_delta_log`). Every write, update, or delete operation commits a new JSON file (e.g., `000001.json`) containing changes and pointing to specific Parquet files. When you query an older version using `VERSION AS OF` or `TIMESTAMP AS OF`, Delta reconstructs the table state using those specific log files without modifying the underlying data. 
  > For disaster recovery, if a bad batch corrupts a table, you can instantly roll back production data using: `RESTORE TABLE my_table TO VERSION AS OF 5`."

### Q8: What causes a Spark Shuffle, and how does Adaptive Query Execution (AQE) optimize it?
* **Professional Answer:**
  > "A shuffle occurs when data needs to be redistributed across different executor nodes—typically during wide transformations like `groupBy`, `join`, or `repartition`. It involves disk I/O, serialization, and network traffic, making it the most expensive phase of a Spark job.
  > Databricks enables **Adaptive Query Execution (AQE)** by default, which optimizes execution plans *at runtime* based on accurate stats collected from shuffle blocks. AQE dynamically:
  > 1. Converts sort-merge joins into **broadcast hash joins** if one side shrinks below the threshold.
  > 2. Coalesces post-shuffle partitions to prevent small-file overhead.
  > 3. Automatically handles **data skew** by splitting skew partitions into smaller sub-tasks."

---

## Part 4: Unity Catalog & Modern Governance

### Q9: What is Databricks Unity Catalog, and how does it solve traditional data governance challenges?
* **Professional Answer:**
  > "Unity Catalog provides centralized access control, data lineage, auditing, and discovery across all workspaces in a Databricks account. Unlike the legacy Hive metastore—which was restricted to a single workspace, relied on external cloud IAM mappings, and lacked fine-grained column/row-level security—Unity Catalog introduces a secure three-level namespace (`catalog.schema.table`) and supports attribute-based access control (ABAC) natively across tables, views, volumes, and models."

### Q10: How do you implement Row-Level and Column-Level Security (RLS/CLS) in Unity Catalog?
* **Professional Answer:**
  > "Instead of duplicating data into isolated tables for different departments, Unity Catalog allows you to implement RLS and CLS using standard SQL **dynamic views** combined with built-in user context functions like `is_member()` or `current_user()`. 
  > For example, you can create a view where a regional sales column is dynamically masked (`CASE WHEN is_member('hr_admins') THEN salary ELSE 'REDACTED' END`) or filtered (`WHERE region = current_region()`). Because Unity Catalog enforces permissions on the underlying view/table definitions, users only see data they are authorized to access."

---

## Part 5: Delta Live Tables (DLT) & Declarative Pipelines

### Q11: What is Delta Live Tables (DLT), and how does it differ from traditional Spark streaming code?
* **Professional Answer:**
  > "Delta Live Tables is a declarative framework for building reliable, maintainable batch and streaming data pipelines. In traditional Spark, developers write imperative code—manually handling checkpoints, state management, file discovery, and failure retries across multiple interdependent notebooks. 
  > With DLT, you use a **declarative** approach (Python or SQL decorators like `@dlt.table`). You define *what* the tables should look like, and the DLT engine automatically manages workflow orchestration, dependency resolution, infrastructure provisioning, and continuous data quality checks under the hood."

### Q12: How do you handle data quality and bad records in Delta Live Tables without failing the entire pipeline?
* **Professional Answer:**
  > "DLT introduces **Expectations**, which act as automated assertions on data quality directly within the table definition using SQL constraints. You handle bad data using three strategies depending on business requirements:
  > 1. `CONSTRAINT name EXPECT (condition)`: Logs a warning metric if a record fails, but lets the record pass through.
  > 2. `CONSTRAINT name EXPECT (condition) ON VIOLATION DROP`: Silently drops invalid records.
  > 3. `CONSTRAINT name EXPECT (condition) ON VIOLATION FAIL`: Halts the pipeline immediately if bad data appears (ideal for contract validations).
  > To capture dropped records for auditing without failing the run, I typically build a companion 'quarantine' table using the inverse of the expectation logic."

---

## Part 6: High-Frequency Scenario-Based Questions

### Scenario 1: Debugging a Production Pipeline Failure
> **The Interviewer Asks:** *"A critical daily pipeline writing to a Delta table failed overnight due to an erroneous application code change that inserted corrupted schema data halfway through. The table is now corrupt and downstream BI reports are broken. How do you fix this immediately and prevent it moving forward?"*

* **How to Answer (The Structured Senior Approach):**
  1. **Immediate Rollback (Time Travel):** *"First, I’ll query the table history using `DESCRIBE HISTORY my_table` to identify the version right before the bad job ran. I will instantly restore stability using `RESTORE TABLE my_table TO VERSION AS OF <version>`."*
  2. **Enforce Protection:** *"To prevent recurrence, I'll ensure **Schema Enforcement** (the default behavior in Delta Lake) is explicitly relied upon, which automatically throws an exception if incoming data columns don't match the target table schema."*
  3. **Data Quality Framework:** *"I would implement Delta Live Tables (DLT) **Expectations** or runtime validation checks in the ingestion stage to drop or quarantine invalid records before they hit clean layers."*

---

### Scenario 2: Resolving Severe Data Skew in a Large Join
> **The Interviewer Asks:** *"You are joining a 2TB transaction table with a 50GB customer dimension table on `customer_id`. The job keeps failing with an OOM (Out Of Memory) error on a couple of specific executors, while others finish quickly. What is happening and how do you fix it?"*

* **How to Answer:**
  1. **Identify the Root Cause:** *"This is a classic symptom of **Data Skew**. A small number of `customer_id` values (e.g., corporate accounts, null keys, or system test accounts) account for 80% of the rows. Those specific keys are overloading a few executor nodes during the shuffle join phase."*
  2. **Resolution Strategy:**
     * *If the dimension table was smaller (< 10-100MB), I would force a **Broadcast Join** using `broadcast(dim_df)` to eliminate the shuffle entirely.*
     * *Since the dimension table is 50GB (too large to broadcast safely without driver OOM), I would use **Salting**. I'd append a random salt integer (e.g., `0 to 9`) to the join key of the large table and replicate the dimension rows across 10 variations so the heavy keys get distributed evenly across tasks.*
     * *Alternatively, enable AQE skew join optimization (`spark.sql.adaptive.skewJoin.enabled=true`), which automatically detects and splits skewed partitions.*

---

### Scenario 3: Cross-Workspace Data Sharing with Unity Catalog
> **The Interviewer Asks:** *"Your data science team operates in a separate Databricks workspace from your data engineering team. They need secure, read-only access to gold-tier customer tables without copying data or managing complex cloud IAM roles across different AWS accounts or Azure tenants. How do you set this up using Unity Catalog?"*

* **How to Answer:**
  > "I would leverage **Delta Sharing**, which is natively integrated into Unity Catalog as an open protocol for secure data sharing. 
  > 1. I don't need to duplicate any data. As the data owner, I create a **Share** in Unity Catalog and add the target Gold tables to it.
  > 2. I create a **Recipient** entity representing the data science workspace or external organization.
  > 3. The data science team can then directly query the shared tables (e.g., `SELECT * FROM shared_catalog.gold_schema.customer_features`) as if it were a local table, while Unity Catalog handles secure token-based authentication, auditing, and governance across boundaries."*

---

### Scenario 4: Designing a Self-Healing Medallion Architecture with DLT
> **The Interviewer Asks:** *"Design a production-grade Medallion architecture (Bronze -> Silver -> Gold) using Delta Live Tables that ingests streaming JSON files from an S3/ADLS bucket, cleans data, and handles schema evolution gracefully."*

* **How to Answer:**
  > "I would structure the DLT pipeline into three distinct phases using Python decorators:
  > 1. **Bronze Layer:** Use `dlt.table` combined with Auto Loader (`spark.readStream.format('cloudFiles').option('cloudFiles.format', 'json')`) to ingest raw files incrementally. I would enable schema evolution (`cloudFiles.inferColumnTypes` and rescue data columns) to prevent pipeline crashes when upstream systems inject new fields.
  > 2. **Silver Layer:** Define streaming tables using `dlt.expect_or_drop` to filter out null keys and malformed JSON payloads. I'll perform deduplication and cast types explicitly.
  > 3. **Gold Layer:** Build aggregated materialized views using `dlt.table` for business intelligence reporting. 
  > Because it's DLT, I configure the pipeline in **Continuous mode** for low-latency streaming or **Triggered mode** for cost-effective scheduled batch runs, while leveraging built-in lineage graphs to monitor dependencies automatically."*

---

### Scenario 5: Handling GDPR / Data Privacy Requests (The "Right to Be Forgotten")
> **The Interviewer Asks:** *"Your company operates under GDPR. A user requests complete deletion of their personal identifiable information (PII) from your Delta Lake tables across Bronze, Silver, and Gold layers. How do you execute this efficiently?"*

* **How to Answer:**
  > "Executing a simple `DELETE FROM table WHERE user_id = '123'` marks the records as deleted in the Delta log, but the data physically remains in the Parquet files and older versions due to time travel. To achieve full compliance:
  > 1. I will run the standard `DELETE` command to remove records from active versions.
  > 2. To completely purge the data from storage and bypass time travel retention windows, I must run `VACUUM table RETAIN 0 HOURS` (note: disabling safety checks is required).
  > 3. Finally, I will run `OPTIMize` to clean up the files. For long-term architecture, I'd advocate tokenizing or isolating PII into separate tables/files so compliance deletions don't require full table rewrites."*