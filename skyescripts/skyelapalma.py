import sqlite3
import pandas as pd
import os

# ===========================================================================
# LOADING CSVs WITH PANDAS
# ===========================================================================

# pd.read_csv() reads a CSV file and turns it into a DataFrame object
event_df = pd.read_csv("LaPalma2023-Main-Dataset\\LaPalma2023-EventData.csv")
specimen_df = pd.read_csv("LaPalma2023-Main-Dataset\\LaPalma2023-SpecimenData.csv")
dna_df = pd.read_csv("LaPalma2023-Main-Dataset\\LaPalma2023-DNAextractions.csv")

# Inspect/Verify data by getting rows and column counts (If they don't match you know something messed up)
print(f"\nEvent Data:        {event_df.shape[0]} rows, {event_df.shape[1]} columns")
print(f"Specimen Data:     {specimen_df.shape[0]} rows, {specimen_df.shape[1]} columns")
print(f"DNA Extractions:   {dna_df.shape[0]} rows, {dna_df.shape[1]} columns")

print("\n--- Event Data column names ---")
print(list(event_df.columns))

print("\n--- Specimen Data column names ---")
print(list(specimen_df.columns))

print("\n--- DNA Extraction column names ---")
print(list(dna_df.columns))

# ===========================================================================
# DATA CLEANING: EventData
# ===========================================================================

event_clean = event_df.rename(
    columns={
        "TripID": "trip_id",
        "EventCode": "event_code",  # PRIMARY KEY
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
        "Locality": "locality",
        "Country": "country",
        "Collectors": "collector",
        "EventNotes": "event_notes",
        "PhotosEnvironment": "photos_env",  # remove
        "UseInMap": "use_in_map",  # remove
        "SpecificLocality": "locality_details",  # remap using names from Panama - these are the same types of info, just different column names
        "Municipality": "city_district",
        "ShortName": "population",  # the most similar match I could think of to Panama is population (not that it matters since we're not including this)
    }
)
# These columns are missing from La Palma but are in Panama - fill with None data for now
event_panama_only_columns = [
    "fieldwork_status",  # Might not matter if we're removing
    "low_tide",  # Also probably being removed
    "province",
    "area"
]

for col in event_panama_only_columns:
    event_clean[col] = None

print("\n --- Cleaned EventData Columns ---")
print(list(event_clean.columns))

# ===========================================================================
# DATA CLEANING: SpecimenData
# ===========================================================================

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
    
# print("\n --- Cleaned SpecimenData Columns ---")
# print(list(specimen_clean.columns))
