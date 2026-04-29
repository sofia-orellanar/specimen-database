import sqlite3
import pandas as pd
import os
import sys

# ===========================================================================
# STEP 0: CONFIGURATION
# ===========================================================================

db_path = "TEST-database-scripts/TEST_cunha_invertebrate_specimens.db"

# A SCHEMA dictionary will be used to validate incoming table columns
# the dictionary is populated by the build_schema() function based on the live database, ensuring it reflects the most current updates to the SCHEMA rather than hardcoding columns

#   primary_key  : the single primary key column name (str)
#   foreign_keys : {col: (referenced_table, referenced_col), ...}
#   required_cols: [primary key col] + [foreign key cols]
#   optional_cols: all other columns (will be entered as NULL if missing from CSV)

SCHEMA = {}
def build_schema(conn):
    """
    Reads the live database schema using 2 PRAGMA queries per table.
    The result is used to update the module-level SCHEMA dict so all downstream validation functions (choose_table, validate, etc) see it without any changes to those functions.

    """
    cursor = conn.cursor()

    # get all user-defined tables
    tables = [
        row[0]
        for row in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    ]

    schema = {}
    for table in tables:

        # Primary Key
        # get all column names and identify the primary key
        # (Any row where pk field > 0, # 0 means not part of pk)
        cols_info = cursor.execute(f"PRAGMA table_info({table})").fetchall()
        pk_cols = [row[1] for row in cols_info if row[5] > 0]
        # all tables in this database have a single-column pk
        primary_key = pk_cols[0] if pk_cols else None

        # Foreign Keys
        # get foreign key relationships
        # build in {local_col: (ref_table, ref_col)} format
        fk_info = cursor.execute(f"PRAGMA foreign_key_list({table})").fetchall()
        foreign_keys = {row[3]: (row[2], row[4]) for row in fk_info}


        # Required Columns: primary key + any foreign key columns
        # must be present in every CSV or database fails
        # Optional Columns = everything else
        # missing columns will be entered as NULL
        required_cols = []
        if primary_key:
            required_cols.append(primary_key)
        for fk_col in foreign_keys:
            if fk_col not in required_cols:
                required_cols.append(fk_col)

        all_cols = [row[1] for row in cols_info]
        optional_cols = [col for col in all_cols if col not in required_cols]

        schema[table] = {
            "primary_key": primary_key,
            "foreign_keys": foreign_keys,
            "required_cols": required_cols,
            "optional_cols": optional_cols,
        }

    return schema


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
# STEP 2: LOAD GIVEN CSV
# ===========================================================================


def load_csv():
    section("Load your CSV file")
    while True:
        path = input("Enter the path to your CSV file (or 'q' to quit): ").strip()
        if path.lower() == "q":
            print("Quitting CSV loading.")
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


# ===========================================================================
# STEP 3: CSV VALIDATION
# ===========================================================================


