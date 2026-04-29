import sqlite3
import pandas as pd
import os

# ===========================================================================
# LOADING CSVs WITH PANDAS
# ===========================================================================

# pd.read_csv() reads a CSV file and turns it into a DataFrame object
event_df = pd.read_csv("Panama2021-Main-Dataset/Panama2021-EventData.csv")
specimen_df = pd.read_csv("Panama2021-Main-Dataset/Panama2021-SpecimenData.csv")
dna_df = pd.read_csv("Panama2021-Main-Dataset/Panama2021-DNAextractions.csv")
library_df = pd.read_csv("Panama2021-Main-Dataset/Panama2021-GenomicLibraries.csv")


# Inspect/Verify data by getting rows and column counts (If they don't match you know something messed up)
print(f"\nEvent Data:        {event_df.shape[0]} rows, {event_df.shape[1]} columns")
print(f"Specimen Data:     {specimen_df.shape[0]} rows, {specimen_df.shape[1]} columns")
print(f"DNA Extractions:   {dna_df.shape[0]} rows, {dna_df.shape[1]} columns")
print(f"Genomic Libraries: {library_df.shape[0]} rows, {library_df.shape[1]} columns")

print("\n--- Event Data column names ---")
print(list(event_df.columns))

print("\n--- Specimen Data column names ---")
print(list(specimen_df.columns))

print("\n--- DNA Extraction column names ---")
print(list(dna_df.columns))

print("\n--- Genomic Library column names ---")
print(list(library_df.columns))

# ===========================================================================
# DATA CLEANING
# ===========================================================================

# Renaming columns to be more consistent and descriptive
# rename() takes a dictionary mapping key(old names) to value(new names)
# This also doesn't modify the original DF (we're saving to a new one)
event_clean = event_df.rename(
    columns={
        "trip_id": "trip_id",
        "event_code": "event_code",  # PRIMARY KEY
        "fieldwork_status": "fieldwork_status",  # remove
        "year": "year",
        "month": "month",
        "day": "day",
        "date": "date",
        "waypoint": "waypoint",
        "latitude": "latitude",
        "longitude": "longitude",
        "environment": "environment",
        "low_tide": "low_tide",  # remove? not in la palma
        "collecting_method": "collecting_method",
        "depth": "depth",
        "population": "population",  # this will get removed
        "locality": "locality",
        "locality_details": "locality_details",
        "city_district": "city_district",
        "province": "province",
        "area": "area",
        "photos_env": "photos_env",  # remove
        "country": "country",
        "collector": "collector",
        "notes": "event_notes",  # Renamed - all the datasets have a notes column so need to rename to avoid confusion (disambiguation)
        "use_in_map": "use_in_map",  # this will get removed
    }
)

# remove use_in_map column and population column
# .loc[] in pandas drops columns
# The ~ means "not" so we keep all columns that do NOT start with "Unnamed"
# pandas is doing some stuff with making a boolean array for all columns
event_clean = event_clean.loc[
    :, ~event_clean.columns.str.startswith("fieldwork_status")
]
event_clean = event_clean.loc[:, ~event_clean.columns.str.startswith("low_tide")]
event_clean = event_clean.loc[:, ~event_clean.columns.str.startswith("photos_env")]
event_clean = event_clean.loc[:, ~event_clean.columns.str.startswith("use_in_map")]
event_clean = event_clean.loc[:, ~event_clean.columns.str.startswith("population")]

