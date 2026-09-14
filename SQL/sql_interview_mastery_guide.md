# Ultimate SQL Interview Mastery Guide: 30+ Patterns, DDLs, Data & Expected Outputs

Mastering SQL interviews is not about memorizing syntax; it is about recognizing the **underlying structural patterns** so you can map any complex business requirement to a known architectural template. 

---

## Phase 1: The Core Mental Framework

Before diving into patterns, internalize these core rules to avoid common scoping and execution pitfalls:

1. **Deconstruct Business Logic First:** Translate prompts into raw data transformations: *Am I filtering rows, collapsing buckets, expanding permutations, or looking across timelines?*
2. **Respect the Logical Query Processing Order:** 
   $$\text{FROM} \to \text{ON} \to \text{OUTER} \to \text{WHERE} \to \text{GROUP BY} \to \text{HAVING} \to \text{SELECT} \to \text{DISTINCT} \to \text{ORDER BY} \to \text{LIMIT}$$
   *Knowing this order prevents scope errors, such as referencing a window function or column alias in a `WHERE` clause.*
3. **Build a Mental Template Library:** Categorize every question into one of core data shapes: Aggregations/Pivots, Ranking/Deduplication, Sequence/Time-series, Relational Graph/Funnel traversal, or Semi-structured data (JSON/Strings).

---

## Section 1: Grouping, Aggregation & Conditional Metrics

### Expanded Frequently Asked Questions & Solutions

#### Question 1.1: Rolling Retention & Month-over-Month Growth
* **Prompt:** Calculate a rolling 30-day active user count and month-over-month retention rate.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE user_activity (
      user_id INT,
      activity_date DATE
  );

  INSERT INTO user_activity VALUES 
  (1, '2026-01-05'), (1, '2026-02-01'), (2, '2026-01-10'), 
  (2, '2026-02-05'), (3, '2026-01-15'), (1, '2026-03-02');
  ```
* **Expected Output:**
  ```text
  activity_month | active_users | mom_retention_rate
  --------------------------------------------------
  2026-01        | 3            | NULL
  2026-02        | 2            | 0.67
  2026-03        | 1            | 0.50
  ```

#### Question 1.2: Department Sales vs. Company Average
* **Prompt:** Find categories where average sales exceed the overall company average, broken down by regional department.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE sales_records (
      dept VARCHAR(50),
      category VARCHAR(50),
      sale_amount DECIMAL(10,2)
  );

  INSERT INTO sales_records VALUES 
  ('North', 'Electronics', 500.00), ('North', 'Electronics', 600.00),
  ('North', 'Clothing', 100.00), ('South', 'Electronics', 400.00),
  ('South', 'Clothing', 150.00), ('South', 'Clothing', 200.00);
  ```
* **Expected Output:**
  ```text
  dept  | category    | category_avg | company_avg
  ------------------------------------------------
  North | Electronics | 550.00       | 325.00
  ```

#### Question 1.3: Dynamic Pivot Transformation
* **Prompt:** Pivot row-level transaction logs into monthly columns (Jan through Dec) via conditional logic.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE transactions (
      department_id INT,
      sale_date DATE,
      amount DECIMAL(10,2)
  );

  INSERT INTO transactions VALUES 
  (101, '2026-01-15', 100.00), (101, '2026-01-20', 150.00),
  (101, '2026-02-10', 200.00), (102, '2026-01-05', 300.00);
  ```
* **Expected Output:**
  ```text
  department_id | jan_rev | feb_rev
  ---------------------------------
  101           | 250.00  | 200.00
  102           | 300.00  | 0.00
  ```

#### Question 1.4: Sliding Window Moving Averages
* **Prompt:** Calculate running totals and moving averages with sliding windows of varying sizes.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE daily_stock (
      stock_date DATE,
      price DECIMAL(10,2)
  );

  INSERT INTO daily_stock VALUES 
  ('2026-01-01', 10.00), ('2026-01-02', 12.00), 
  ('2026-01-03', 14.00), ('2026-01-04', 16.00);
  ```
