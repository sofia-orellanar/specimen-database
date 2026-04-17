# ===========================================================================
# TESTING EXAMPLE QUERIES
# ===========================================================================

import sqlite3
import pandas as pd

# connect to database file we made
conn = sqlite3.connect("skyescripts\\panama_specimens.db")
cur = conn.cursor()

"""
SQL query structure:

SELECT [columns you want]
FROM   [table name]
WHERE  [filter condition]      <- optional
JOIN   [other table] ON [...]  <- optional, links tables together
ORDER BY [column] ASC/DESC     <- optional, sorts results
LIMIT  [number]                <- optional, caps number of results

The asterisk (*) in SELECT means "all columns"
"""
print("\n---- Query 1: List all collection events with locations and dates ----")
# Send query to database
# This is a simple SELECT query that just retrieves specific columns
# and sorts them by date (ascending order)
cur.execute(
    """
    SELECT event_code, date, locality, latitude, longitude, environment
    FROM EventData
    ORDER BY date ASC;
"""
)
rows = cur.fetchall()  # Return results as a list of tuples
for row in rows[:5]:  # Print first 5
    print(row)
print(f"  ... ({len(rows)} total events)")


print("\n---- Query 2: Find all specimens of a specific species ----")
# WHERE condition: "only return rows where the species column matches this string exactly"
cur.execute(
    """
    SELECT lot_id, species, event_code, voucher
    FROM SpecimenData
    WHERE species = 'Fissurella virescens';
"""
)
rows = cur.fetchall()
for row in rows[:5]:
    print(row)
print(f"  ({len(rows)} specimens found)")


print("\n---- Query 3: All specimens from family Fissurellidae ----")
# ORDER BY genus (alphabetically)
cur.execute(
    """
    SELECT lot_id, species, genus, event_code
    FROM SpecimenData
    WHERE family = 'Fissurellidae'
    ORDER BY genus;
"""
)
rows = cur.fetchall()
for row in rows[:5]:
    print(row)
print(f"  ... ({len(rows)} total Fissurellidae specimens)")


print("\n ---- Query 4: JOIN two tables (combine specimen and event information")
# AS s and AS e gives short alias to each table
# use these prefixes in SELECT to specify which table you're getting the columns from
# ON s.event_code = e.event_code - joining coniditon: "For each specimen row, find the event row where the values of event_code match, and then make them one row"
cur.execute(
    """
    SELECT s.lot_id, s.species, e.locality, e.latitude, e.longitude, e.date
    FROM SpecimenData AS s
    JOIN EventData AS e ON s.event_code = e.event_code
    LIMIT 5;
"""
)
rows = cur.fetchall()
for row in rows:
    print(row)


print("\n---- Query 5: Specimens with associated DNA extractions ----")
cur.execute(
    """
    SELECT d.extraction_id, d.lot_id, d.species, d.extraction_date, d.qubit_dna_ng_ul
    FROM DNAExtractions AS d
    ORDER BY d.extraction_date
    LIMIT 5;
"""
)
rows = cur.fetchall()
for row in rows:
    print(row)
total = cur.execute("SELECT COUNT(*) FROM DNAExtractions").fetchone()[0]
print(f"  ({total} total extractions in database)")


print("\n ---- Query 6: JOIN specimen, event, and extraction (three tables)----")
# Same as Query 4but with three tables (two JOIN statements)
# each JOIN adds a new table and specifies what column is linking is to the previous table
cur.execute(
    """
    SELECT 
        s.lot_id,
        s.species,
        e.locality,
        e.date AS collection_date,
        d.extraction_id,
        d.qubit_dna_ng_ul AS dna_concentration
    FROM SpecimenData AS s
    JOIN EventData AS e ON s.event_code = e.event_code
    JOIN DNAExtractions AS d ON s.lot_id = d.lot_id
    ORDER BY d.qubit_dna_ng_ul DESC
    LIMIT 8;
"""
)
rows = cur.fetchall()
print(
    f"{'Lot ID':<20} {'Species':<30} {'Locality':<15} {'Date':<15} {'Extraction':<12} {'DNA (ng/ul)':>12}"
)
print("-" * 105)
for row in rows:
    print(
        f"{str(row[0]):<20} {str(row[1]):<30} {str(row[2]):<15} {str(row[3]):<15} {str(row[4]):<12} {str(row[5]):>12}"
    )


print("\n ---- Query 7: Count specimens per species (aggregate query) ----")
# GROUP BY collapses all rows with the same species name into a single group
# COUNT(*) counts how many rows are in each group
# AS specimen_count gives that count a column name
cur.execute(
    """
    SELECT species, COUNT(*) AS specimen_count
    FROM SpecimenData
    GROUP BY species
    ORDER BY specimen_count DESC
    LIMIT 10;
"""
)
rows = cur.fetchall()
for row in rows:
    print(f"  {row[0]:<40} {row[1]} specimens")


print("\n ---- Query 8: Specimens with voucher numbers----")
# % is a wildcard - so matches ANY voucher that STARTS with USNM
cur.execute(
    """
    SELECT lot_id, species, voucher
    FROM SpecimenData
    WHERE voucher LIKE 'USNM%'
    ORDER BY voucher;
"""
)
rows = cur.fetchall()
for row in rows[:8]:
    print(row)
usnm_count = len(
    cur.execute("SELECT lot_id FROM SpecimenData WHERE voucher LIKE 'USNM%'").fetchall()
)
print(f"  ... ({usnm_count} total USNM vouchers)")

conn.close()  # Close connection