specimen_clean = specimen_df.rename(
    columns={
        "lot_id": "lot_id",  # PRIMARY KEY
        "sufix": "suffix",  # Spelling
        "event_code": "event_code",  # FOREIGN KEY (EventData)
        "species": "species",
        "genus": "genus",
        "epithet": "epithet",  # remove
        "clade": "clade",  # remove
        "family": "family",  # remove
        "development": "development",  # keep but ask about/add to La Palma
        "habitat": "habitat",
        "fixation_method": "fixation_method",  # add ethanol 95% in panama
        "specimens": "specimen_count",  # More descriptive
        "parts": "parts",  # keep but ask about/add to La Palma
        "vial": "vial",  # remove
        "operculum": "operculum",  # remove
        "notes": "specimen_notes",  # Renamed
        "photos_org": "photos_org",  # remove
        "identification_by": "identification_by",
        "Voucher": "voucher",  # lowercase
        "SecondVoucherClip": "second_voucher_clip",
        # need to add a column for location of sample in the lab
    }
)

specimen_clean = specimen_clean.loc[
    :, ~specimen_clean.columns.str.startswith("epithet")
]
specimen_clean = specimen_clean.loc[:, ~specimen_clean.columns.str.startswith("clade")]
specimen_clean = specimen_clean.loc[:, ~specimen_clean.columns.str.startswith("family")]
specimen_clean = specimen_clean.loc[:, ~specimen_clean.columns.str.startswith("vial")]
specimen_clean = specimen_clean.loc[
    :, ~specimen_clean.columns.str.startswith("operculum")
]
specimen_clean = specimen_clean.loc[
    :, ~specimen_clean.columns.str.startswith("photos_org")
]
# Remove unnamed last columns
# keep all columns that do NOT start with "Unnamed"
specimen_clean = specimen_clean.loc[
    :, ~specimen_clean.columns.str.startswith("Unnamed")
]

# Need to remove special characters
dna_clean = dna_df.rename(
    columns={
        "extraction_id": "extraction_id",  # PRIMARY KEY
        "lot_id": "lot_id",  # FOREIGN KEY (SpecimenData)
        "species": "species",  # remove
        "plate_id": "plate_id",  # remove, maybe ask?
        "plate_well": "plate_well",  # remove, maybe ask?
        "extraction_date": "extraction_date",
        "extraction_kit": "extraction_kit",
        "elution_ul": "elution_ul",
        "Qubit_DNA_[ng/ul]": "qubit_dna_ng_ul",  # Removed brackets and slashes
        "Nanodrop_[ng/ul]": "nanodrop_ng_ul",  # create dummy in La Palma
        "Nanodrop_260/280": "nanodrop_260_280",  # create dummy in La Palma
        "Nanodrop_260/230": "nanodrop_260_230",  # create dummy in La Palma
        "Qubit : Nanodrop": "qubit_nanodrop_ratio",  # create dummy in La Palma
        "clip_over": "clip_over",  # create dummy in La Palma
        "contamination_plate": "contamination_plate",  # create dummy in La Palma
        "contamination_wells": "contamination_wells",  # create dummy in La Palma
        "extraction_notes": "extraction_notes",
        "piece_size": "piece_size",
        "Qubit_after_SpeedVac": "qubit_after_speedvac",  # create dummy in La Palma
    }
)


dna_clean = dna_clean.loc[:, ~dna_clean.columns.str.startswith("species")]
dna_clean = dna_clean.loc[:, ~dna_clean.columns.str.startswith("plate_id")]
dna_clean = dna_clean.loc[:, ~dna_clean.columns.str.startswith("plate_well")]

### add empty columns for BLAST info to Panama
library_clean = library_df.rename(
    columns={
        "library_id": "library_id",  # PRIMARY KEY
        "extraction_id": "extraction_id",  # FOREIGN KEY(DNAExtractions)
        "lot_id": "lot_id",
        "species": "species",
        "library_date": "library_date",
        "library_kit": "library_kit",
        "Qubit_DNA_[ng/ul]": "qubit_dna_ng_ul",  # Removed brackets and slashes
        "input_mass_ng": "input_mass_ng",
        "input_vol_ul": "input_vol_ul",
        "EB_complement_ul": "eb_complement_ul",
        "frag_time_min": "frag_time_min",
        "cycles": "cycles",
        "elution_ul": "elution_ul",
        "Qubit_lib_[ng/ul]": "qubit_lib_ng_ul",
        "size_selection": "size_selection",
        "Qubit_size-selection_[ng/ul]": "qubit_size_selection_ng_ul",
        "IDT xGen UDI Primer Pair Well": "idt_primer_well",
        "Primer Name": "primer_name",
        "i5 index": "i5_index",
        "i7 index": "i7_index",
        "Bioanalyzer_avg_size": "bioanalyzer_avg_size",
        "insert_size": "insert_size",
        "[C]_nM_estimate": "concentration_nm_estimate",
        "Data_Target_GB": "data_target_gb",
    }
)