def validate(df, table_name, conn):
    """
    Function to validate the incoming CSV against the existing database schema prior to loading, by
    performing the following checks:

      1. Required columns are present
      2. Primary key column has no missing values
      3. Primary key has no duplicates within the CSV itself
      4. Primary key values don't already exist in the database (would break INSERT)
      5. Foreign key values all point to real rows in the referenced table
      6. Warn about unrecognized columns (could be typos)
      7. Warn about missing optional columns (will become NULL)

    Returns two lists: fatal_errors (must fix or loading will break) and warnings (require review but do not break the loading).
    """
    schema = SCHEMA[table_name]  # Call schema dictionary for the table
    pk = schema["primary_key"]  # Call primary key for the table
    csv_cols = set(df.columns)  # Get the columns in the CSV as a set

    fatal_errors = []  # These are a list of errors that will prevent a safe load
    warnings = []  # These are worth flagging but won't break the load

    section("Validating your CSV...")

    # -----------------------------------------------------------------------
    # 1. Check that the CSV contains all required columns
    # -----------------------------------------------------------------------
    section("[1] Checking required columns...")

    for col in schema["required_cols"]:

        if col not in csv_cols:

            fatal_errors.append(
                f"Required column '{col}' is missing from your CSV. "
                f"This column is the {'primary key' if col == pk else 'foreign key / required field'} "
                f"for {table_name}."
            )
            error(f"Missing required column: '{col}'")

        else:
            ok(f"Found required column: '{col}'")

    # -----------------------------------------------------------------------
    # 2. Check that the primary key column contains no missing/null values
    # -----------------------------------------------------------------------
    section("[2] Checking for missing values in primary key '{pk}'...")

    if pk in df.columns:

        null_pk_rows = df[df[pk].isna()]  # any NaN values

        if not null_pk_rows.empty:

            fatal_errors.append(
                f"{len(null_pk_rows)} row(s) have a blank/null value in '{pk}'. "
            )
            error(
                f"{len(null_pk_rows)} row(s) with missing primary key "
                f"\n Row indices: {null_pk_rows.index.tolist()}"
            )

        else:
            ok(f"No missing values in '{pk}'")

    # -----------------------------------------------------------------------
    # 3. Check for duplicate primary keys within the CSV itself
    # -----------------------------------------------------------------------
    section("[3] Checking for duplicate primary keys within the CSV...")

    if pk in df.columns:

        dupes_in_csv = df[
            df[pk].duplicated(keep=False)
        ]  # keep=False marks all duplicates as True, not just the second/subsequent occurences

        if not dupes_in_csv.empty:
            dupe_vals = dupes_in_csv[pk].unique().tolist()
            fatal_errors.append(
                f"{len(dupes_in_csv)} row(s) share duplicate values in '{pk}': {dupe_vals}. "
            )
            error(f"Duplicate primary keys within your CSV: {dupe_vals}")
        else:
            ok("No duplicate primary keys within the CSV")

    # -----------------------------------------------------------------------
    # 4. Check for conflicts with primary keys already in the database
    # -----------------------------------------------------------------------
    section("[4] Checking for primary key conflicts with existing database rows...")

    if pk in df.columns:

        cursor = conn.cursor()
        existing_pks = set(
            str(row[0])
            for row in cursor.execute(f"SELECT {pk} FROM {table_name}").fetchall()
        )  # query the database for all existing primary key values in the target table and store in a set
        csv_pks = set(
            df[pk].dropna().astype(str)
        )  # store the primary key values from the CSV in a set
        # use dropna() to ignore any missing values (already flagged as an error above)
        conflicts = (
            csv_pks & existing_pks
        )  # find any overlap between the CSV primary keys and existing database primary keys

        if conflicts:
            fatal_errors.append(
                f"{len(conflicts)} value(s) in '{pk}' already exist in the database: "
                f"{sorted(conflicts)}. "
            )
            error(
                f"Primary key conflicts with existing database primary keys: {sorted(conflicts)}"
            )
        else:
            ok(
                f"No primary key conflicts with existing database "
                f"({len(existing_pks)} existing rows checked)"
            )

    # -----------------------------------------------------------------------
    # 5. Check correct foreign key references if applicable
    # -----------------------------------------------------------------------
    section("[5] Checking foreign key references...")

    for fk_col, (ref_table, ref_col) in schema["foreign_keys"].items():
        if fk_col not in csv_cols:
            ok("No foreign keys to check for this table.")

        cursor = conn.cursor()
        valid_refs = set(
            str(row[0])
            for row in cursor.execute(f"SELECT {ref_col} FROM {ref_table}").fetchall()
        )  # query the database for all valid reference values in the parent table and store in a set

        csv_fk_values = df[fk_col].dropna().astype(str)
        invalid_refs = (
            set(csv_fk_values) - valid_refs
        )  # find any foreign key values in the CSV that don't reference a valid parent row in the database
        orphan_rows = df[df[fk_col].astype(str).isin(invalid_refs)]

        if invalid_refs:
            fatal_errors.append(
                f"{len(orphan_rows)} row(s) in column '{fk_col}' reference values that don't exist in {ref_table}.{ref_col}: {sorted(invalid_refs)}. "
                f"This could be caused by needing to load the parent rows first."
            )
            error(
                f"Foreign key error: '{fk_col}' references {ref_table}.{ref_col}. "
                f"Unknown values: {sorted(invalid_refs)} "
                f"({len(orphan_rows)} affected row(s))"
            )
            # Save orphans to a csv for review
            orphan_path = f"TEST-database-scripts/orphan_{table_name}_{fk_col}.csv"
            orphan_rows.to_csv(orphan_path, index=False)
            warn(f"Orphan rows saved to '{orphan_path}' for review")
        else:
            ok(
                f"All values in '{fk_col}' match existing "
                f"{ref_table}.{ref_col} entries"
            )

    # -----------------------------------------------------------------------
    # 6. Warn about columns in the CSV that the schema doesn't recognize
    # -----------------------------------------------------------------------
    section("[6] Checking for unrecognized columns...")

    all_existing_cols = set(schema["required_cols"]) | set(schema["optional_cols"])
    unknown_cols = csv_cols - all_existing_cols
    if unknown_cols:
        for col in sorted(unknown_cols):
            warnings.append(
                f"Column '{col}' is not in the existing {table_name} schema. "
                f"It will still be inserted, but verify it's not a typo or other mistake."
            )
            warn(f"Unrecognized column (will still be inserted): '{col}'")
    else:
        ok("All CSV columns are recognized by the schema")

    # -----------------------------------------------------------------------
    # 7. Warn about optional columns that are missing from the CSV
    # -----------------------------------------------------------------------
    section("[7] Checking for missing optional columns...")

    missing_optional = [col for col in schema["optional_cols"] if col not in csv_cols]
    if missing_optional:
        for col in missing_optional:
            warnings.append(
                f"Optional column '{col}' not found in your CSV. "
                f"It will still be inserted but automatically filled with NULL values."
            )
            warn(f"Optional column missing (will be inserted with NULL): '{col}'")
    else:
        ok("All optional columns are present")

    return fatal_errors, warnings


