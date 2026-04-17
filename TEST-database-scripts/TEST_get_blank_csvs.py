import sqlite3
import pandas as pd

############################################
### GETTING CORRECT COLUMN NAMES FROM DB ###
############################################

#connecting to database file
conn = sqlite3.connect('database-scripts/cunha_invertebrate_specimens.db')
cursor = conn.cursor()

#selecting all columns from EventData table and saving in a list
cursor.execute('''SELECT * FROM EventData''')
event_cols = [description[0] for description in cursor.description]

#selecting all columns from DNAExtractions table and saving in a list
cursor.execute('''SELECT * FROM DNAExtractions''')
dna_cols = [description[0] for description in cursor.description]

#selecting all columns from SpecimenData table and saving in a list
cursor.execute('''SELECT * FROM SpecimenData''')
spec_cols = [description[0] for description in cursor.description]

#selecting all columns from GenomicLibraries table and saving in a list
cursor.execute('''SELECT * FROM GenomicLibraries''')
genomlib_cols = [description[0] for description in cursor.description]

#closing connection
conn.close()

################################################
### CREATING DATAFRAMES AND EXPORTING TO CSV ###
################################################

#creating dataframe with columns from database as header row for each table
#for table EventData
event_df = pd.DataFrame(columns=event_cols)
event_df.to_csv('template_CSVs/TEMPLATE_EventData.csv',index=False)

#for table DNAExtractions
event_df = pd.DataFrame(columns=dna_cols)
event_df.to_csv('template_CSVs/TEMPLATE_DNAExtractions.csv',index=False)

#for table SpecimenData
event_df = pd.DataFrame(columns=spec_cols)
event_df.to_csv('template_CSVs/TEMPLATE_SpecimenData.csv',index=False)

#for table GenomicLibraries
event_df = pd.DataFrame(columns=genomlib_cols)
event_df.to_csv('template_CSVs/TEMPLATE_GenomicLibraries.csv',index=False)

print('Success! 4 blank CSV files have been generated with the prefix "TEMPLATE_" in the directory "template_CSVs"')