import sqlite3
import pandas as pd
import logging
import os

# 1. LOGGING SETUP
logging.basicConfig(
    filename="schema_alignment.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 2. SETUP PATHS
path = "/home/sorellanarebolledo/specimen-database/LaPalma2023-Main-Dataset/"
db_path = 'panama_scripts/panama_specimens.db'

# 3. LOAD CSVs (La Palma has 3 tables)
event_df = pd.read_csv(path + "LaPalma2023-EventData.csv")
specimen_df = pd.read_csv(path + "LaPalma2023-SpecimenData.csv")
dna_df = pd.read_csv(path + "LaPalma2023-DNAextractions.csv")

csv_tables = {
    "EventData": event_df,
    "SpecimenData": specimen_df,
    "DNAExtractions": dna_df
}

# 4. GET DB SCHEMA FOR THESE TABLES
def get_db_columns(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
    cols = [d[0] for d in cursor.description]
    conn.close()
    return cols

db_schemas = {
    "EventData": get_db_columns(db_path, "EventData"),
    "SpecimenData": get_db_columns(db_path, "SpecimenData"),
    "DNAExtractions": get_db_columns(db_path, "DNAExtractions")
}

# 5. CLEANING RULES (La Palma → Panama mapping)

# EVENT DATA CLEANING
def clean_event_data(df):
    df = df.rename(columns={
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
        "Locality": "locality",
        "Country": "country",
        "Collectors": "collector",
        "EventNotes": "event_notes",
        "SpecificLocality": "locality_details",
        "Municipality": "city_district",
        "ShortName": "population",
        "PhotosEnvironment": "photos_env",
        "UseInMap": "use_in_map"
    })

    # Panama-only columns (La Palma missing)
    for col in ["fieldwork_status", "low_tide", "province", "area"]:
        df[col] = None

    return df


# SPECIMEN DATA CLEANING
def clean_specimen_data(df):
    df = df.rename(columns={
        "SampleCode": "lot_id",
        "EventCode": "event_code",
        "Species": "species",
        "Specimens": "specimen_count",
        "Parts": "parts",
        "FixationMethod": "fixation_method",
        "Family": "family",
        "Habitat": "habitat",
        "IdentifiedBy": "identification_by",
        "LabNotes": "specimen_notes",
        "FMNH": "voucher",
        "Order": "clade",
        "PhotosLab": "photos_org"
    })

    # Panama-only columns
    for col in [
        "suffix", "genus", "epithet", "development",
        "vial", "operculum", "second_voucher_clip"
    ]:
        df[col] = None

    return df

# DNA EXTRACTIONS CLEANING
def clean_dna_data(df):
    # Add mappings here if needed
    return df

# 6. AUTOMATED SCHEMA ALIGNMENT
def align_schema(df, db_columns, table_name, interactive=True):
    df = df.copy()
    df.columns = df.columns.str.strip()

    logging.info(f"--- Aligning schema for {table_name} ---")

    # Add missing columns
    for col in db_columns:
        if col not in df.columns:
            df[col] = None
            logging.info(f"[{table_name}] Added missing column: {col}")

    # Detect extra columns
    extra_cols = [c for c in df.columns if c not in db_columns]

    if extra_cols:
        logging.info(f"[{table_name}] Extra columns: {extra_cols}")

        if interactive:
            print(f"\n[{table_name}] Extra columns found: {extra_cols}")
            drop = input("Drop these columns? (y/n): ").strip().lower()

            if drop == "y":
                df = df.drop(columns=extra_cols)
                logging.info(f"[{table_name}] Dropped: {extra_cols}")
            else:
                logging.info(f"[{table_name}] Kept extra columns.")
        else:
            df = df.drop(columns=extra_cols)
            logging.info(f"[{table_name}] Auto-dropped: {extra_cols}")

    # Reorder
    df = df[[col for col in db_columns if col in df.columns]]

    return df

# 7. RUN CLEANING + SCHEMA ALIGNMENT
cleaned_tables = {
    "EventData": align_schema(clean_event_data(event_df), db_schemas["EventData"], "EventData"),
    "SpecimenData": align_schema(clean_specimen_data(specimen_df), db_schemas["SpecimenData"], "SpecimenData"),
    "DNAExtractions": align_schema(clean_dna_data(dna_df), db_schemas["DNAExtractions"], "DNAExtractions")
}

# 8. OPTIONAL: LOAD INTO DATABASE
# conn = sqlite3.connect(db_path)
# for table, df in cleaned_tables.items():
#     df.to_sql(table, conn, if_exists="append", index=False)
# conn.close()