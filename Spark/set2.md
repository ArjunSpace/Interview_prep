# PySpark Fundamentals and Advanced Concepts

## 1. What is PySpark?

PySpark is the Python API for Apache Spark. It offers:

- **PySpark Shell** which connects the Python API to the Spark core and initializes the Spark context.
- For any Spark functionality, the entry point is `SparkContext`.
- By default, PySpark has `SparkContext` available as `sc`, so creating a new `SparkContext` won't work.

### More on PySpark

- PySpark is built on top of Spark's Java API.
- Data is processed in Python and cached/shuffled in the JVM.
- `SparkContext` uses **Py4J** to launch a JVM and creates a `JavaSparkContext`.

### Py4J Overview

Py4J enables Python programs running in a Python interpreter to dynamically access Java objects in a Java Virtual Machine. Methods are called as if the Java objects resided in the Python interpreter, and Java collections can be accessed through standard Python collection methods.

**Key Point:** To establish local communication between the Python and Java `SparkContext` objects, Py4J is used on the driver.

### Installation and Configuration of PySpark

- PySpark requires **Python 2.6 or higher**.
- PySpark applications are executed using a standard CPython interpreter in order to support Python modules that use C extensions.
- By default, PySpark requires Python to be available on the system PATH and uses it to run programs.
- Among PySpark's library dependencies, all are bundled with PySpark (including Py4J) and are automatically imported.

### Getting Started

You can enter Spark's Python environment by running the command in the shell:

```bash
./bin/pyspark
```

This will start your PySpark shell:

```
Python 2.7.12 (default, Nov 20 2017, 18:23:56)
[GCC 5.4.0 20160609] on linux2
Type "help", "copyright", "credits" or "license" for more information.
Welcome to
    ____              __
    / __/__  ___ _____/ /__
   _\ \/ _ \/ _ `/ __/  '_/
  /__ / .__/\_,_/_/ /_/\_\   version 2.x.x
     /_/

Using Python version 2.7.12 (default, Nov 20 2017, 18:23:56)
SparkSession available as 'spark'.
```

## 2. Resilient Distributed Datasets (RDDs)

Resilient Distributed Datasets (RDDs) are the main abstraction in Spark.

**Definition:**
- RDDs are a partitioned collection of objects spread across a cluster.
- They can be persisted in memory or on disk.
- Once created, RDDs are **immutable**.

### Ways to Create RDDs

1. **Parallelizing a collection** in the driver program.
2. **Referencing an external dataset** from an external storage system, like a shared filesystem, HBase, HDFS, or any data source providing a Hadoop InputFormat.

### Features of RDDs

- **Resilient:** Tolerant to faults using Hadoop RDD lineage graph and ready to recompute damaged or missing partitions due to node failures.
- **Dataset:** A set of partitioned data with primitive values or tuples/records.
- **Distributed:** Data remains on multiple nodes in a cluster.

### Creating RDDs

#### 1. Parallelizing a Collection

Example: Create a parallelized collection holding the numbers 1 to 5:

```python
data = [1, 2, 3, 4, 5]
distData = sc.parallelize(data)
```

Here, `distData` is the new RDD created by calling the `parallelize()` method.

#### 2. Referencing External Storage

You can create text file RDDs using `SparkContext`'s `textFile()` method:

```python
distFile = sc.textFile("data.txt")
```

This method takes a URI (local path, `hdfs://`, `s3n://`, etc.) and reads it as a collection containing lines to produce the RDD.

## 3. RDD Operations

RDDs support two types of operations:

1. **Transformations:** Create a new dataset from an existing one.
2. **Actions:** Return a value to the driver program after running a computation on the dataset.

### Examples

- `map()` is a **transformation** that passes each dataset element through a function and returns a new RDD representing the results.
- `reduce()` is an **action** which aggregates all RDD elements using a function and returns the final result to the driver program.

### Simple RDD Program Example

```python
lines = sc.textFile("data.txt")
lineLengths = lines.map(lambda s: len(s))
totalLength = lineLengths.reduce(lambda a, b: a + b)
```

- **Line 1:** Defines a base RDD from an external file.
- **Line 2:** Defines `lineLengths` as the result of a `map()` transformation.
- **Line 3:** Runs `reduce()`, which is an action.

## 4. Transformations

**Definition:** Transformations are functions that use an RDD as input and return one or more RDDs as output.

### Characteristics

