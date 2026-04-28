import sqlite3
import urllib.request
import json
import time
import urllib.parse

# ===========================================================================
# STEP 0: CONFIGURATION
# ===========================================================================

db_path = "database-scripts/cunha_invertebrate_specimens.db"

# Create a dictionary to map the columns to the keys that GBIF will return

TAXONOMY_MAP = {
    "phylum": "phylum",
    "class_name": "class",  # use "class_name" because "class" is used in Python
    "subclass": "subclass",  # GBIF won't always return subclass
    "family": "family",
    "taxon_order": "order",  # use "taxon_order" because "order" is used in Python
}
CONFIDENCE_THRESHOLD = 90  # start with a confidence score of 90 for matches

REQUEST_DELAY = 0.3  # add a delay between API calls as to not overload server

# ===========================================================================
# STEP 1: ADD MISSING COLUMNS TO THE DATABASE
# ===========================================================================
# We need to add new columns for different levels
# Some of which were removed during cleaning (e.g. family)


def add_missing_cols(cursor):
    """Add any taxonomy columns that don't already exist in SpecimenData."""
    print("\n--- Checking for missing taxonomy columns... ---")
    for db_col in TAXONOMY_MAP.keys():
        try:
            cursor.execute(f"ALTER TABLE SpecimenData ADD COLUMN {db_col} TEXT;")
            print(f"  Added new column to SpecimenData: {db_col}")
        except sqlite3.OperationalError:
            # Column already exists — this is expected for phylum, class_name, subclass
            print(f"  Column already exists in Specimen Data. Skipping: {db_col}")


# ===========================================================================
# STEP 2: FETCH TAXONOMY FROM GBIF
# ===========================================================================

# GBIF takes a name as the query and returns the most confident taxonomy matches
# we can query with the full species name, or fall back to genus


def fetch_gbif_taxonomy(genus, species):
    """
    Query the GBIF species match API and return a dict of taxonomy fields,
    or None if no confident match was found.
    """

    # If species name is unknown or incomplete, fall back to using the Genus as the search term
    species_is_unknown = not species or str(species).strip().lower() in (
        "sp.",
        "sp",
        "nan",
        "none",
        "",
    )

    if species_is_unknown:
        search_name = str(genus).strip()
    else:
        # Combine genus + species into a full name
        search_name = f"{str(genus).strip()} {str(species).strip()}"

    # GBIF doesn't require an API key, you can just build a URL for the query
    base_url = "https://api.gbif.org/v1/species/match"
    query = urllib.parse.urlencode({"name": search_name, "verbose": "false"})
    url = f"{base_url}?{query}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"    [API ERROR] Could not reach GBIF for search '{search_name}': {e}")
        return None


# ===========================================================================
# STEP 3: FILL FUNCTION
# ===========================================================================


def fill_taxonomy(conn):
    cursor = conn.cursor()

    # find all rows with at least one NULL entry in a taxonomy field
    null_check = " OR ".join([f"{col} IS NULL" for col in TAXONOMY_MAP.keys()])
    # WHERE checks if any of the five expected columns are NULL
    # This ensures rows that already have info are skipped
    cursor.execute(
        f"""
        SELECT lot_id, genus, species
        FROM SpecimenData
        WHERE {null_check}
    """
    )
    rows_needing_fill = cursor.fetchall()

    if not rows_needing_fill:
        print("\nNo rows with missing taxonomy found.")
        return

    print(
        f"\nFound {len(rows_needing_fill)} row(s) with at least one NULL taxonomy field."
    )

    # build a dictionary where key = tuple of (genus, species)
    # and value = list of lot_ids that match that combination
    # this is a "De-duplication step" so that if we onlny need to make 1 API call
    # for each species instead of calling the API for every instance of that species
    species_groups = {}
    for lot_id, genus, species in rows_needing_fill:
        key = (
            str(genus).strip() if genus else "",
            str(species).strip() if species else "",
        )
        if key not in species_groups:
            species_groups[key] = []
        species_groups[key].append(lot_id)

    print(
        f"Found {len(species_groups)} unique genus+species combination(s) to look up.\n"
    )

    filled_count = 0  # rows successfully updated
    skipped_count = 0  # rows skipped
    no_match_log = []  # species we couldn't find on GBIF

    # loop through each unique species and call GBIF API
    for (genus, species), lot_ids in species_groups.items():

        display_name = f"{genus} {species}".strip() or "[no name]"
        print(f"  Looking up: {display_name} ({len(lot_ids)} row(s))")

        # Call GBIF
        gbif_result = fetch_gbif_taxonomy(genus, species)

        # good practice to pause between requests to not overload API
        time.sleep(REQUEST_DELAY)

        if gbif_result is None:
            print(f"    -> No match found on GBIF. Skipping.")
            no_match_log.append(display_name)
            skipped_count += len(lot_ids)
            continue

        print(
            f"Found matched name: {gbif_result['matched_name']}"
            f"(confidence: {gbif_result['confidence']}, type: {gbif_result['match_type']})"
        )

        # for each database column, update if
        # we were able to find a match AND the current entry is NULL (so it needs to be filled)
        for db_col, gbif_key in TAXONOMY_MAP.items():
            gbif_value = gbif_result.get(gbif_key)

            if gbif_value is None:
                continue  # couldn't find a match

            # Update only NULL cells in this column
            placeholders = ",".join(["?" for _ in lot_ids])
            cursor.execute(
                f"""
                UPDATE SpecimenData
                SET {db_col} = ?
                WHERE lot_id IN ({placeholders})
                  AND {db_col} IS NULL
            """,
                [gbif_value] + lot_ids,
            )

        filled_count += len(lot_ids)

    conn.commit()

    print("\n" + "=" * 60)
    print("  Completed Filling Taxonomy Information!")
    print("=" * 60)
    print(f"  Rows updated:      {filled_count}")
    print(f"  Rows skipped:      {skipped_count}")

    if no_match_log:
        print(f"\n  {len(no_match_log)} species had no GBIF match:")
        for name in no_match_log:
            print(f"    - {name}")
        print("\n  Consider reviewing these manually.")
    else:
        print("\n  All species matched successfully!")

 
if __name__ == "__main__":
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
 
    print("="*60)
    print("  Performing GBIF Taxonomy Filling")
    print("="*60)
    
    # Make sure all taxonomy columns exist
    add_missing_cols(cursor)
    conn.commit()
 
    # Perform look up adn fill functions
    fill_taxonomy(conn)
 
    conn.close()
    print("\nFinished Taxonomy Filling.\n")