import sqlite3
import pandas as pd
import os

# ===========================================================================
# IMPORTANT!!!!!
# IF you want to run this script, you MUST RUN panama_clean_load.py BEFORE!
# ===========================================================================

# ===========================================================================
# INITIAL LOADING AND VALIDATION OF CSV COLUMNS
# ===========================================================================

# Define paths and load La Palma CSVs
path = "LaPalma2023-Main-Dataset/"
db_path = "skyescripts/TEST_cunha_invertebrate_specimens.db"

event_df = pd.read_csv(path + "LaPalma2023-EventData.csv")
specimen_df = pd.read_csv(path + "LaPalma2023-SpecimenData.csv")
dna_df = pd.read_csv(path + "LaPalma2023-DNAextractions.csv")

print(f"\nEvent Data:        {event_df.shape[0]} rows, {event_df.shape[1]} columns")
print(f"Specimen Data:     {specimen_df.shape[0]} rows, {specimen_df.shape[1]} columns")
print(f"DNA Extractions:   {dna_df.shape[0]} rows, {dna_df.shape[1]} columns")

print("\n--- Event Data column names ---")
print(list(event_df.columns))

print("\n--- Specimen Data column names ---")
print(list(specimen_df.columns))

print("\n--- DNA Extraction column names ---")
print(list(dna_df.columns))

# Get master column names from database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get EventData columns
cursor.execute("SELECT * FROM EventData LIMIT 0")
db_event_cols = [d[0] for d in cursor.description]

# Get SpecimenData columns
cursor.execute("SELECT * FROM SpecimenData LIMIT 0")
db_spec_cols = [d[0] for d in cursor.description]

# Get DNAExtractions columns
cursor.execute("SELECT * FROM DNAExtractions LIMIT 0")
db_dna_cols = [d[0] for d in cursor.description]

conn.close()

# VALIDATION FUNCTION
def check_schema(table_name, db_columns, csv_columns):
    print(f"-- LaPalma: {table_name} --")
    for col in db_columns:
        if col not in csv_columns:
            print(f"MISSING: {col} -> Fix name or add column to CSV")
    print()


# Run checks
check_schema("Event Table", db_event_cols, list(event_df.columns))
check_schema("Specimen Table", db_spec_cols, list(specimen_df.columns))
check_schema("DNA Table", db_dna_cols, list(dna_df.columns))

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
# These columns are missing from La Palma but are in Panama - fill with None/NULL data for now
event_panama_only_columns = [
    "fieldwork_status",  # Might not matter if we're removing
    "low_tide",  # Also probably being removed
    "province",
    "area",
]

for col in event_panama_only_columns:
    event_clean[col] = None

# Drop same columns that Panama drops (for now)
event_clean = event_clean.loc[:, ~event_clean.columns.str.startswith("photos_env")]
event_clean = event_clean.loc[:, ~event_clean.columns.str.startswith("use_in_map")]
event_clean = event_clean.loc[:, ~event_clean.columns.str.startswith("population")]
event_clean = event_clean.loc[
    :, ~event_clean.columns.str.startswith("fieldwork_status")
]
event_clean = event_clean.loc[:, ~event_clean.columns.str.startswith("low_tide")]

print("\n --- Cleaned EventData Columns ---")
print(list(event_clean.columns))

# ===========================================================================
# DATA CLEANING: SpecimenData
# ===========================================================================

specimen_clean = specimen_df.rename(
    columns={
        "SampleCode": "lot_id",  # PRIMARY KEY
        "EventCode": "event_code",  # FOREIGN KEY (EventData)
        "Species": "species",
        "Specimens": "specimen_count",
        "Parts": "parts",
        "FixationMethod": "fixation_method",
        "Family": "family",  # remove for now
        "Habitat": "habitat",
        "IdentifiedBy": "identification_by",
        "LabNotes": "specimen_notes",  # Panama's "notes" was renamed to this
        "FMNH": "voucher",
        "Order": "clade",  # temporary mapping, might come back to later
        "PhotosLab": "photos_org",  # closest match (will remove anyways)
        # Columns in La Palma but not in Panama
        # Just adding these, can go back and remove later if we find them unnecessary
        "DNA": "dna_extracted",
        "Phylum": "phylum",
        "Class": "class_name",  # the word "Class" might mess with Python
        "Subclass": "subclass",
        "Uncertainty": "uncertainty",
        "PhotosUnderwater": "photos_underwater",  # probably remove
        "CollectedBy": "collected_by",  # Panama EventData has a "collector" column?
    }
)

specimen_panama_only_columns = [
    "suffix",
    "genus",  # Eventually parse out genus from species name to put in genus column
    "epithet",  # Probably remove
    "development",
    "vial",  # Probably remove
    "operculum",  # Probably remove
    "second_voucher_clip",
]

# these missing columns will just be filled with NULL for now
for col in specimen_panama_only_columns:
    specimen_clean[col] = None