- Transformations do not change the input RDD; they always create one or more new RDDs.
- By using transformations, you incrementally create an RDD lineage with all parent RDDs.
- **Transformations are lazy** — they are not run immediately.
- **Transformations are executed only after calling an action.**

### Examples of Transformations

- `filter(func)`: Returns a new dataset (RDD) by choosing elements where the function returns `true`.
- `map(func)`: Passes each element of the RDD through a supplied function.
- `union()`: New RDD contains elements from both source RDD and argument RDD.
- `intersection()`: New RDD includes only common elements from both RDDs.
- `cartesian()`: New RDD with cross product of all elements from both RDDs.

### Common Transformations

- `randomSplit`, `cogroup`, `join`, `reduceByKey`, `filter`, `map`

## 5. Actions

**Definition:** Actions return the final results of RDD computations.

### How Actions Work

Actions trigger execution by:
1. Using the lineage graph to load data into the original RDD.
2. Executing all intermediate transformations.
3. Writing final results to the file system or returning to the driver program.

### Examples of Actions

- `count()`: Get the number of data elements in the RDD.
- `collect()`: Get all data elements in an RDD as an array.
- `reduce(func)`: Aggregate data elements using a function that takes two arguments and returns one.
- `take(n)`: Fetch the first n data elements computed by the driver program.
- `foreach(func)`: Execute a function for each data element in RDD (usually for updates or external system interaction).
- `first()`: Retrieve the first data element in RDD (similar to `take(1)`).
- `saveAsTextFile(path)`: Write RDD content to a text file or set of text files on local filesystem or HDFS.

## 6. What is DataFrame?

**Definition:** In general, DataFrames are a data structure with tabular nature. They represent rows, each consisting of a number of observations.

**Characteristics:**
- Rows can have a variety of data formats (heterogeneous).
- A column can have data of the same data type (homogeneous).
- They contain metadata in addition to data like column and row names.

### Why DataFrames?

- DataFrames are widely used for processing large collections of structured or semi-structured data.
- They have the ability to handle petabytes of data.
- They support a wide range of data formats for reading and writing.

### Features of DataFrame

- **Distributed:** Fault-tolerant and highly available data structure.
- **Lazy Evaluation:** Evaluation strategy that holds expression evaluation until its value is needed.
- **Immutable:** Object state cannot be modified after creation.

### DataFrame Sources

DataFrames can be constructed from various sources:

- Structured data files
- Tables in Hive
- External Databases
- Existing RDDs

## 7. What is Spark SQL?

Spark SQL is a programming module for structured data processing introduced by Spark. It provides:

- A programming abstraction called **DataFrame**.
- Acts as a distributed SQL query engine.

### Features of Spark SQL

- Provides DataFrame abstraction in Scala, Java, and Python.
- Can read and write data from Hive Tables, JSON, and Parquet in various structured formats.
- Data can be queried using Spark SQL.

### Important Classes of Spark SQL and DataFrames

- `pyspark.sql.SparkSession`: Main entry point for DataFrame and Spark SQL functionality.
- `pyspark.sql.DataFrame`: A distributed collection of data grouped into named columns.
- `pyspark.sql.Column`: A column expression in a DataFrame.
- `pyspark.sql.Row`: A row of data in a DataFrame.
- `pyspark.sql.GroupedData`: Aggregation methods, returned by `DataFrame.groupBy()`.
- `pyspark.sql.DataFrameNaFunctions`: Methods for handling missing data (null values).
- `pyspark.sql.DataFrameStatFunctions`: Methods for statistics functionality.
- `pyspark.sql.functions`: List of built-in functions available for DataFrame.
- `pyspark.sql.types`: List of data types available.
- `pyspark.sql.Window`: For working with window functions.

## 8. Creating a DataFrame

The entry point into all functionality in Spark is the `SparkSession` class.

### Creating a Basic SparkSession

```python
from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .appName("Data Frame Example") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()
```

### Creating DataFrame with Rows

```python
from pyspark.sql import *

Student = Row("firstName", "lastName", "age", "telephone")
s1 = Student('David', 'Julian', 22, 100000)
s2 = Student('Mark', 'Webb', 23, 658545)
StudentData = [s1, s2]
df = spark.createDataFrame(StudentData)
df.show()
```

### Result of `show()`

```
+---------+--------+---+---------+
|firstName|lastName|age|telephone|
+---------+--------+---+---------+
|    David|  Julian| 22|   100000|
|     Mark|    Webb| 23|   658545|
+---------+--------+---+---------+
```

