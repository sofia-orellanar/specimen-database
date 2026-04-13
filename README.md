# Invertebrate Species Database for the Cunha Lab

This project's goal is to build a SQL database that combines invertebrate species sample data across multiple spreadsheets to make accessing this data easier. After running the included scripts, users will have a database file that can be accessed through Python scripts or various extensions as the user prefers.

---
## Required Tools

* [**Python**](https://www.python.org/downloads/) version 3.12.3 or higher 
* **SQLite3** : usually pre-installed with Python
* **pandas**: install by running:

      pip install pandas
* **VSCode** with the extension **VSQLite Explorer**  (recommended for database use)
    * Other options for viewing and accessing the database after building are included under the **Accessing Database** section of this ReadMe.
---

## Cloning the Repository

In your desired directory, run:

    git clone https://github.com/shiizue/specimen-database.git

Then navigate into the project folder:

    cd specimen-database

---

## Step 1: Build the Initial Database (Panama 2021)

The database is structured according to the Panama2021 dataset (all files under Panama2021-Main-Dataset). To build the initial database, run the `TEST_panama_clean_load.py` script in the **TEST-database-scripts** folder:

    python3 TEST-database-scripts/TEST_panama_clean_load.py

After running this script, you should have a file called `TEST_cunha_invertebrate_specimens.db` and see a total of rows reported as:

| Table | Expected rows |
|---|---|
| EventData | 33 |
| SpecimenData | 1105 |
| DNAExtractions | 782 |
| GenomicLibraries | 11 |

You should also see a new file appear at:

    TEST-database-scripts/TEST_cunha_invertebrate_specimens.db

> **Note:** It is important that the Panama script is loaded _before_ the La Palma script, as the latter depends on the former building the expected schema for the database.

---

## Step 2: Add the La Palma 2023 Dataset

After building the initial database, you can add the data from the La Palma dataset (all files under LaPalma2023-Main-Dataset) by running the `TEST_la_palma_clean_load.py` script:

    python3 TEST-database-scripts/TEST_la_palma_clean_load.py

There should be the following numbers reported for rows loaded into each table:

| Table | Expected rows added |
|---|---|
| EventData | 16 |
| SpecimenData | 86 |
| DNAExtractions | 34 |

> **Important:** This script depends on the database created in Step 1. If you run it without completing Step 1 first, you will get an error.

---

## Step 3: Test the Verification and Loading Script

`TEST_verify_and_load.py` is an interactive script for safely adding new data to the existing database. It validates your CSV before inserting anything, and will clearly report any errors or warnings it finds. Use the provided test CSV files to see how it handles different scenarios.

Run the script with:

    python3 TEST-database-scripts/TEST_verify_and_load.py

The script will prompt you to:
1. **Choose a table** to load into (enter the number corresponding to the table)
2. **Enter the path** to your CSV file

### Test Cases

We have provided five CSV files in the `TEST-database-scripts/` folder to walk you through different scenarios. Run the script once for each test file and note what output you receive.

---

**Test 1: Valid event data** (`test_01_event_valid.csv`)

Load into: `EventData`

This file is well-formatted and should pass all validation checks without errors or warnings.

*Expected result:* All 7 validation checks pass and 4 rows are inserted into EventData.

---

**Test 2:  Valid specimen data** (`test_02_specimen_valid.csv`)

Load into: `SpecimenData`

This file contains 5 specimens that all reference event codes loaded in Test 1.

*Expected result:* All validation checks pass and 5 rows are inserted into SpecimenData.

> **Note:** Run Test 1 before Test 2, since the specimen rows reference event codes from Test 1. Running them out of order will cause a foreign key error (which is itself a useful thing to observe — you can try it intentionally if you like).

---

**Test 3: Specimen data with bad foreign keys** (`test_03_specimen_bad_foreign_key.csv`)

Load into: `SpecimenData`

Two rows in this file reference event codes that do not exist in the database (`TEST-5555`, `FAIL-EVENT`).

*Expected result:* A **fatal error** is reported for the foreign key violations, the invalid rows are saved to a separate CSV for review, and **no data is inserted**. The script should exit without modifying the database.

---

**Test 4: Event data with multiple problems** (`test_04_event_multiple_problems.csv`)

Load into: `EventData`

This file contains several issues: a duplicate primary key within the CSV, a missing primary key value (empty `event_code`), and an unrecognized column (`speices_target`).

*Expected result:* Multiple errors and warnings are reported. Fatal errors should block insertion. The warning about the unrecognized column should still be flagged but will not block loading on its own.

---

**Test 5: DNA extraction data with missing required column** (`test_05_dna_missing_required_column.csv`)

Load into: `DNAExtractions`

This file is missing the required `extraction_id` column (the primary key for that table).

*Expected result:* A **fatal error** is reported for the missing required column and no data is inserted.

---

## Step 4: Run the Example Queries

To verify the database is working correctly, we have included two example queries to run and check with expected output. These queries can be ran through the VSQLite Explorer (see Accessing the Database below) query editor function, or through the test_query1.py and test_query2.py scripts in the database-scripts directory.

**Test Query 1:** counts the number of specimens per species, returning the top 10:

> ```
> SELECT species, COUNT(*) AS specimen_count
    FROM SpecimenData
    GROUP BY species
    ORDER BY specimen_count DESC
    LIMIT 10
> ```

To run the Python script:

    python3 TEST-database-scripts/test_query1.py

The correct output for this query is saved in `TEST-database-scripts/check_query1.csv` for comparison.

**Test Query 2**: returns voucher number, species, extraction date, and DNA concentration for samples with a Qubit concentration above 100 ng/µL that have been deposited in a museum:

> ```
> SELECT voucher, species, extraction_date, qubit_dna_ng_ul
    FROM SpecimenData
    JOIN EventData on SpecimenData.event_code = EventData.event_code
    JOIN DNAExtractions on SpecimenData.lot_id= DNAExtractions.lot_id
    WHERE qubit_dna_ng_ul > 100 AND Voucher != 'NA'
    ORDER BY Qubit_DNA_ng_ul DESC
    ```

To run the Python script:

    python3 TEST-database-scripts/test_query2.py

The correct output for this query is saved in `TEST-database-scripts/check_query2.csv` for comparison.

---

## Accessing the Database

There are several ways to view and interact with the `.db` file directly:

- **VSCode + SQLite Explorer extension** (recommended): lets you browse tables, edit entries, and execute queries through a GUI without writing Python
- **DB Browser for SQLite**: a standalone desktop app available at [https://sqlitebrowser.org/](https://sqlitebrowser.org/) (NOT TESTED as of 4/13/26)
- **Python scripts**: run SQL commands directly using `sqlite3` and `pandas`, as shown in the example query scripts

---

## Writing SQL Queries

This [GitHub](https://github.com/enochtangg/quick-SQL-cheatsheet) includes a detailed summary on various statements that can be used in SQL queries to filter, sort, and aggregate data. We have included some basic information on writing SQL queries below, but recommend SQL documentation, such as the above link, for more details.

A basic SQL query uses the following structure:

```sql
SELECT column_name
FROM table_name
JOIN other_table ON table_name.shared_column = other_table.shared_column
WHERE column_name <condition>
```

* **SELECT column_name**: select columns to be reported from the database as a whole
* **FROM table_name**: selects the table that is initially accessed (for this database, the central table is SpecimenData)
* **JOIN alt_table on table.common_col = alt_table.common_col**: joins tables along a common identifier for accessing information in a different table.
* **WHERE column_name \<condition\>**: filters rows by if a value in the named column fits a particular condition. These statements can use any logical operator, including inequalities, AND, OR, NOT, BETWEEN and IS NULL. 
