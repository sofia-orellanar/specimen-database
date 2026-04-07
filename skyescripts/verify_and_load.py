import sqlite3
import pandas as pd
import os
import sys

# ===========================================================================
# STEP 0: CONFIGURATION
# ===========================================================================

db_path = "skyescripts/TEST_cunha_invertebrate_specimens.db"

#SCHEMA dictionary will be used to validate incoming table columns
#keys are 1 of the 4 tables in the database (EventData, SpecimenData, DNAextractions, GenomicLibraries)
#those contain dictionaries with keys for primary_key, foreign_keys, required_cols, optional_cols and their corresponding values
# optional_cols can be filled with NULL if missing values
SCHEMA = {
    "EventData": {
        "primary_key": "event_code",
        "foreign_keys": {},
        "required_cols": ["event_code"],
        "optional_cols": [
            "trip_id",
            "year",
            "month",
            "day",
            "date",
            "waypoint",
            "latitude",
            "longitude",
            "environment",
            "collecting_method",
            "depth",
            "locality",
            "locality_details",
            "city_district",
            "province",
            "area",
            "country",
            "collector",
            "event_notes",
        ],
    },
    "SpecimenData": {
        "primary_key": "lot_id",
        "foreign_keys": {"event_code": ("EventData", "event_code")},
        "required_cols": ["lot_id", "event_code"],
        "optional_cols": [
            "suffix",
            "species",
            "genus",
            "development",
            "habitat",
            "fixation_method",
            "specimen_count",
            "parts",
            "specimen_notes",
            "identification_by",
            "voucher",
            "second_voucher_clip",
            "dna_extracted",
            "phylum",
            "class_name",
            "subclass",
            "uncertainty",
            "collected_by",
        ],
    },
    "DNAExtractions": {
        "primary_key": "extraction_id",
        "foreign_keys": {"lot_id": ("SpecimenData", "lot_id")},
        "required_cols": ["extraction_id", "lot_id"],
        "optional_cols": [
            "extraction_date",
            "extraction_kit",
            "elution_ul",
            "qubit_dna_ng_ul",
            "nanodrop_ng_ul",
            "nanodrop_260_280",
            "nanodrop_260_230",
            "qubit_nanodrop_ratio",
            "clip_over",
            "contamination_plate",
            "contamination_wells",
            "extraction_notes",
            "piece_size",
            "qubit_after_speedvac",
            "extraction_suffix",
            "clipping_notes",
            "extracted_by",
            "coi",
            "pcr_by",
            "blast_best_match",
            "blast_max_score",
            "blast_total_score",
            "blast_query_cover",
            "blast_e_value",
            "blast_percent_identity",
            "blast_match_length",
            "blast_match_accession",
            "original_extraction_id",
        ],
    },
    "GenomicLibraries": {
        "primary_key": "library_id",
        "foreign_keys": {"extraction_id": ("DNAExtractions", "extraction_id")},
        "required_cols": ["library_id", "extraction_id"],
        "optional_cols": [
            "lot_id",
            "species",
            "library_date",
            "library_kit",
            "qubit_dna_ng_ul",
            "input_mass_ng",
            "input_vol_ul",
            "eb_complement_ul",
            "frag_time_min",
            "cycles",
            "elution_ul",
            "qubit_lib_ng_ul",
            "size_selection",
            "qubit_size_selection_ng_ul",
            "idt_primer_well",
            "primer_name",
            "i5_index",
            "i7_index",
            "bioanalyzer_avg_size",
            "insert_size",
            "concentration_nm_estimate",
            "data_target_gb",
        ],
    },
}

# Helper functions to better organize terminal output for clarity

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def ok(msg):
    print(f"[OK]{msg}")


def warn(msg):
    print(f"[WARNING]{msg}")


def error(msg):
    print(f"[ERROR]{msg}")


# ===========================================================================
# STEP 1: CHOOSE DB TABLE TO LOAD INTO
# ===========================================================================


def choose_table():
    section("Which table are you loading into?")
    tables = list(
        SCHEMA.keys()
    )  # return a list of the tables which are the keys in the SCHEMA dictionary
    for i, name in enumerate(tables, start=1):
        print(f"{i} -> {name}")
    print()

    while True:
        choice = input("Enter the number of the table (or 'q' to quit): ").strip()
        if choice.lower() == "q":
            print("Exiting selection")
            sys.exit(0)
        if choice.isdigit() and 1 <= int(choice) <= len(tables):
            selected = tables[int(choice) - 1]
            print(f"\n  Selected: {selected}")
            return selected
        print("Please enter a valid table number from the list above.")


# ===========================================================================
# STEP 1: LOAD GIVEN CSV
# ===========================================================================


def load_csv():
    section("Load your CSV file")
    while True:
        path = input("Enter the path to your CSV file (or 'q' to quit): ").strip()
        if path.lower() == "q":
            print("Goodbye!")
            sys.exit(0)
        if not os.path.exists(path):
            error(f"File not found: '{path}'. Please check the path and try again.")
            continue
        try:
            df = pd.read_csv(path)
            ok(f"Loaded '{path}' - Found {df.shape[0]} rows, {df.shape[1]} columns")
            return df, path
        except Exception as e:
            error(f"Could not read file: {e}")