## 9. Data Sources

- Spark SQL supports operating on a variety of data sources through the DataFrame interface.
- A DataFrame can be operated on using relational transformations and can be used to create a temporary view.
- Registering a DataFrame as a temporary view allows you to run SQL queries over its data.

### Generic Load/Save Functions

```python
df = spark.read.load("file path")
# Spark loads the data source from the defined file path

df.select("column name", "column name").write.save("file name")
# The DataFrame is saved in the defined format
# By default it is saved in the Spark Warehouse
```

File paths can be from local machines as well as from HDFS.

### Manually Specifying Data Sources

You can manually specify the data source that will be used along with any extra options.

Data sources fully qualified name is used, but for built-in sources, you can use their short names: `json`, `parquet`, `jdbc`, `orc`, `libsvm`, `csv`, `text`.

### Loading JSON Files

```python
df = spark.read.load("path of json file", format="json")
```

## 10. Apache Parquet

### Overview

- Apache Parquet is a columnar storage format available to all projects in the Hadoop ecosystem.
- It is independent of the framework used for data processing, the data model, or programming language.
- Spark SQL provides support for both reading and writing Parquet files.
- Automatic conversion to nullable occurs when writing Parquet files (done for compatibility reasons).

### Why Parquet File Format?

- **Columnar Storage:** Stores nested data structures in a flat columnar format.
- **Efficiency:** Compared with traditional row-oriented storage, Parquet is more efficient.
- **Performance:** Parquet is the choice for big data because it serves both needs: efficiency and performance in both storage and processing.

### Reading and Writing Parquet Files

#### Reading JSON and Writing to Parquet

```python
from pyspark.sql import *

spark = SparkSession.builder.getOrCreate()
df = spark.read.json("emp.json")
df.show()
df.write.parquet("Employees")
df.createOrReplaceTempView("data")
res = spark.sql("select age,name,stream from data where stream='JAVA'")
res.show()
res.write.parquet("JavaEmployees")
```

#### Verifying the Result

```python
pf = spark.read.parquet("parquet file name")
pf.show()  # View the DataFrame
```

## 11. Advanced Concepts in DataFrame

### Reading Data From a CSV File

#### What is a CSV File?

- CSV is a file format that allows storing data in tabular format.
- CSV stands for **comma-separated values**.
- Data fields are most often separated or delimited by a comma.

#### CSV Loading

To load a CSV dataset, use `spark.read.csv()` method:

```python
df = spark.read.csv("path-of-file/fifa_players.csv", inferSchema=True, header=True)
```

**Parameters:**
- `inferSchema` (default: false): Infers the input schema automatically from the data.
- `header` (default: false): Uses the first line as column names.

**Verification:** Run `df.show(2)` to display the first two rows.

### DataFrame Schema

**What is schema?** It's the structure of the DataFrame.

#### Checking the Schema

```python
df.printSchema()
```

**Example output:**

```
root
 |-- ID: integer (nullable = true)
 |-- Name: string (nullable = true)
 |-- Age: integer (nullable = true)
 |-- Nationality: string (nullable = true)
 |-- Overall: integer (nullable = true)
 |-- Potential: integer (nullable = true)
 |-- Club: string (nullable = true)
 |-- Value: string (nullable = true)
 |-- Wage: string (nullable = true)
 |-- Special: integer (nullable = true)
```

## 12. Column Names and Count

### Getting Column Information

```python
# Get column names
df.columns
# Output: ['ID', 'Name', 'Age', 'Nationality', 'Overall', 'Potential', 'Club', 'Value', 'Wage', 'Special']

# Get row count
df.count()
# Output: 17981

# Get column count
len(df.columns)
# Output: 10
```

## 13. Describing Columns

To get a summary of any particular column, use the `describe()` method:

```python
df.describe('Name').show()
```

**Example output:**

```
+-------+-------------+
|summary|         Name|
+-------+-------------+
|  count|        17981|
|   mean|         null|
| stddev|         null|
|    min|     A. Abbas|
|    max|Óscar Whalley|
+-------+-------------+
```

### Describing Different Columns

```python
df.describe('Age').show()
```

**Example output:**

```
+-------+------------------+
|summary|               Age|
+-------+------------------+
|  count|             17981|
|   mean|25.144541460430453|
| stddev| 4.614272345005111|
|    min|                16|
|    max|                47|
+-------+------------------+
```