* **Expected Output:**
  ```text
  stock_date | price | running_total | moving_avg_3d
  --------------------------------------------------
  2026-01-01 | 10.00 | 10.00         | 10.00
  2026-01-02 | 12.00 | 22.00         | 11.00
  2026-01-03 | 14.00 | 36.00         | 12.00
  2026-01-04 | 16.00 | 52.00         | 14.00
  ```

#### Question 1.5: Pareto Analysis (Top 80% Revenue)
* **Prompt:** Identify power users who account for the top 80% of cumulative revenue using running sums.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE user_revenue (
      user_id INT,
      revenue DECIMAL(10,2)
  );

  INSERT INTO user_revenue VALUES 
  (1, 500.00), (2, 300.00), (3, 100.00), (4, 50.00), (5, 50.00);
  ```
* **Expected Output:**
  ```text
  user_id | revenue | cumulative_pct
  ------------------------------------
  1       | 500.00  | 50.00
  2       | 300.00  | 80.00
  ```

### Architectural Mastery Strategy
* **The Pivot Pattern:** Stop relying on vendor-specific `PIVOT` clauses. Master **Conditional Aggregation**:
  ```sql
  SELECT 
      department_id,
      SUM(CASE WHEN EXTRACT(MONTH FROM sale_date) = 1 THEN amount ELSE 0 END) AS jan_rev,
      SUM(CASE WHEN EXTRACT(MONTH FROM sale_date) = 2 THEN amount ELSE 0 END) AS feb_rev
  FROM transactions
  GROUP BY department_id;
  ```
* **The Denominator Trap:** When computing percentages where numerator and denominator require different grouping levels, use window functions with `OVER()` instead of collapsing the entire dataset with `GROUP BY`.

---

## Section 2: Ranking, Deduplication & Temporal Ordering

### Expanded Frequently Asked Questions & Solutions

#### Question 2.1: Top N per Group with Sparse Departments
* **Prompt:** Find the top 3 highest-paid employees in *each* department without dropping departments that have fewer than 3 employees.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE employees (
      emp_id INT,
      dept_id INT,
      salary DECIMAL(10,2)
  );

  INSERT INTO employees VALUES 
  (1, 10, 5000), (2, 10, 7000), (3, 10, 6000), (4, 10, 8000),
  (5, 20, 4000), (6, 20, 4500);
  ```
* **Expected Output:**
  ```text
  emp_id | dept_id | salary | rnk
  -------------------------------
  4      | 10      | 8000   | 1
  2      | 10      | 7000   | 2
  3      | 10      | 6000   | 3
  6      | 20      | 4500   | 1
  5      | 20      | 4000   | 2
  ```

#### Question 2.2: Second-to-Last Login Timestamp
* **Prompt:** Identify the second-to-last login timestamp for every active user.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE logins (
      user_id INT,
      login_time TIMESTAMP
  );

  INSERT INTO logins VALUES 
  (1, '2026-01-01 08:00:00'), (1, '2026-01-02 09:00:00'), (1, '2026-01-03 10:00:00'),
  (2, '2026-01-01 11:00:00'), (2, '2026-01-02 12:00:00');
  ```
* **Expected Output:**
  ```text
  user_id | second_to_last_login
  ------------------------------
  1       | 2026-01-02 09:00:00
  2       | 2026-01-01 11:00:00
  ```

#### Question 2.3: Staging Table Deduplication
* **Prompt:** Deduplicate a high-throughput event staging table where multiple updates occurred for the same transaction ID, keeping only the absolute latest version.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE staging_events (
      txn_id INT,
      payload VARCHAR(50),
      updated_at TIMESTAMP
  );

  INSERT INTO staging_events VALUES 
  (100, 'v1', '2026-01-01 10:00:00'),
  (100, 'v2', '2026-01-01 12:00:00'),
  (101, 'v1', '2026-01-01 09:00:00');
  ```
