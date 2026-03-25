import sqlite3
import pandas as pd

### AS OF 3/18/2026:
    # this script builds the Panama database fromm the 4 supplied csv files, including:
        #removing unnecessary columns, checking for missing data, adding placeholders for missing data, renaming column names to be SQl compatible
    # queries.py supplies some example queries and basic info on writing queries

### TO DO NEXT:
    # automate/generalize the data cleaning parts
    # fix the case of all column names to be all lowercase ? (check with Skye and Sofi)
    # ask Dr. Cunha about event PAN22E034 
    # start cleaning the La Palma data to match this data

path = "/home/gfinger/specimen-database/"
datafolder= "Panama2021-Main-Dataset/"
csv_files= ["Panama2021-EventData", "Panama2021-SpecimenData", "Panama2021-DNAextractions","Panama2021-GenomicLibraries"]

##################################################
### CLEANING EVENT DF ###
event_df = pd.read_csv(path + datafolder + "Panama2021-EventData.csv")

#PAN22E034 is missing from event_df
'''
print("Event codes in event_df:")
print(set(event_df["event_code"]))

print("\nEvent codes in specimen_df:")
print(set(specimen_df["event_code"]))

# Find mismatches
missing = set(specimen_df["event_code"]) - set(event_df["event_code"])
print("\nMissing event_codes (cause of error):")
print(missing)'''

#adding row for missing event code
columns_edf= list(event_df.columns)
missingecode = "PAN22E034"
missingrow= {}
for col in columns_edf:
    missingrow[col] = 'unknown'
missingrow['event_code'] = missingecode
new_row_df = pd.DataFrame([missingrow])
event_df = pd.concat([event_df, new_row_df], ignore_index=True)

#removing unnecessary columns
event_df = event_df.drop(labels= ['use_in_map','photos_env'],axis=1)

#renaming notes column to event_notes so no duplicate when querying
event_df= event_df.rename(columns={'notes': 'event_notes'})

##################################################
# CLEANING SPECIMEN DF
specimen_df = pd.read_csv(path + datafolder + "Panama2021-SpecimenData.csv")

#removing unnecessary column
specimen_df= specimen_df.drop(labels='Unnamed: 20',axis = 1)

#renaming notes to specimen_notes
specimen_df= specimen_df.rename(columns={'notes':'specimen_notes'})

#adding field_group column and 'museum' column
specimen_df['field_group']= "Panama"
specimen_df.loc[specimen_df['Voucher'].notnull(), 'museum'] = "Smithsonian"


##########################################
### CLEANING dna_df
dna_df = pd.read_csv(path + datafolder+ "Panama2021-DNAextractions.csv")

dna_df= dna_df.rename(columns={'Qubit_DNA_[ng/ul]':'Qubit_DNA_ng_ul', "Nanodrop_[ng/ul]":"Nanodrop_ng_ul", "Qubit : Nanodrop": "Qubit_Nanodrop","Nanodrop_260/280":"Nanodrop_260_280","Nanodrop_260/230":"Nanodrop_260_230"})

#used this code chunk to make sure there are no lot_ids in dna_df that point to nothing in specimen_df
'''print("Lot IDs in specimen_df:")
print(set(specimen_df["lot_id"]))

print("\nLot IDs in dna_df:")
print(set(dna_df["lot_id"]))

# Find mismatches
missing = set(dna_df["lot_id"]) - set(specimen_df["lot_id"])
print("\nMissing event_codes (cause of error):")
print(missing)'''
##################################################
### CLEANING EVENT DF ###
libraries_df = pd.read_csv(path + datafolder + "Panama2021-GenomicLibraries.csv")
libraries_df = libraries_df.rename(columns={'Qubit_DNA_[ng/ul]':'Qubit_DNA_ng_ul_lib','Qubit_lib_[ng/ul]':'Qubit_lib_ng_ul','IDT xGen UDI Primer Pair Well':'IDTxGen_UDI_PrimerPair_Well','Primer Name':'Primer_Name', 'i5 index': 'i5_index', 'i7 index': 'i7_index','[C]_nM_estimate':'C_nM_estimate','Qubit_size-selection_[ng/ul]': 'Qubit_size_selection_ng_ul'})

#used this code chunk to make sure there are no lot_ids in dna_df that point to nothing in specimen_df
'''print("extraction_ids in dna_df:")
print(set(dna_df["extraction_id"]))

print("\nextraction_ids in libraries_df:")
print(set(libraries_df["extraction_id"]))

# Find mismatches
missing = set(libraries_df["extraction_id"]) - set(dna_df["extraction_id"])
print("\nMissing extraction ids:")
print(missing)'''


