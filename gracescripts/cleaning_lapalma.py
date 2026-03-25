import sqlite3
import pandas as pd

path = "LaPalma2023-Main-Dataset/"

### READING IN FILES
event_df= pd.read_csv(path + "LaPalma2023-EventData.csv")
specimen_df= pd.read_csv(path + "LaPalma2023-SpecimenData.csv")
dna_df= pd.read_csv(path + "LaPalma2023-DNAextractions.csv")


### GETTING CORRECT COLUMN NAMES FROM DB ###
conn = sqlite3.connect('panama_scripts/panama_specimens.db')
cursor = conn.cursor()

cursor.execute('''SELECT * FROM EventData''')

# Extract column names from cursor.description
event_cols = [description[0] for description in cursor.description]

conn.close()

conn = sqlite3.connect('panama_scripts/panama_specimens.db')
cursor = conn.cursor()

cursor.execute('''SELECT * FROM DNAExtractions''')


dna_cols = [description[0] for description in cursor.description]

conn.close()

conn = sqlite3.connect('panama_scripts/panama_specimens.db')
cursor = conn.cursor()
cursor.execute('''SELECT * FROM SpecimenData''')
spec_cols = [description[0] for description in cursor.description]

conn.close()
########################################################################
### DATA CLEANING ON EVENT TABLE



############################################################################
### CHECKING IF COLUMNS ARE CORRECT
event_cols_lapalma= list(event_df.columns)
print('--LaPalma--')
print('--Event Table--')
for col in event_cols:
    check= 'Fix name'
    if col not in event_cols_lapalma:
        print(col, check)
print()

spec_cols_lapalma= list(specimen_df.columns)
print('--LaPalma--')
print('--Specimen Table--')
for col in event_cols:
    check= 'Fix name'
    if col not in event_cols_lapalma:
        print(col, check)
print()

dna_cols_lapalma= list(dna_df.columns)
print('--LaPalma--')
print('--DNA Table--')
for col in event_cols:
    check= 'Fix name'
    if col not in event_cols_lapalma:
        print(col, check)
print()