* **Expected Output:**
  ```text
  txn_id | payload | updated_at
  ------------------------------------
  100    | v2      | 2026-01-01 12:00:00
  101    | v1      | 2026-01-01 09:00:00
  ```

#### Question 2.4: Median Fulfillment Time Without Percentile Functions
* **Prompt:** Find median values for delivery times across different fulfillment centers without using built-in percentile functions.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE fulfillment (
      center_id INT,
      delivery_hours INT
  );

  INSERT INTO fulfillment VALUES 
  (1, 12), (1, 24), (1, 48), 
  (2, 10), (2, 20), (2, 30), (2, 40);
  ```
* **Expected Output:**
  ```text
  center_id | median_hours
  ------------------------
  1         | 24
  2         | 30
  ```

#### Question 2.5: Higher Than Department Average
* **Prompt:** Find employees who earn more than the average salary of their respective departments.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE salaries (
      emp_name VARCHAR(50),
      dept VARCHAR(50),
      salary INT
  );

  INSERT INTO salaries VALUES 
  ('Alice', 'Eng', 100), ('Bob', 'Eng', 50), ('Charlie', 'HR', 40), ('David', 'HR', 60);
  ```
* **Expected Output:**
  ```text
  emp_name | dept | salary
  ------------------------
  Alice    | Eng  | 100
  David    | HR   | 60
  ```

### Architectural Mastery Strategy
* **Window Function Hierarchy:** Understand exact behavioral differences:
  * `ROW_NUMBER()`: Assigns a unique sequential integer. Use when you need to pick *any* arbitrary row during ties (e.g., standard deduplication).
  * `RANK()`: Assigns identical ranks for ties, leaving gaps in sequence numbers (e.g., 1, 2, 2, 4).
  * `DENSE_RANK()`: Assigns identical ranks for ties without gaps (e.g., 1, 2, 2, 3).
* **The Self-Join / CTE Fallback:** For legacy databases lacking window functions, use correlated subqueries or `NOT EXISTS` checks to isolate extreme values.

---

## Section 3: Sequences, Gaps & Islands (Advanced Temporal Logic)

### Expanded Frequently Asked Questions & Solutions

#### Question 3.1: Consecutive Streak Tracking
* **Prompt:** Find all consecutive days a user logged into the platform (Streak tracking).
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE user_logins (
      user_id INT,
      login_date DATE
  );

  INSERT INTO user_logins VALUES 
  (42, '2026-01-01'), (42, '2026-01-02'), (42, '2026-01-03'), 
  (42, '2026-01-05'), (42, '2026-01-06');
  ```
* **Expected Output:**
  ```text
  user_id | streak_start | streak_end | streak_length
  ---------------------------------------------------
  42      | 2026-01-01   | 2026-01-03 | 3
  42      | 2026-01-05   | 2026-01-06 | 2
  ```

#### Question 3.2: Missing Transaction ID Sequences
* **Prompt:** Find unoccupied seat blocks or missing transaction ID sequences in an audit log.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE audit_log (
      txn_id INT
  );

  INSERT INTO audit_log VALUES (1), (2), (4), (7), (8);
  ```
* **Expected Output:**
  ```text
  missing_txn_id
  --------------
  3
  5
  6
  ```

#### Question 3.3: Clickstream Sessionization
* **Prompt:** Track user sessionization: group clickstream events that happened within 30 minutes of each other into a single distinct session ID.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE clickstream (
      user_id INT,
      event_time TIMESTAMP
  );

  INSERT INTO clickstream VALUES 
  (1, '2026-01-01 10:00:00'), (1, '2026-01-01 10:15:00'),
  (1, '2026-01-01 11:00:00');
  ```
* **Expected Output:**
  ```text
  user_id | event_time          | session_id
  ------------------------------------------
  1       | 2026-01-01 10:00:00 | 1
  1       | 2026-01-01 10:15:00 | 1
  1       | 2026-01-01 11:00:00 | 2
  ```

#### Question 3.4: Overlapping Resource Bookings
* **Prompt:** Find overlapping hotel room bookings or schedule conflicts for resource allocation.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE bookings (
      room_id INT,
      start_date DATE,
      end_date DATE
  );

  INSERT INTO bookings VALUES 
  (101, '2026-01-01', '2026-01-05'),
  (101, '2026-01-04', '2026-01-08');
  ```