###################
#used this code chunk to generate column names and TEXT format for creating tables
#at some point we'll probably want to change TEXT to more specific datatypes but that's a later problem
'''columns_edf= list(event_df.columns)
for col in columns_edf:
    print(f'{col} TEXT,')
cols_spec= (list(specimen_df.columns))
for col in cols_spec:
    print(f'{col} TEXT,')'''
'''cols_dna= list(dna_df.columns)
for col in cols_dna:
    print(f'{col} TEXT,')'''
'''cols_libs= list(libraries_df.columns)
for col in cols_libs:
    print(f'{col} TEXT,')'''




##################################################
### BUILDING DATABASE
conn = sqlite3.connect(path + "Panama.db")
conn.execute("PRAGMA foreign_keys = ON")

cursor = conn.cursor()
cursor.execute("""
CREATE TABLE event (
    event_code TEXT PRIMARY KEY,
    trip_id TEXT,
    year INT,
    month INT,
    day INT,
    date DATE,
    waypoint TEXT,
    latitude FLOAT,
    longitude FLOAT,
    environment TEXT,
    low_tide FLOAT,
    collecting_method TEXT,
    depth TEXT,
    population TEXT,
    locality TEXT,
    locality_details TEXT,
    city_district TEXT,
    province TEXT,
    area TEXT,
    country TEXT,
    collector TEXT,
    event_notes TEXT
)
""")
cursor.execute("""
CREATE TABLE specimen (
    lot_id TEXT PRIMARY KEY,
    sufix TEXT,
    event_code TEXT,
    species TEXT,
    genus TEXT,
    epithet TEXT,
    clade TEXT,
    family TEXT,
    development TEXT,
    habitat TEXT,
    fixation_method TEXT,
    specimens INT,
    parts TEXT,
    vial TEXT,
    operculum TEXT,
    specimen_notes TEXT,
    photos_org TEXT,
    identification_by TEXT,
    museum TEXT,
    Voucher TEXT,
    SecondVoucherClip TEXT,
    field_group TEXT,
    FOREIGN KEY (event_code) REFERENCES event(event_code)
)
""")
cursor.execute("""
CREATE TABLE dna (
    extraction_id TEXT PRIMARY KEY,
    lot_id TEXT,
    species TEXT,
    plate_id TEXT,
    plate_well TEXT,
    extraction_date DATE,
    extraction_kit TEXT,
    elution_ul INT,
    Qubit_DNA_ng_ul FLOAT,
    Nanodrop_ng_ul FLOAT,
    Nanodrop_260_280 FLOAT,
    Nanodrop_260_230 FLOAT,
    Qubit_Nanodrop FLOAT,
    clip_over TEXT,
    contamination_plate TEXT,
    contamination_wells TEXT,
    extraction_notes TEXT,
    piece_size TEXT,
    Qubit_after_SpeedVac FLOAT,
    FOREIGN KEY (lot_id) REFERENCES specimen(lot_id)
)
""")
cursor.execute("""
CREATE table libraries (
    library_id TEXT PRIMARY KEY,
    extraction_id TEXT,
    lot_id TEXT,
    species TEXT,
    library_date DATE,
    library_kit TEXT,
    Qubit_DNA_ng_ul_lib TEXT,
    input_mass_ng FLOAT,
    input_vol_ul FLOAT,
    EB_complement_ul FLOAT,
    frag_time_min FLOAT,
    cycles INT,
    elution_ul FLOAT,
    Qubit_lib_ng_ul FLOAT,
    size_selection TEXT,
    Qubit_size_selection_ng_ul TEXT,
    IDTxGen_UDI_PrimerPair_Well TEXT,
    Primer_Name TEXT,
    i5_index TEXT,
    i7_index TEXT,
    Bioanalyzer_avg_size FLOAT,
    insert_size FLOAT,
    C_nM_estimate FLOAT,
    Data_Target_GB FLOAT,
    FOREIGN KEY (extraction_id) REFERENCES dna(extraction_id)
)
""")

#insert data from pandas
event_df.to_sql("event", conn, if_exists="append", index=False)
specimen_df.to_sql("specimen", conn, if_exists="append", index=False)
dna_df.to_sql("dna", conn, if_exists="append", index=False)
libraries_df.to_sql("libraries", conn, if_exists="append",index=False)
