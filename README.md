# Invertebrate Species Database for the Cunha Lab

This project's goal is to build a SQL database that combines invertebrate specimen data across multiple spreadsheets to make accessing this data easier. After running the included scripts, users will have a database file that can be accessed through Python scripts or various extensions as the user prefers.

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

## Building Initial Database (optional)
A complete database file including data from the Panama 2021 dataset and La Palma 2023 dataset is included in the GitHub repo at `TEST-cunha_invertebrate_specimens.db`. The following two commands are included for transparency, or to rebuild the database file as needed:

`python3 TEST-database-scripts/TEST_panama_clean_load.py`

**Expected Output**:

| Table            | Expected rows |
| ---------------- | ------------- |
| EventData        | 33            |
| SpecimenData     | 1105          |
| DNAExtractions   | 782           |
| GenomicLibraries | 11            |

`python3 TEST-database-scripts/TEST_la_palma_clean_load.py`

**Expected Output:**

| Table          | Expected rows added |
| -------------- | ------------------- |
| EventData      | 16                  |
| SpecimenData   | 86                  |
| DNAExtractions | 34                  |

> **Note:** The database is structured according to the Panama2021 dataset (all files under Panama2021-Main-Dataset). It is important that the Panama script is loaded _before_ the La Palma script, as the latter depends on the former building the expected schema for the database.


## Accessing Database
### Viewing Database
There are various ways to view the database file (.db) file. We recommend using **DB Browswer for SQLite**. This is a free application that allows a user to upload a .db file to browse, query, and edit it. One limitation of this GUI is that it is not a shared file, so one user would be able to access it. Users could coordinate a GitHub page to pull and push database edits, which ensures the integrity of the database if a user makes a mistake. Our user guide for installing and setting up our database file with DB Browser is included in the GitHub.

For other scripts included for this project, any Python IDE is sufficient, but we recommend VScode. 

Other storage options include:
* **Remote Server**: allows multiple users to edit the same database file. When accessed through VSCode, the extension VSQLite Explorer is helpful for browsing and editing. In this case, we recommend using Python scripts to run SQL commands directly using `sqlite3` and `pandas`, as shown in the example query scripts. However, this option is less user friendly to researchers unfamiliar to the command line and writing scripts.
* **Remote Host**: (Laravel Cloud, Google Cloud, etc) allows multiple users to edit and access the database and is stored with a 3rd party service. This often requires a regular fee for storage, but may be an appropriate option depending on the number of researchers needing regular access to the database.

### Adding Single Rows and Columns
**Adding Columns**

To add a column to an existing table in SQL, the basic command format is:
   
```sql
ALTER TABLE table_name 
ADD COLUMN column_name column_definition
```
      
Where the column_definition is the type of data being stored in that column. For example, TEXT or ID. By default, each row will get NULL assigned as the value for the new column; optional is adding a NOT NULL statement to specify a different default value.

For example, to add a column to the SpecimenData table called "common name", which would be stored as text, with 'intervertebrate species' as the default value:

```sql
ALTER TABLE SpecimenData 
ADD COLUMN common_name TEXT 
NOT NULL DEFAULT 'invertebrate species'
```
**Renaming Columns**
To rename a column, the general format for the SQL command is...
```sql
ALTER TABLE table_name
RENAME COLUMN old_name TO new_name
```
For example, to fix a typo that mispelled "suffix" as "sufix", the following command would alter the column name to the correct spelling.

```sql
ALTER TABLE LoanedSpecimens 
RENAME COLUMN sufix TO suffix
```

**Adding Rows**
To add an additional entry (row) to an existing table, the basic command format is:

```sql
INSERT INTO table_name (columnA, columnB, columnC) 
VALUES (value1, value2, value3)
```

Multiple rows can be added by separating the lists of values by commas. Each new entry must have a unique primary key to be added, and if using a foreign key, that foreign key must previously exist in the database.

For example, to add the following two rows...

| lot_id | genus |  species |
|--------|-------|----------|
dummy_01 | Mesonychoteuthis | hamiltoni |
dummy_02 |  Haemopis  |  sanguisuga |