* **Expected Output:**
  ```text
  room_id | booking_1_start | booking_1_end | booking_2_start | booking_2_end
  ---------------------------------------------------------------------------
  101     | 2026-01-01      | 2026-01-05    | 2026-01-04      | 2026-01-08
  ```

#### Question 3.5: Customer Subscription Tenure Gaps
* **Prompt:** Calculate customer tenure gaps (inactive periods between active subscription cycles).
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE subscriptions (
      customer_id INT,
      sub_start DATE,
      sub_end DATE
  );

  INSERT INTO subscriptions VALUES 
  (1, '2025-01-01', '2025-06-01'),
  (1, '2025-08-01', '2025-12-01');
  ```
* **Expected Output:**
  ```text
  customer_id | gap_start  | gap_end    | gap_days
  ------------------------------------------------
  1           | 2025-06-01 | 2025-08-01 | 61
  ```

### Architectural Mastery Strategy
* **The Date-Minus-Row-Number Trick:** The gold standard for islands-and-gaps. Subtracting a sequential row number (`ROW_NUMBER()`) from a date sequence creates a constant group identifier for continuous blocks:
  ```sql
  WITH numbered AS (
      SELECT login_date, 
             login_date - INTERVAL '1 day' * ROW_NUMBER() OVER (ORDER BY login_date) AS grp
      FROM user_logins
      WHERE user_id = 42
  )
  SELECT MIN(login_date) AS streak_start, MAX(login_date) AS streak_end, COUNT(*) AS streak_length
  FROM numbered
  GROUP BY grp;
  ```
* **Lead/Lag Delta Analysis:** Use `LEAD()` and `LAG()` to inspect adjacent rows directly, evaluating state transitions without complex self-joins.

---

## Section 4: Complex Joins, Self-Joins & Funnel Analysis

### Expanded Frequently Asked Questions & Solutions

#### Question 4.1: Multi-Step Conversion Funnel
* **Prompt:** Calculate the multi-step conversion rate: Product View $\to$ Add to Cart $\to$ Checkout $\to$ Purchase.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE tracking_events (
      user_id INT,
      event_name VARCHAR(50),
      event_timestamp TIMESTAMP
  );

  INSERT INTO tracking_events VALUES 
  (1, 'View', '2026-01-01 10:00:00'), (1, 'Cart', '2026-01-01 10:05:00'), (1, 'Purchase', '2026-01-01 10:10:00'),
  (2, 'View', '2026-01-01 11:00:00');
  ```
* **Expected Output:**
  ```text
  total_views | total_carts | total_purchases | view_to_cart_rate | cart_to_purchase_rate
  ---------------------------------------------------------------------------------------
  2           | 1           | 1               | 0.50              | 1.00
  ```

#### Question 4.2: Organizational Hierarchy Traversal
* **Prompt:** Find organizational hierarchies: list all employees reporting up to a specific executive vice president.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE org_chart (
      emp_id INT,
      manager_id INT,
      emp_name VARCHAR(50)
  );

  INSERT INTO org_chart VALUES 
  (1, NULL, 'CEO'), (2, 1, 'VP'), (3, 2, 'Manager'), (4, 3, 'Analyst');
  ```
* **Expected Output:**
  ```text
  emp_id | emp_name | depth_level
  -------------------------------
  2      | VP       | 1
  3      | Manager  | 2
  4      | Analyst  | 3
  ```

#### Question 4.3: Action Sequence Within Strict Time Windows
* **Prompt:** Find users who performed Action X *followed by* Action Y within a strict 24-hour window, without performing Action Z in between.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE user_actions (
      user_id INT,
      action_type VARCHAR(10),
      action_time TIMESTAMP
  );

  INSERT INTO user_actions VALUES 
  (1, 'X', '2026-01-01 10:00:00'),
  (1, 'Y', '2026-01-01 15:00:00');
  ```
