# Invertebrate Species Database for the Cunha Lab
This project's goal is to build a SQL database that combines invertebrate species sample data across multiple spreadsheets to make accessing this data easier. After running the included scripts, users will have a database file that can be accessed through Python scripts or various extensions as the user prefers.

### Required Tools
* **Python** version 3.12.3
* **SQLite3** : usually pre-installed with Python
* (recommended for database use) **VSCode** with the extension **VSQLite Explorer**
    * Other options for viewing and accessing the database after building are included under the **Accessing Database** section of this ReadMe.

## Cloning Repository
In your desired directory, run the command:

    git clone https://github.com/shiizue/specimen-database.git

## Building Initial Database
The database is structured according to the Panama2021 dataset (all files under Panama2021-Main-Dataset). To build the initial database, run the panama_clean_load.py script in the database-scripts folder:

    python3 database-scripts/panama_clean_load.py

After running this script, you should have a file called "cunha_invertebrate_specimens.db" and see a total of rows reported as 33 rows in EventData, 1105 rows in SpecimenData, 782 rows in DNAExtractions, and 11 rows in GenomicLibraries. 

## Accessing Database
### Viewing Database
There are various ways to view the database file (.db) file. We recommend using the VSQLite Explorer extension through VSCode. This extension is open access and allows the user to view each table, edit entries, and execute queries in a more intuitive way.

Other options include:
* Running SQL commands through Python scripts
* DB Browser for SQLite https://sqlitebrowser.org/ (not tested as of 4/8/2026)
### Adding Additional Datasets
After building the initial database, you can add the data from the La Palma dataset (all files under LaPalma2023-Main-Dataset) by running the la_palma_clean_load.py script:

    python3 database-scripts/la_palma_clean_load.py

There should be the following numbers reported for rows loaded into each table: 16 in EventData, 86 in SpecimenData, and 34 in DNAExtractions.

**Note:** Once other datasets are obtained, we will include a generalized script for identifying missing column names as demonstrated in the output in the la_palma_clean_load.py script. 

### SQL Queries
SQL queries allow the user to filter and report data from the database, accessing columns from multiple tables for a particular condition.

**Writing SQL Queries**

This [GitHub](https://github.com/enochtangg/quick-SQL-cheatsheet) includes a detailed summary on various statements that can be used in SQL queries to filter, sort, and aggregate data. We have included some basic information on writing SQL queries below, but recommend SQL documentation, such as the above link, for more details.

A basic SQL query uses SELECT, FROM, JOIN and WHERE statements to filter data and select particular rows and columns. 
* **SELECT column_name**: select columns to be reported from the database as a whole
* **FROM table_name**: selects the table that is initially accessed (for this database, the central table is SpecimenData)
* **JOIN alt_table on table.common_col = alt_table.common_col**: joins tables along a common identifier for accessing information in a different table.
* **WHERE column_name \<condition\>**: filters rows by if a value in the named column fits a particular condition. These statements can use any logical operator, including inequalities, AND, OR, NOT, BETWEEN and IS NULL. 

**Example Queries**


### Editing Entries