## 14. Selecting Multiple Columns

To select particular columns from a DataFrame, use the `select()` method:

```python
df.select('Column name 1', 'Column name 2', ..., 'Column name n').show()
```

**Note:** The `show()` method is optional. You can load the result into another DataFrame by equating:

```python
dfnew = df.select('ID', 'Name')
dfnew.show(5)
```

**Example output:**

```
+------+-----------------+
|    ID|             Name|
+------+-----------------+
| 20801|Cristiano Ronaldo|
|158023|         L. Messi|
|190871|           Neymar|
|176580|        L. Suárez|
|167495|         M. Neuer|
+------+-----------------+
only showing top 5 rows
```

## 15. Filtering Data

To filter data, use the `filter()` method:

```python
df.filter(df.Club == 'FC Barcelona').show(3)
```

**Example output:**

```
+------+----------+---+-----------+-------+---------+------------+------+-----+-------+
|    ID|      Name|Age|Nationality|Overall|Potential|        Club| Value| Wage|Special|
+------+----------+---+-----------+-------+---------+------------+------+-----+-------+
|158023|  L. Messi| 30|  Argentina|     93|       93|FC Barcelona| €105M|€565K|   2154|
|176580| L. Suárez| 30|    Uruguay|     92|       92|FC Barcelona|  €97M|€510K|   2291|
|168651|I. Rakitić| 29|    Croatia|     87|       87|FC Barcelona|€48.5M|€275K|   2129|
+------+----------+---+-----------+-------+---------+------------+------+-----+-------+
only showing top 3 rows
```

### Filtering with Multiple Conditions

```python
df.filter((df.Club == 'FC Barcelona') & (df.Nationality == 'Spain')).show(3)
```

**Example output:**

```
+------+---------------+---+-----------+-------+---------+------------+-----+-----+-------+
|    ID|           Name|Age|Nationality|Overall|Potential|        Club| Value| Wage|Special|
+------+---------------+---+-----------+-------+---------+------------+-----+-----+-------+
|152729|          Piqué| 30|      Spain|     87|       87|FC Barcelona|€37.5M|€240K|   1974|
|    41|        Iniesta| 33|      Spain|     87|       87|FC Barcelona|€29.5M|€260K|   2073|
|189511|Sergio Busquets| 28|      Spain|     86|       86|FC Barcelona|  €36M|€250K|   1998|
+------+---------------+---+-----------+-------+---------+------------+-----+-----+-------+
only showing top 3 rows
```

Similar logical operators can be used (OR, NOT, etc.).

## 16. Sorting Data (OrderBy)

To sort data, use the `orderBy()` method. By default, it sorts in ascending order:

```python
df.filter((df.Club == 'FC Barcelona') & (df.Nationality == 'Spain')).orderBy('ID').show(5)
```

To sort in descending order:

```python
df.filter((df.Club == 'FC Barcelona') & (df.Nationality == 'Spain')).orderBy('ID', ascending=False).show(5)
```

**Example output (ascending):**

```
+------+---------------+---+-----------+-------+---------+------------+-----+-----+-------+
|    ID|           Name|Age|Nationality|Overall|Potential|        Club| Value| Wage|Special|
+------+---------------+---+-----------+-------+---------+------------+-----+-----+-------+
|    41|        Iniesta| 33|      Spain|     87|       87|FC Barcelona|€29.5M|€260K|   2073|
|152729|          Piqué| 30|      Spain|     87|       87|FC Barcelona|€37.5M|€240K|   1974|
|189332|     Jordi Alba| 28|      Spain|     85|       85|FC Barcelona|€30.5M|€215K|   2206|
|189511|Sergio Busquets| 28|      Spain|     86|       86|FC Barcelona|  €36M|€250K|   1998|
|199564|  Sergi Roberto| 25|      Spain|     81|       86|FC Barcelona|€19.5M|€140K|   2071|
+------+---------------+---+-----------+-------+---------+------------+-----+-----+-------+
only showing top 5 rows
```

## 17. Random Data Generation

Random data generation is useful for testing algorithms and implementing new ones.

In Spark `sql.functions`, methods are available to generate random data: `uniform` (rand) and standard normal (randn).

```python
from pyspark.sql.functions import rand, randn

df = sqlContext.range(0, 7)
df.show()
```

**Example output:**