* **Expected Output:**
  ```text
  user_id | x_time              | y_time
  ---------------------------------------------------
  1       | 2026-01-01 10:00:00 | 2026-01-01 15:00:00
  ```

#### Question 4.4: Market Basket Analysis Pairs
* **Prompt:** Find market basket analysis pairs: products frequently purchased together in the same transaction.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE order_items (
      order_id INT,
      product_name VARCHAR(50)
  );

  INSERT INTO order_items VALUES 
  (1, 'Laptop'), (1, 'Mouse'),
  (2, 'Laptop'), (2, 'Keyboard'),
  (3, 'Laptop'), (3, 'Mouse');
  ```
* **Expected Output:**
  ```text
  product_a | product_b | frequency
  ---------------------------------
  Keyboard  | Laptop    | 1
  Laptop    | Mouse     | 2
  ```

#### Question 4.5: Full Outer Join Database Reconciliation
* **Prompt:** Perform a full outer join reconciliation across two independent databases to identify missing records on both sides.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE db_primary (record_id INT, val VARCHAR(10));
  CREATE TABLE db_replica (record_id INT, val VARCHAR(10));

  INSERT INTO db_primary VALUES (1, 'A'), (2, 'B');
  INSERT INTO db_replica VALUES (2, 'B'), (3, 'C');
  ```
* **Expected Output:**
  ```text
  record_id | primary_val | replica_val | match_status
  ----------------------------------------------------
  1         | A           | NULL        | Missing in Replica
  2         | B           | B           | Match
  3         | NULL        | C           | Missing in Primary
  ```

### Architectural Mastery Strategy
* **Interval and Non-Equi Joins:** Move beyond standard `ON a.id = b.id`. Practice joining tables on inequality boundaries or time intervals:
  ```sql
  SELECT c.user_id, e.event_name
  FROM conversions c
  JOIN tracking_events e 
    ON c.user_id = e.user_id
   AND e.event_timestamp BETWEEN c.conversion_time - INTERVAL '24 hours' AND c.conversion_time;
  ```
* **Funnel Logic with Conditional States:** Isolate each step into clear Common Table Expressions (CTEs), then stitch them together using `LEFT JOIN` or conditional aggregation flags to prevent pipeline drop-off miscalculations.

---

## Section 5: Strings, Arrays & Semi-Structured JSON

### Expanded Frequently Asked Questions & Solutions

#### Question 5.1: Delimited String Splitting to Rows
* **Prompt:** Parse a comma-separated list of tags stored in a single table column into individual rows.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE articles (
      article_id INT,
      tags VARCHAR(100)
  );

  INSERT INTO articles VALUES 
  (1, 'sql,database,performance'),
  (2, 'python,etl');
  ```
* **Expected Output:**
  ```text
  article_id | tag
  ----------------------
  1          | sql
  1          | database
  1          | performance
  2          | python
  2          | etl
  ```

#### Question 5.2: JSON Property Extraction and Filtering
* **Prompt:** Extract nested keys from a JSON configuration column and filter rows based on attribute values.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE configurations (
      config_id INT,
      settings JSON
  );

  INSERT INTO configurations VALUES 
  (1, '{"mode": "production", "timeout": 30}'),
  (2, '{"mode": "staging", "timeout": 10}');
  ```
* **Expected Output:**
  ```text
  config_id | mode       | timeout
  --------------------------------
  1         | production | 30
  ```

