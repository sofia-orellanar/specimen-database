# specimen-database
## database-scripts
- get_blank_csvs.py Generates blank CSV files from the live database schema to use as templates (output to template_CSVs folder)
- verify_and_load.py Validates a given CSV file for expected data from current database schema before automatically loading it into the database
## initial-building-scripts
- panama_clean_load.py Builds initial database file using Panama data
- la_palma_clean_load.py Adds on La Palma data to the database
- add_cols_sql.py Adds additional columns as requested
- fill_taxonomy.py Uses GBIF API to search and automatically add higher taxonomy level information (Up to Order) for each species
## LaPalma2023-Main-Dataset
- LaPalma2023-DNAextractions.csv
- LaPalma2023-EventData.csv
- LaPalma2023-SpecimenData.csv
## Panama2021-Main-Dataset
- Panama2021-DNAextractions.csv
- Panama2021-EventData.csv
- Panama2021-GenomicLibraries.csv
- Panama2021-SpecimenData.csv
## template_CSVs
- TEMPLATE_DNAExtractions.csv
- TEMPLATE_EventData.csv
- TEMPLATE_GenomicLibraries.csv
- TEMPLATE_SpecimenData.csv
## TEST-database-scripts
- TEST_cunha_invertebrate_specimens.db Copy of database file specifically for testing
- TEST_get_blank_csvs.py opy of template CSV generating file specifically for testing
- test_query1.py Query script for testing
- test_query2.py Query script for testing
- TEST_verify_and_load.py Copy of verify and load script specifically for testing
- - test_01_event_valid.csv Test CSV for verify and load script - should pass all checks
- test_02_specimen_valid.csv Test CSV for verify and load script - should pass all checks
- test_03_specimen_bad_foreign_key.csv Test CSV for verify and load script - should fail foreign key validation
- test_04_event_multiple_problems.csv Test CSV for verify and load script - should fail multiple checks
- test_05_dna_missing_required_column.csv Test CSV for verify and load script - should fail required column validation
- check_query1.csv Verify results from test_query1
- check_query2.csv Verify results from test_query2
## user-guides
- advanced_user_guide.pdf
- beginner_user_guide.pdf
- How_to_use_DB_Browser.pdf
.gitignore
README.mdscripts