```
+---+
| id|
+---+
|  0|
|  1|
|  2|
|  3|
+---+
```

### Generating Random Columns

```python
df.select("id", rand(seed=10).alias("uniform"), 
          randn(seed=27).alias("normal")).show()
```

**Example output:**

```
+---+-------------------+-------------------+
| id|            uniform|             normal|
+---+-------------------+-------------------+
|  0|0.41371264720975787| 0.5888539012978773|
|  1| 0.1982919638208397|0.06157382353970104|
|  2|0.12030715258495939| 1.0854146699817222|
|  3|0.44292918521277047|-0.4798519469521663|
+---+-------------------+-------------------+
```

## 18. Summary and Descriptive Statistics

The first operation after importing data is to understand what it looks like. The `describe()` function returns a DataFrame with information such as:

- Number of non-null entries (count)
- Mean, standard deviation
- Minimum and maximum values for each numerical column

```python
df.describe('uniform', 'normal').show()
```

**Example output:**

```
+-------+-------------------+--------------------+
|summary|            uniform|              normal|
+-------+-------------------+--------------------+
|  count|                 10|                  10|
|   mean| 0.3841685645682706|-0.15825812884638607|
| stddev|0.31309395532409323|   0.963345903544872|
|    min|0.03650707717266999| -2.1591956435415334|
|    max| 0.8898784253886249|  1.0854146699817222|
+-------+-------------------+--------------------+
```

### Using Standard Statistical Functions

```python
from pyspark.sql.functions import mean, min, max

df.select([mean('uniform'), min('uniform'), max('uniform')]).show()
```

**Example output:**

```
+------------------+-------------------+------------------+
|      avg(uniform)|       min(uniform)|      max(uniform)|
+------------------+-------------------+------------------+
|0.3841685645682706|0.03650707717266999|0.8898784253886249|
+------------------+-------------------+------------------+
```

## 19. Sample Co-Variance and Correlation

### Co-Variance

In statistics, co-variance measures how one random variable changes with respect to another:

- **Positive value:** Indicates a trend in increase when the other increases.
- **Negative value:** Indicates a trend in decrease when the other increases.

```python
from pyspark.sql.functions import rand

df = sqlContext.range(0, 10).withColumn('rand1', rand(seed=10)).withColumn('rand2', rand(seed=27))
df.stat.cov('rand1', 'rand2')
# Output: 0.031109767020625314
```

From this result, we can infer that the co-variance of two random columns is near zero.

### Correlation

Correlation provides the statistical dependence of two random variables:

```python
df.stat.corr('rand1', 'rand2')
# Output: 0.30842745432650953
```

Two randomly generated columns have a low correlation value.

## 20. Cross Tabulation (Contingency Table)

Cross Tabulation provides a frequency distribution table for a given set of variables. It's a powerful statistical tool to observe the statistical independence of variables.

### Example

```python
# Create a DataFrame with two columns (name, item)
names = ["Alice", "Bob", "Mike"]
items = ["milk", "bread", "butter", "apples", "oranges"]
df = sqlContext.createDataFrame([(names[i % 3], items[i % 5]) for i in range(100)], 
                                ["name", "item"])

# Apply cross tabulation
df.stat.crosstab("name", "item").show()
```

**Example output:**

```
+---------+------+-----+------+----+-------+
|name_item|apples|bread|butter|milk|oranges|
+---------+------+-----+------+----+-------+
|      Bob|     6|    7|     7|   6|      7|
|     Mike|     7|    6|     7|   7|      6|
|    Alice|     7|    7|     6|   7|      7|
+---------+------+-----+------+----+-------+
```

**Note:** Cardinality of columns you run crosstab on cannot be too large.

## 21. Spark SQL - Advanced

Spark SQL brings native support for SQL to Spark and blurs the lines between RDDs and relational tables. By integrating these powerful features, Spark makes it easy for developers to:

- Use SQL commands for querying external data
- Perform complex analytics
- All within a single application

### Performing SQL Queries

You can pass SQL queries directly to any DataFrame. First, create a table from the DataFrame using the `createOrReplaceTempView()` method:

```python
df.createOrReplaceTempView("table_name")
result = spark.sql("SELECT * FROM table_name WHERE condition")
result.show()
```

## 22. Apache Hive

Apache Hive is data warehouse software that allows:

- Managing large datasets residing in distributed storage
- Reading and writing these datasets
- Querying using SQL-like queries