to the SpecimenData table:

```sql
INSERT INTO SpecimenData (lot_id, genus, species) 
VALUES ('dummy_01', 'Mesonychoteuthis', 'hamiltoni'), ('dummy_02', 'Haemopis', 'sanguisuga')
```
### Editing an Individual Entry
Many GUIs for SQL databases enable users to simply click and type in a cell that they want to change, including VSQLite Explorer through VSCode. 

To edit an existing entry using SQL, the basic format is:

```sql
UPDATE table_name 
SET columnA= value1, columnB = value 2 
WHERE condition
```

For example, to update the dummy_01 row above to include the common_name and collected_by columns:

```sql
UPDATE SpecimenData 
SET common_name = "Colossal Squid", collected_by= "LU Wolf" 
WHERE lot_id == "dummy_01"
```

### Adding a New Table
To add an additional table, the basic format for the SQL command is...
First, to create the new table:
```sql
CREATE TABLE IF NOT EXISTS table_name (
    column_1 data_type PRIMARY KEY,
    column_2 data_type,
)
```

For example, if you wanted a table to keep track of specimens on loan from a museum with the following format and entries...

| voucher | museum | genus | species | date_borrowed | returned_bool | date_returned
|---------|--------|--------|--------|--------|--------|--------|
|SNHM0001 | Smithsonian | Mesonychoteuthis | hamiltoni | 04-05-2026 | False | |
| FMNH0002 | Field | Haemopis | sanguisuga | 04-15-2026 | True | 04-29-26 |

In this case, the primary key (or unique identifier) would be the voucher number. Since these specimens are separate from the specimens collected by the Cunha lab, there are no foreign keys for this table.

First, to create the new table:
```sql
CREATE TABLE IF NOT EXISTS LoanedSpecimens (
    voucher TEXT PRIMARY KEY,
    museum TEXT,
    genus TEXT,
    species TEXT,
    date_borrowed TEXT,
    returned_bool TEXT,
    date_returned TEXT
)
```

Then, after the table has been created, you can follow the instructions above for adding individual rows into an existing table. For example, to add the example entries shown above...
```sql
INSERT INTO LoanedSpecimens (voucher, museum, genus, species, date_borrowed, returned_bool, date_returned) 
VALUES 
('SNHM0001', 'Smithsonian', 'Mesonychoteuthis','hamiltoni', '04-05-2026','False', 'NULL'), 
('FMNH0002', 'Field', 'Haemopis', 'sanguisuga','04-15-2026','True', '04-29-26');
```

## Adding Additional Datasets
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


## Run the Example Queries

To verify the database is working correctly, we have included two example queries to run and check with expected output. These queries can be run through the VSQLite Explorer (see Accessing the Database above) query editor function, or through the test_query1.py and test_query2.py scripts in the database-scripts directory.

**Test Query 1:** counts the number of specimens per species, returning the top 10:

```sql
SELECT species, COUNT(*) AS specimen_count
FROM SpecimenData
GROUP BY species
ORDER BY specimen_count DESC
LIMIT 10
```

To run the Python script:

    python3 TEST-database-scripts/test_query1.py

The correct output for this query is saved in `TEST-database-scripts/check_query1.csv` for comparison.

**Test Query 2**: returns voucher number, species, extraction date, and DNA concentration for samples with a Qubit concentration above 100 ng/µL that have been deposited in a museum:

```sql
SELECT voucher, species, extraction_date, qubit_dna_ng_ul
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



## Generating Blank CSV Files
In the directory "template_CSVs", there are blank CSVs created for the database as it was structured on 4/12/2026. This is to minimize the amount of manual column name edits users will have to make to input new CSV files into the existing database.

To generate new blank CSV files based on the current column names for each table, run the script "get_blank_csvs.py"

    python3 TEST-database-scripts/TEST-get_blank_csvs.py

These CSV files can be opened as Excel files for easy use during data collection, and then exported as CSV files to add to database after data is recorded.