print(f"\nCleaned Event columns:    {list(event_clean.columns)}")
print(f"\nCleaned Specimen columns: {list(specimen_clean.columns)}")
print(f"\nCleaned DNA columns: {list(dna_clean.columns)}")
print(f"\nCleaned Genomic Library columns: {list(library_clean.columns)}")


# ===========================================================================
# CREATING THE SQLITE DATABASE
# ===========================================================================


# sqlite3.connect() creates a new .db file (or opens it if it exists) at the given path
# The "connection" (conn) is your link to the database file
# The "cursor" (cur) is the object you use to send SQL commands

db_path = "initial-building-scripts/cunha_invertebrate_specimens.db"

# Cleaning outputs made during testing
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Removed existing database at {db_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()
print(f"Database created at: {db_path}")

# SQLite has foreign key enforcement off by default
# must be run every time you open a connection because it doesn't persist in the file itself
cur.execute("PRAGMA foreign_keys = ON;")

# CREATE TABLE: EventData
# This is actually defining the schema for a table
# IF NOT EXISTS prevents an error (os.remove() pretty much handles this already though)
# Column name - Data Type

# PRIMARY KEY means this column is the unique identifier for every row
# it also means it is the target for FOREIGN KEY references from other tables
cur.execute(
    """
CREATE TABLE IF NOT EXISTS EventData (
    event_code       TEXT PRIMARY KEY,
    trip_id          TEXT,
    year             INTEGER,
    month            INTEGER,
    day              INTEGER,
    date             TEXT,
    waypoint         TEXT,
    latitude         REAL,
    longitude        REAL,
    environment      TEXT,
    collecting_method TEXT,
    depth            TEXT,
    locality         TEXT,
    locality_details TEXT,
    city_district    TEXT,
    province         TEXT,
    area             TEXT,
    country          TEXT,
    collector        TEXT,
    event_notes      TEXT
);
"""
)

# CREATE TABLE: SpecimenData
# FOREIGN KEY - event_code column in the SpecimenData table must always reference a value that also exists in the event_code column in EventData
# So, can't add a specimen with an invalid/missing event code
# and can't delete an event that still has specimens associated with it
cur.execute(
    """
CREATE TABLE IF NOT EXISTS SpecimenData (
    lot_id           TEXT PRIMARY KEY,  -- Unique ID for each specimen lot
    suffix           TEXT,
    event_code       TEXT,              -- Links to EventData
    species          TEXT,
    genus            TEXT,
    development      TEXT,
    habitat          TEXT,
    fixation_method  TEXT,
    specimen_count   INTEGER,
    parts            TEXT,
    specimen_notes   TEXT,
    identification_by TEXT,
    voucher          TEXT,
    second_voucher_clip TEXT,
    FOREIGN KEY (event_code) REFERENCES EventData(event_code)
);
"""
)

# CREATE TABLE: DNAExtractions
cur.execute(
    """
CREATE TABLE IF NOT EXISTS DNAExtractions (
    extraction_id         TEXT PRIMARY KEY,  -- Unique ID for each extraction
    lot_id                TEXT,              -- Links to SpecimenData
    extraction_date       TEXT,
    extraction_kit        TEXT,
    elution_ul            REAL,
    qubit_dna_ng_ul       REAL,
    nanodrop_ng_ul        REAL,
    nanodrop_260_280      REAL,
    nanodrop_260_230      REAL,
    qubit_nanodrop_ratio  REAL,
    clip_over             TEXT,
    contamination_plate   TEXT,
    contamination_wells   TEXT,
    extraction_notes      TEXT,
    piece_size            TEXT,
    qubit_after_speedvac  REAL,
    FOREIGN KEY (lot_id) REFERENCES SpecimenData(lot_id)
);
"""
)

# CREATE TABLE: GenomicLibraries
cur.execute(
    """
CREATE TABLE IF NOT EXISTS GenomicLibraries (
    library_id                 TEXT PRIMARY KEY,
    extraction_id              TEXT,           -- Links to DNAExtractions
    lot_id                     TEXT,
    species                    TEXT,
    library_date               TEXT,
    library_kit                TEXT,
    qubit_dna_ng_ul            REAL,
    input_mass_ng              REAL,
    input_vol_ul               REAL,
    eb_complement_ul           REAL,
    frag_time_min              INTEGER,
    cycles                     INTEGER,
    elution_ul                 REAL,
    qubit_lib_ng_ul            REAL,
    size_selection             TEXT,
    qubit_size_selection_ng_ul REAL,
    idt_primer_well            TEXT,
    primer_name                TEXT,
    i5_index                   TEXT,
    i7_index                   TEXT,
    bioanalyzer_avg_size       INTEGER,
    insert_size                INTEGER,
    concentration_nm_estimate  REAL,
    data_target_gb             REAL,
    FOREIGN KEY (extraction_id) REFERENCES DNAExtractions(extraction_id)
);
"""
)

# Replace any 'NA' strings with actual NULL across the whole DataFrame
specimen_clean = specimen_clean.replace("NA", None)

conn.commit()  # Permanently writes these to the file
print("All four tables created successfully!")

# ===========================================================================
# LOADING DATA INTO DATABASE
# ===========================================================================

"""
pandas - to_sql() writes a DataFrame directly to a SQL table

Parameters:
    name: the name of the target table in the database
    con:the database connection
    if_exists: 'append' adds these rows to existing table ()'replace' would overwrite it)
    index: False means don't write the pandas internal row-numbering index as an extra column
"""
# Load Data: EventData
event_clean.to_sql("EventData", conn, if_exists="append", index=False)
print(f"Loaded {len(event_clean)} rows into EventData")

# If a specimen references an event code that doesnt exist yet, it causes an error when loading
# Remove those rows and deal with them later

valid_event_codes = set(
    event_clean["event_code"]
)  # Create a set of all successfully-loaded event codes
orphan_specimens = specimen_clean[
    ~specimen_clean["event_code"].isin(valid_event_codes)
]  # return True for each specimen row whose event_code DOES NOT exist in the valid codes set (find orphans)
valid_specimens = specimen_clean[
    specimen_clean["event_code"].isin(valid_event_codes)
]  # Opposite of previous line; these are rows actually safe to load without error
if len(orphan_specimens) > 0:
    print(
        f"\n  NOTE: {len(orphan_specimens)} specimen row(s) reference unknown event codes and were skipped: {orphan_specimens['event_code'].unique().tolist()}. Saving to orphan_specimens.csv for review."
    )
    orphan_specimens.to_csv(
        "initial-building-scripts/orphan_specimens.csv", index=False
    )

# Now we can actually load the "cleared" rows
valid_specimens.to_sql("SpecimenData", conn, if_exists="append", index=False)
print(f"Loaded {len(valid_specimens)} rows into SpecimenData")

dna_clean.to_sql("DNAExtractions", conn, if_exists="append", index=False)
print(f"Loaded {len(dna_clean)} rows into DNAExtractions")

library_clean.to_sql("GenomicLibraries", conn, if_exists="append", index=False)
print(f"Loaded {len(library_clean)} rows into GenomicLibraries")

conn.commit()
print("\nAll data loaded successfully!")