#### Question 5.3: Array Aggregation and Deduplication
* **Prompt:** Group transactional elements into a distinct array collection per user.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE user_logs (
      user_id INT,
      action VARCHAR(50)
  );

  INSERT INTO user_logs VALUES 
  (1, 'login'), (1, 'click'), (1, 'login');
  ```
* **Expected Output:**
  ```text
  user_id | distinct_actions
  --------------------------
  1       | ["login", "click"]
  ```

#### Question 5.4: Substring Pattern Matching & Domain Extraction
* **Prompt:** Extract domain names from a column containing full email addresses.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE users (
      email VARCHAR(100)
  );

  INSERT INTO users VALUES 
  ('alice@company.com'), ('bob@enterprise.org');
  ```
* **Expected Output:**
  ```text
  email              | domain_name
  --------------------------------
  alice@company.com  | company.com
  bob@enterprise.org | enterprise.org
  ```

#### Question 5.5: Dynamic JSON Key-Value Flattening
* **Prompt:** Flatten an arbitrary key-value JSON dictionary structure into tabular key-value rows.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE metadata_store (
      item_id INT,
      attributes JSON
  );

  INSERT INTO metadata_store VALUES 
  (1, '{"color": "red", "size": "L"}');
  ```
* **Expected Output:**
  ```text
  item_id | attr_key | attr_value
  -------------------------------
  1       | color    | red
  1       | size     | L
  ```

### Architectural Mastery Strategy
* **String & JSON Functions:** Familiarize yourself with dialect-specific functions (`STRING_SPLIT`, `JSON_EXTRACT`, `unnest`, `LATERAL VIEW`) depending on whether you are using PostgreSQL, Snowflake, or Spark.

---

## Section 6: Self-Joins & Complex Hierarchies

### Expanded Frequently Asked Questions & Solutions

#### Question 6.1: Manager vs Employee Salary Comparison
* **Prompt:** Find employees who earn more than their direct managers.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE staff (
      id INT,
      name VARCHAR(50),
      salary INT,
      manager_id INT
  );

  INSERT INTO staff VALUES 
  (1, 'Boss', 10000, NULL),
  (2, 'Manager Bob', 6000, 1),
  (3, 'Worker Alice', 7000, 2);
  ```
* **Expected Output:**
  ```text
  employee_name | employee_salary | manager_name | manager_salary
  ---------------------------------------------------------------
  Worker Alice  | 7000            | Manager Bob  | 6000
  ```

#### Question 6.2: Multi-Level Path Reconstruction
* **Prompt:** Reconstruct complete organizational reporting paths (e.g., CEO $\to$ VP $\to$ Manager).
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE reporting_line (
      emp_id INT,
      manager_id INT,
      name VARCHAR(50)
  );

  INSERT INTO reporting_line VALUES 
  (1, NULL, 'Root'), (2, 1, 'Mid'), (3, 2, 'Leaf');
  ```
* **Expected Output:**
  ```text
  emp_id | hierarchy_path
  -----------------------
  3      | Root > Mid > Leaf
  ```

#### Question 6.3: Consecutive Paired Temperature Anomalies
* **Prompt:** Find all dates with higher temperatures compared to the previous day using self-joins or lag.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE weather (
      record_date DATE,
      temperature INT
  );

  INSERT INTO weather VALUES 
  ('2026-01-01', 20), ('2026-01-02', 25), ('2026-01-03', 22);
  ```
* **Expected Output:**
  ```text
  record_date | temperature
  -------------------------
  2026-01-02  | 25
  ```

#### Question 6.4: Bipartite Graph Edge Pairing (Symmetrical Matches)
* **Prompt:** Find reciprocal friendships or symmetrical matches in a social network graph without duplicate inverse pairs.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE friendships (
      user_a INT,
      user_b INT
  );

  INSERT INTO friendships VALUES 
  (1, 2), (2, 1), (3, 4);
  ```
* **Expected Output:**
  ```text
  user_a | user_b
  ---------------
  1      | 2
  3      | 4
  ```

#### Question 6.5: Circular Dependency Detection
* **Prompt:** Identify circular manager or dependency loops in a relational graph.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE dependencies (
      task_id INT,
      depends_on INT
  );

  INSERT INTO dependencies VALUES 
  (1, 2), (2, 3), (3, 1);
  ```
