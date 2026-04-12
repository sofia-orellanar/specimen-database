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

## Building Initial Database (optional)
A complete database file including data from the Panama 2021 dataset and La Palma 2023 dataset is included in the GitHub repo. The following two commands are included for transparency, or to rebuild the database file as needed.

The database is structured according to the Panama2021 dataset (all files under Panama2021-Main-Dataset). To build the initial database, run the panama_clean_load.py script in the database-scripts folder:

    python3 database-scripts/panama_clean_load.py

After running this script, you should have a file called "cunha_invertebrate_specimens.db" and see a total of rows reported as 33 rows in EventData, 1105 rows in SpecimenData, 782 rows in DNAExtractions, and 11 rows in GenomicLibraries. 

After building the initial database, you can add the data from the La Palma dataset (all files under LaPalma2023-Main-Dataset) by running the la_palma_clean_load.py script:

    python3 database-scripts/la_palma_clean_load.py

There should be the following numbers reported for rows loaded into each table: 16 in EventData, 86 in SpecimenData, and 34 in DNAExtractions.

## Accessing Database
### Viewing Database
There are various ways to view the database file (.db) file. We recommend using the VSQLite Explorer extension through VSCode. This extension is open access and allows the user to view each table, edit entries, and execute queries and commands in a more intuitive way without using an intermediate Python script.

Other options include:
* Running SQL commands through Python scripts
* DB Browser for SQLite https://sqlitebrowser.org/ (not tested as of 4/8/2026)

### Adding Single Rows and Columns
**Adding Columns**

To add a column to an existing table in SQL, the basic command format is:
   
    ALTER TABLE table_name ADD COLUMN column_name column_definition
Where the column_definition is the type of data being stored in that column. For example, TEXT or ID. By default, each row will get NULL assigned as the value for the new column; optional is adding a NOT NULL statement to specify a different default value.

For example, to add a column to the SpecimenData table called "common name", which would be stored as text, with 'intervertebrate species' as the default value:

    ALTER TABLE SpecimenData ADD COLUMN common_name TEXT NOT NULL DEFAULT 'invertebrate species'

**Adding Rows**
To add an additional entry (row) to an existing table, the basic command format is:

    INSERT INTO table_name (columnA, columnB, columnC) VALUES (value1, value2, value3)

Multiple rows can be added by separating the lists of values by commas. Each new entry must have a unique primary key to be added, and if using a foreign key, that foreign key must previously exist in the database.

For example, to add the following two rows...

    lot_id  genus   species
    dummy_01    Mesonychoteuthis    hamiltoni
    dummy_02    Haemopis    sanguisuga

to the SpecimenData table:

    INSERT INTO SpecimenData (lot_id, genus, species) VALUES ('dummy_01', 'Mesonychoteuthis', 'hamiltoni'), ('dummy_02', 'Haemopis', 'sanguisuga')

### Editing an Individual Entry
Many GUIs for SQL databases enable users to simply click and type in a cell that they want to change, including VSQLite Explorer through VSCode. 

To edit an existing entry using SQL, the basic format is:

    UPDATE table_name SET columnA= value1, columnB = value 2 WHERE condition

For example, to update the dummy_01 row above to include the common_name and collected_by columns:

    UPDATE SpecimenData SET common_name = "Colossal Squid", collected_by= "LU Wolf" WHERE lot_id == "dummy_01"


### Adding Additional Datasets
**Documentation for verify_and_load.py goes HERE**

### SQL Queries
SQL queries allow the user to filter and report data from the database, accessing columns from multiple tables for a particular condition.

**Writing SQL Queries**

This [GitHub](https://github.com/enochtangg/quick-SQL-cheatsheet) includes a detailed summary on various statements that can be used in SQL queries to filter, sort, and aggregate data. We have included some basic information on writing SQL queries below, but recommend SQL documentation, such as the above link, for more details.

A basic SQL query uses SELECT, FROM, JOIN and WHERE statements to filter data and select particular rows and columns. 
* **SELECT column_name**: select columns to be reported from the database as a whole
* **FROM table_name**: selects the table that is initially accessed (for this database, the central table is SpecimenData)
* **JOIN alt_table on table.common_col = alt_table.common_col**: joins tables along a common identifier for accessing information in a different table.
* **WHERE column_name \<condition\>**: filters rows by if a value in the named column fits a particular condition. These statements can use any logical operator, including inequalities, AND, OR, NOT, BETWEEN and IS NULL. 

**Running Queries**
To ensure the database is working properly, we have included 2 example queries to run and check with correct output. These queries can be ran through the VSQLite Explorer query editor function, or through the test_query1.py and test_query2.py scripts in the database-scripts directory.

Test Query 1:

    SELECT species, COUNT(*) AS specimen_count
    FROM SpecimenData
    GROUP BY species
    ORDER BY specimen_count DESC
    LIMIT 10

To run the Python script:

    python3 database-scripts/test_query1.py

This query counts the number of specimens for each sample and returns the top 10 species and their counts. The correct output for running this query is included under database-scripts/check_query1.csv

Test Query 2:

    SELECT voucher, species, extraction_date, qubit_dna_ng_ul
    FROM SpecimenData
    JOIN EventData on SpecimenData.event_code = EventData.event_code
    JOIN DNAExtractions on SpecimenData.lot_id= DNAExtractions.lot_id
    WHERE qubit_dna_ng_ul > 100 AND Voucher != 'NA'
    ORDER BY Qubit_DNA_ng_ul DESC

To run the Python script:

    python3 database-scripts/test_query1.py

This query reports the voucher number, species, extraction date and concentration for samples that have a Qubit concentration greater than 100 ng/ul and have been depoited in a museum (if they have a voucher) The correct output for running this query is included under database-scripts/check_query2.csv


## Generating Blank CSV Files
In the directory "template_CSVs", there are blank CSVs created for the database as it was structured on 4/12/2026. This is to minimize the amount of manual column name edits users will have to make to input new CSV files into the existing database.

To generate new blank CSV files based on the currenty column names for each table, run the script "get_blank_csvs.py"

    python3 database-scripts/get_blank_csvs.py

These CSV files can be opened as Excel files for easy use during data collection, and then exported as CSV files to add to database after data is recorded.