# removing columns
specimen_clean = specimen_clean.loc[:, ~specimen_clean.columns.str.startswith("clade")]
specimen_clean = specimen_clean.loc[:, ~specimen_clean.columns.str.startswith("family")]
specimen_clean = specimen_clean.loc[
    :, ~specimen_clean.columns.str.startswith("epithet")
]
specimen_clean = specimen_clean.loc[:, ~specimen_clean.columns.str.startswith("vial")]
specimen_clean = specimen_clean.loc[
    :, ~specimen_clean.columns.str.startswith("operculum")
]
specimen_clean = specimen_clean.loc[
    :, ~specimen_clean.columns.str.startswith("photos_org")
]
specimen_clean = specimen_clean.loc[
    :, ~specimen_clean.columns.str.startswith("photos_underwater")
]

print("\n --- Cleaned SpecimenData Columns ---")
print(list(specimen_clean.columns))

# ===========================================================================
# DATA CLEANING: DNAextractions
# ===========================================================================

dna_clean = dna_df.rename(
    columns={
        "ExtractionID": "extraction_id",  # PRIMARY KEY
        "Date": "extraction_date",
        "Method": "extraction_kit",  # same thing in Panama
        "Elution_ul": "elution_ul",
        "Qubit_ngul": "qubit_dna_ng_ul",  # Same thing
        "TissueType": "piece_size",  # closest match?
        "ExtractionNotes": "extraction_notes",
        # Columns only in La Palma and not Panama
        "Suffix": "extraction_suffix",  # not to be confused with suffix column in specimen
        "ClippingNotes": "clipping_notes",
        "ExtractedBy": "extracted_by",
        "COI": "coi",
        "PCRBy": "pcr_by",
        # specify "blast" for clarity
        # La Palma runs BLAST searches on COI columns, but Panama doesn't
        # we'll see if this matters later
        "Best_Match": "blast_best_match",
        "Max_Score": "blast_max_score",
        "Total_Score": "blast_total_score",
        "Query_Cover": "blast_query_cover",
        "E-Value": "blast_e_value",
        "Percent_Identity": "blast_percent_identity",
        "Match_Length": "blast_match_length",
        "Match_Accession": "blast_match_accession",
    }
)

# Drop Species column because it's already in SpecimenData
dna_clean = dna_clean.loc[:, ~dna_clean.columns.str.startswith("Species")]

# Panama columns missing from La Palma
dna_panama_only_columns = [
    "nanodrop_ng_ul",
    "nanodrop_260_280",
    "nanodrop_260_230",
    "qubit_nanodrop_ratio",
    "clip_over",
    "contamination_plate",
    "contamination_wells",
    "qubit_after_speedvac",
]
for col in dna_panama_only_columns:
    dna_clean[col] = None

# La Palma's foreign key to link DNAextractions to SpecimenData is "voucher" (FMNH) but Panama's schema uses lot_id as the foreign key in this situation
# in La Palma, SpecimenData also has lot_id (SampleCode)
# we can do a pd.merge() on the voucher columns and the correct lot_ids the database expects

# take the voucher and lot_id columns from SpecimenData/specimen_clean
voucher_merge = specimen_clean[["voucher", "lot_id"]].copy()
# need everything to be a string
voucher_merge["voucher"] = voucher_merge["voucher"].astype(str)
dna_clean["Voucher"] = dna_clean["Voucher"].astype(str)

# we want to add lot_id to DNAextractions/dna_clean
# we want to add it to the "Voucher" column in dna_clean
# the matching column is "voucher" in SpecimenData/specimen_clean
dna_clean = pd.merge(
    dna_clean,
    voucher_merge,
    left_on="Voucher",
    right_on="voucher",
    # keep all dna_clean rows even if no match (becomes NaN)
    how="left",
)

# Flag any DNAExtractioons rows that couldn't be connected back to SpecimenData via lot_id (NaN after merge)
unmatched_dna = dna_clean[dna_clean["lot_id"].isna()]
if not unmatched_dna.empty:
    print(
        f"NOTE: {len(unmatched_dna)} DNA rows could not be matched to a specimen via lot_ids"
    )
    print(unmatched_dna[["extraction_id", "Voucher"]].to_string())

# We can drop these columns since now they are redundant
dna_clean = dna_clean.drop(columns=["Voucher", "voucher"])

print("\n --- Cleaned DNAextractions Columns ---")
print(list(dna_clean.columns))

# ===========================================================================
# ADD TO SQL DATABASE
# ===========================================================================
# IMPORTANT: This script appends to the database that clean_load_panama.py
# already created. Do NOT use os.remove() here — that would delete Panama data.
# Run clean_load_panama.py first, then run this script.

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("PRAGMA foreign_keys = ON;")

def add_missing_column(cursor, table, column, col_type):
    """Helper function to add columns that exist in one table but not another"""
    # use try and except to easily skip columns that already exist
    try:
        # SQL ALTER TABLE statement and ADD COLUMN claude adds columns to existing tables
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type};")
        print(f"Added {column} to {table}")
    # throws an error if column already exists, so it'll be skipped
    except sqlite3.OperationalError:
        pass