* **Expected Output:**
  ```text
  task_id | status
  ---------------------------
  1       | Circular Loop Detected
  ```

### Architectural Mastery Strategy
* **Recursive CTEs:** Master the `WITH RECURSIVE` construct for hierarchies, separating the anchor member from the recursive member using `UNION ALL`.

---

## Section 7: Performance Optimization & Query Tuning

### Expanded Frequently Asked Questions & Solutions

#### Question 7.1: Correlated Subquery to Join Refactoring
* **Prompt:** Optimize a slow-running correlated subquery checking for latest records into an efficient hash join.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE logs (user_id INT, log_time TIMESTAMP);
  INSERT INTO logs VALUES (1, '2026-01-01 10:00:00'), (1, '2026-01-01 11:00:00');
  ```
* **Expected Output:**
  ```text
  user_id | latest_log_time
  -------------------------
  1       | 2026-01-01 11:00:00
  ```

#### Question 7.2: Index Scan vs. Sequential Scan Identification
* **Prompt:** Explain how indexing columns used in `WHERE` and `JOIN` clauses alters query execution plans.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE orders (order_id INT PRIMARY KEY, customer_id INT);
  INSERT INTO orders VALUES (1, 100), (2, 101);
  ```
* **Expected Output:**
  ```text
  execution_strategy
  -------------------------------------------
  Index Scan using orders_pkey on orders
  ```

#### Question 7.3: Avoiding `SELECT *` and Unnecessary Sorting
* **Prompt:** Optimize a wide-table query bottlenecked by excessive disk spilling during `ORDER BY` execution.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE wide_table (id INT, col_a VARCHAR(100), col_b VARCHAR(100));
  INSERT INTO wide_table VALUES (1, 'A', 'B'), (2, 'C', 'D');
  ```
* **Expected Output:**
  ```text
  optimized_query_cost
  ---------------------
  Low (Filtered Projection)
  ```

#### Question 7.4: Window Function vs Self-Join Performance Tuning
* **Prompt:** Evaluate why window functions scale better than massive self-joins on large fact tables.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE fact_events (event_id INT, user_id INT, ts TIMESTAMP);
  INSERT INTO fact_events VALUES (1, 1, '2026-01-01');
  ```
* **Expected Output:**
  ```text
  performance_profile
  ------------------------------------
  Single Table Scan + Analytic Pass
  ```

#### Question 7.5: Partition Pruning and Cluster Key Optimization
* **Prompt:** Structure date-partitioned table queries to ensure partition pruning engages properly.
* **DDL & Sample Data:**
  ```sql
  CREATE TABLE partitioned_sales (sale_date DATE, amount INT);
  INSERT INTO partitioned_sales VALUES ('2026-01-01', 100);
  ```
* **Expected Output:**
  ```text
  partitions_scanned
  ------------------
  1 (Pruned: 364)
  ```

### Architectural Mastery Strategy
* **Execution Plan Analysis:** Always check `EXPLAIN ANALYZE` metrics. Look for high buffer usages, nested loop bottlenecks on large unindexed tables, and unnecessary sorts spilling to disk.

---

## Practice Checklist for Interview Readiness
- [ ] Group by and Pivot data without DB-specific functions.
- [ ] Deduplicate tables using `ROW_NUMBER()` and partition clauses.
- [ ] Solve consecutive streak problems using the date-minus-row-number pattern.
- [ ] Write non-equi interval joins for multi-step funnel drop-off analysis.
- [ ] Parse JSON properties and delimited strings into tabular rows.
- [ ] Traverse organizational and graph hierarchies using recursive CTEs.
- [ ] Explain time complexity, indexing strategies, and execution plans for large-scale table scans.