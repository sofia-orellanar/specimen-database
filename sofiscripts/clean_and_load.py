import pandas as pd
import sqlite3

# Event data cleaning
def clean_event_data(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    df["event_date"] = df["date"]
    df["city"] = df["city_district"]

    keep = ["event_code", "trip_id", "event_date",
            "latitude", "longitude", "city",
            "country", "province", "collector", "notes"]

    return df[keep]

# Specimen data cleaning
def clean_specimen_data(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    extra_cols = ["habitat", "parts", "vial", "operculum",
                  "photos_org", "identification_by", "Voucher"]

    # Ensure all extra columns exist (avoid KeyErrors)
    for col in extra_cols:
        if col not in df.columns:
            df[col] = ""

    # Convert everything to string safely
    df["notes"] = (
        df["notes"].fillna("").astype(str)
        + " | "
        + df[extra_cols].apply(
            lambda row: "; ".join([str(x) for x in row]), axis=1
        )
    )

    keep = [
        "lot_id", "Voucher", "identification_by", "event_code",
        "species", "genus", "family", "development",
        "fixation_method", "notes"
    ]

    return df[keep]

# DNA extraction data cleaning
def clean_dna_data(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    keep = ["extraction_id", "lot_id", "extraction_date"]

    return df[keep]

# Genomic libraries data cleaning
def clean_libraries(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    rename_map = {"Qubit_DNA_[ng/ul]": "qubit_dna",
                  "input_mass_ng": "input_mass_ng",
                  "input_vol_ul": "input_vol_ul",
                  "EB_complement_ul": "eb_complement_ul",
                  "frag_time_min": "frag_time_min",
                  "cycles": "cycles",
                  "elution_ul": "elution_ul",
                  "Qubit_lib_[ng/ul]": "qubit_lib",
                  "size_selection": "size_selection",
                  "Qubit_size-selection_[ng/ul]": "qubit_size_selection",
                  "IDT xGen UDI Primer Pair Well": "primer_well",
                  "Primer Name": "primer_name",
                  "i5 index": "i5_index",
                  "i7 index": "i7_index",
                  "Bioanalyzer_avg_size": "bioanalyzer_avg_size",
                  "insert_size": "insert_size",
                  "[C]_nM_estimate": "concentration_nM",
                  "Data_Target_GB": "data_target_gb"}

    df = df.rename(columns=rename_map)

    keep = list(rename_map.values()) + ["library_id", "extraction_id", "lot_id",
                                        "species", "library_date", "library_kit"]

    return df[keep]

# Foreign key validation
def validate_foreign_keys(specimen_df, dna_df, lib_df):
    missing_lots = set(dna_df["lot_id"]) - set(specimen_df["lot_id"])
    if missing_lots:
        print("ERROR: DNAextraction references missing lot_ids:", missing_lots)

    missing_extractions = set(lib_df["extraction_id"]) - set(dna_df["extraction_id"])
    if missing_extractions:
        print("ERROR: GenomicLibraries references missing extraction_ids:", missing_extractions)

# Insert cleaned data into database
def insert_df(df, table, conn):
    df.to_sql(table, conn, if_exists="append", index=False)

if __name__ == "__main__":

    # load CSVs
    event_raw = pd.read_csv("/home/sorellanarebolledo/Final_project/datasets/Panama2021-MainSet/Panama2021 - EventData.csv")
    specimen_raw = pd.read_csv("/home/sorellanarebolledo/Final_project/datasets/Panama2021-MainSet/Panama2021 - SpecimenData.csv")
    dna_raw = pd.read_csv("/home/sorellanarebolledo/Final_project/datasets/Panama2021-MainSet/Panama2021 - DNAextractions.csv")
    lib_raw = pd.read_csv("/home/sorellanarebolledo/Final_project/datasets/Panama2021-MainSet/Panama2021 - GenomicLibraries.csv")

    print("Loaded event_raw:", event_raw.shape)

    # clean
    event_clean = clean_event_data(event_raw)
    specimen_clean = clean_specimen_data(specimen_raw)
    dna_clean = clean_dna_data(dna_raw)
    lib_clean = clean_libraries(lib_raw)

    print("Cleaned event_clean:", event_clean.shape)

    # validate
    validate_foreign_keys(specimen_clean, dna_clean, lib_clean)

    # connect to DB
    conn = sqlite3.connect("Invertebrate_Database.db")

    print("Inserting EventData...")

    # insert in correct order
    insert_df(event_clean, "EventData", conn)
    insert_df(specimen_clean, "SpecimenData", conn)
    insert_df(dna_clean, "DNAextraction", conn)
    insert_df(lib_clean, "GenomicLibraries", conn)

    conn.close()