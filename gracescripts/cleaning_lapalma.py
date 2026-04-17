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
event_clean = event_df.rename(
    columns= {
        "TripID": "trip_id",
        "EventCode": "event_code",
        "Year": "year",
        "Month": "month",
        "Day": "day",
        "Date": "date",
        "Waypoint": "waypoint",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Environment": "environment",
        "CollectingMethod": "collecting_method",
        "Depth": "depth",
        "SpecificLocality": "locality_details",
        "Municipality": "city_district",
        "Locality":"locality",
        "Country":"country",
        "Collectors":"collector",
        "EventNotes":"event_notes"
    }
)

missingcols= ['area','province']
for col in missingcols:
    event_clean[col]= None

### DATA CLEANING ON DNA 
dna_clean = dna_df.rename(
    columns= {
        "ExtractionID": "extraction_id",
        "Suffix": "suffix",
        "Voucher": "voucher", #remove
        "Species": "species", #remove
        "Date": "extraction_date",
        "Method":"extraction_kit",
        "Elution_ul": "elution_ul",
        "Qubit_ngul": "qubit_dna_ng_ul",
        "TissueType": "tissue_type",
        "ExtractionNotes": "extraction_notes",
        "ClippingNotes":"clip_over",
        "ExtractedBy": "extracted_by", #remove
        "COI": "COI", #remove
        "Best_Match": "best_match", #need to add to panama
        "Max_Score": "max_score", #need to add to panama
        "Total_Score": "total_score", #need to add to panama
        "Query_Cover": "query_cover", #need to add to panama
        "E-Value": "e_value", #need to add to panama
        "Percent_Identity": "percent_identity", #need to add to panama
        "Match_Length": "match_length", #need to add to panama
        "Match_Accession": "match_accession", #need to add to panama
    }
)
add_to_pan= [
    "best_match",
    "max_score",
    "total_score",
    "query_cover",
    "e_value",
    "percent_identity",
    "match_length",
    "match_accession",
    "suffix",
    "tissue_type",
]
cols_missing= [
    "nanodrop_ng_ul", 
    "nanodrop_260_280",
    "nanodrop_260_230",
    "qubit_nanodrop_ratio", 
    "contamination_plate" , 
    "contamination_wells", 
    "piece_size",
    "qubit_after_speedvac",
    "lot_id"]
for col in cols_missing:
    dna_clean[col]= None

to_remove = [
    "voucher",
    "species",
    "COI",
    "extracted_by",
    "PCRBy"
]
for col in to_remove:
    dna_clean = dna_clean.loc[:, ~dna_clean.columns.str.startswith(col)]
print(dna_clean.columns)

specimen_clean = specimen_df.rename(columns={
    "SampleCode":    "lot_id",            # PRIMARY KEY
    "EventCode":     "event_code",        # FOREIGN KEY (EventData)
    "Species":       "species",
    "Specimens":     "specimen_count",  
    "Parts":         "parts",
    "FixationMethod":"fixation_method",
    "Family":        "family",
    "Habitat":       "habitat",
    "IdentifiedBy":  "identification_by",
    "LabNotes":      "specimen_notes",    # Panama's "notes" was renamed to this
    "FMNH":          "voucher",
    "Order":         "clade", #temporary mapping, might come back to later
    "PhotosLab":     "photos_org", #closest match (will remove anyways)
})

specimen_panama_only_columns = [
    "suffix",               
    "genus",                # Eventually parse out genus from species name to put in genus column
    "epithet",              # Probably remove
    "development",          # Larval development type; not recorded in La Palma
    "vial",                 # Probably remove
    "operculum",            # Probably remove
    "second_voucher_clip",  
]
 
for col in specimen_panama_only_columns:
    specimen_clean[col] = None

############################################################################
### CHECKING IF COLUMNS ARE CORRECT
event_cols_lapalma= list(event_clean.columns)
print('--LaPalma--')
print('--Event Table--')
for col in event_cols:
    check= 'Fix name'
    if col not in event_cols_lapalma:
        print(col, check)
print()

spec_cols_lapalma= list(specimen_clean.columns)
print('--LaPalma--')
print('--Specimen Table--')
for col in spec_cols:
    check= 'Fix name'
    if col not in spec_cols_lapalma:
        print(col, check)
print()

dna_cols_lapalma= list(dna_clean.columns)
print('--LaPalma--')
print('--DNA Table--')
for col in dna_cols:
    check= 'Fix name'
    if col not in dna_cols_lapalma:
        print(col, check)
print()



# Cleaning outputs made during testing
conn = sqlite3.connect('panama_scripts/panama_specimens.db')
cursor = conn.cursor()

dna_clean.to_sql("DNAExtractions", conn, if_exists="append", index=False)
conn.commit()