# ===========================================================================
# STEP 4: DATABASE INSERTION
# ===========================================================================


def insert_data(df, table_name, conn):

    section("Inserting data into database...")

    try:
        df.to_sql(table_name, conn, if_exists="append", index=False)
        conn.commit()
        ok(f"Successfully inserted {len(df)} row(s) into {table_name}!")

    except Exception as e:
        error(f"Database insertion failed: {e}")
        print(
            "\n  The database has NOT been modified. "
            "Please fix the issue and try again."
        )
        sys.exit(1)  # Exit with error code to indicate failure


# ===========================================================================
# MAIN FUNCTION
# ===========================================================================


def main():

    if not os.path.exists(db_path):
        error(
            f"Database not found at '{db_path}'. "
            f"Please run at least panama_clean_load.py first to create the database,then use this script to add future data."
        )
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")

    ok(f"Connected to database at '{db_path}'")

    # Step 1: Choose target table
    table_name = choose_table()

    # Step 2: Load CSV into a DataFrame
    df, csv_path = load_csv()

    # Step 3: Validate
    fatal_errors, warnings = validate(df, table_name, conn)
    section("Validation Results")

    if fatal_errors:
        print(
            f"\n  Found {len(fatal_errors)} fatal error(s) that MUST be fixed (CSV will not load):\n"
        )
        for i, err in enumerate(fatal_errors, 1):
            print(f"  {i}. {err}\n")

    if warnings:
        print(
            f"\n  Found {len(warnings)} warning(s) that require review (CSV will still load):\n"
        )
        for i, w in enumerate(warnings, 1):
            print(f"  {i}. {w}\n")

    if not fatal_errors and not warnings:
        print("\n  All validation checks passed. Continuing to insertion.")

    # If there are fatal errors, we stop completely
    if fatal_errors:
        print(
            "\n  Cannot proceed with insertion until fatal errors are resolved."
            "\n  Please fix the issues listed above in your CSV and run this script again."
        )
        conn.close()
        sys.exit(1)

    # If there are only warnings, let the user decide whether to proceed
    if warnings:
        print("\n  There are warnings, but no fatal errors.")
        proceed = (
            input("  Do you want to proceed with insertion anyway? (yes/no): ")
            .strip()
            .lower()
        )
        if proceed not in ("yes", "y"):
            print("\n  Insertion cancelled. No changes were made to the database.")
            conn.close()
            sys.exit(0)

    # Step 4: Insert
    insert_data(df, table_name, conn)

    conn.close()
    print("\n  Done! You can now query the database for your new records.\n")


if __name__ == "__main__":
    main()