add_missing_column(cur, "EventData", "locality_details", "TEXT")
add_missing_column(cur, "EventData", "city_district", "TEXT")

add_missing_column(cur, "SpecimenData", "dna_extracted", "TEXT")
add_missing_column(cur, "SpecimenData", "phylum", "TEXT")
add_missing_column(cur, "SpecimenData", "class_name", "TEXT")
add_missing_column(cur, "SpecimenData", "subclass", "TEXT")
add_missing_column(cur, "SpecimenData", "uncertainty", "TEXT")
add_missing_column(cur, "SpecimenData", "collected_by", "TEXT")

add_missing_column(cur, "DNAExtractions", "extraction_suffix", "TEXT")
add_missing_column(cur, "DNAExtractions", "clipping_notes", "TEXT")
add_missing_column(cur, "DNAExtractions", "extracted_by", "TEXT")
add_missing_column(cur, "DNAExtractions", "coi", "TEXT")
add_missing_column(cur, "DNAExtractions", "pcr_by", "TEXT")
add_missing_column(cur, "DNAExtractions", "blast_best_match", "TEXT")
add_missing_column(cur, "DNAExtractions", "blast_max_score", "REAL")
add_missing_column(cur, "DNAExtractions", "blast_total_score", "REAL")
add_missing_column(cur, "DNAExtractions", "blast_query_cover", "TEXT")
add_missing_column(cur, "DNAExtractions", "blast_e_value", "TEXT")
add_missing_column(cur, "DNAExtractions", "blast_percent_identity", "TEXT")
add_missing_column(cur, "DNAExtractions", "blast_match_length", "INTEGER")
add_missing_column(cur, "DNAExtractions", "blast_match_accession", "TEXT")

conn.commit()
print("\nAll table columns updated.")

# ===========================================================================
# LOADING DATA INTO DATABASE
# ===========================================================================

# Verify correct column names
event_cols_lapalma= list(event_clean.columns)
print('\n--LaPalma--')
print('--Event Table--')
good_event_cols_count=0
bad_event_cols_count=0
for col in db_event_cols:
    check= 'Fix name'
    if col not in event_cols_lapalma:
        bad_event_cols_count+=1
        print(col, check)
    good_event_cols_count+=1
print(f'Flagged {bad_event_cols_count} columns requiring correction.\n {good_event_cols_count} columns succesfully matched.')

spec_cols_lapalma= list(specimen_clean.columns)
print('\n--LaPalma--')
print('--Specimen Table--')
good_spec_cols_count=0
bad_spec_cols_count=0
for col in db_spec_cols:
    check= 'Fix name'
    if col not in spec_cols_lapalma:
        bad_espec_cols_count+=1
        print(col, check)
    good_spec_cols_count+=1
print(f'Flagged {bad_spec_cols_count} columns requiring correction.\n {good_spec_cols_count} columns succesfully matched.')

dna_cols_lapalma= list(dna_clean.columns)
print('\n--LaPalma--')
print('--DNA Table--')
good_dna_cols_count=0
bad_dna_cols_count=0
for col in db_dna_cols:
    check= 'Fix name'
    if col not in dna_cols_lapalma:
        bad_dna_cols_count+=1
        print(col, check)
    good_dna_cols_count+=1
print(f'Flagged {bad_dna_cols_count} columns requiring correction.\n {good_dna_cols_count} columns succesfully matched.')

event_clean.to_sql("EventData", conn, if_exists="append", index=False)
print(f"\nLoaded {len(event_clean)} rows into EventData")

specimen_clean.to_sql("SpecimenData", conn, if_exists="append", index=False)
print(f"\nLoaded {len(specimen_clean)} rows into SpecimenData")

# IMPORTANT: some Panama and La Palma extraction_ids conflict
# Add prefix LP- to duplicate La Palma IDs and save in a new column

# get ALL extraction ids from DNAExtractions tab of database
extraction_ids = set(
    row[0] for row in cur.execute("SELECT extraction_id FROM DNAExtractions").fetchall()
)
# get the conflicting ids, which are any that are in La Palma's dna_clean
conflicts = dna_clean["extraction_id"].isin(extraction_ids)

# returns True if
if conflicts.any():
    conflicting_ids = dna_clean.loc[conflicts, "extraction_id"].tolist()
    print(
        f"\n  NOTE: The following extraction_ids already exist in the database from Panama and will be prefixed: {conflicting_ids}"
    )

    # Add the original_extraction_id column and save conflicting IDs before prefixing
    add_missing_column(cur, "DNAExtractions", "original_extraction_id", "TEXT")
    dna_clean["original_extraction_id"] = dna_clean["extraction_id"]
    dna_clean.loc[conflicts, "extraction_id"] = (
        "LP-" + dna_clean.loc[conflicts, "extraction_id"]
    )

conn.commit()

dna_clean.to_sql("DNAExtractions", conn, if_exists="append", index=False)
print(f"\nLoaded {len(dna_clean)} rows into DNAExtractions")

conn.commit()
print("\nAll La Palma data loaded successfully!")

conn.close()
