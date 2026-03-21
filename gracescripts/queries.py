import sqlite3
import pandas as pd

path= "/home/gfinger/specimen-database/"
db_name = "Panama.db"

# writing queries...
    # SELECT -> column names you want; if this column exists in multiple tables you're querying, need to specify with "table.column"
    # FROM -> table you're querying. for my db strucutre, specimen is sort of the central table
    # JOIN -> if you want to access data from more than 1 table
        # joining specimen to event? JOIN event ON specimen.event_code = event.event_code
        # joining specimen to dna? JOIN dna ON specimen.lot_id = dna.lot_id
        # joining dna to libraries? JOIN libraries ON dna.extraction_id = libraries.extraction_id

        # LEFT JOIN to include rows that may be missing data (i.e., in query 3, i used left join to still get all rows with specimen, event and dna even if they are not in libraries)
    # WHERE -> filtering for specific values in a certain column. can use !=, =, >, <, <=, >=, <> as well as AND OR NOT BETWEEN LIKE and IS NULL

### EXAMPLE QUERIES ###
# what Lot IDs for genus Vasula that have entries in event and dna?

query1 = """
SELECT specimen.lot_id
FROM specimen
JOIN event ON specimen.event_code = event.event_code
JOIN dna ON specimen.lot_id = dna.lot_id
WHERE genus= 'Vasula'
"""
# All columns for genus Vasula that have entries in event and dna?
query2 = """
SELECT *
FROM specimen
JOIN event ON specimen.event_code = event.event_code
JOIN dna ON specimen.lot_id = dna.lot_id
WHERE genus= 'Vasula'
"""
# listed columns for genus Vasula with a voucher number that has an entry in event and dna, and may have an entry in libraries?
query3 = """
SELECT specimen.lot_id, specimen.event_code, dna.extraction_id, library_id, specimen.species, specimen_notes, event_notes, locality, collector, Voucher
FROM specimen
JOIN event ON specimen.event_code = event.event_code
JOIN dna ON specimen.lot_id = dna.lot_id
LEFT JOIN libraries ON dna.extraction_id = libraries.extraction_id
WHERE genus= 'Vasula' AND Voucher != 'NA'
"""
# what specimens are in collection in a museum and collected after 2020?
query4= """
SELECT lot_id, Voucher, species, event.date
FROM specimen
JOIN event on specimen.event_code = event.event_code
WHERE year > 2020 AND Voucher != 'NA'
"""
#related to query 4, which of these have been sequenced with yields better than 50 ng/ul, in order of genus then best to worst yield?
query5= """
SELECT specimen.lot_id, Voucher, museum, specimen.species, event.date, Qubit_DNA_ng_ul, extraction_date
FROM specimen
JOIN event on specimen.event_code = event.event_code
JOIN dna on specimen.lot_id = dna.lot_id
WHERE year > 2020 AND Voucher != 'NA' AND Qubit_DNA_ng_ul > 50
ORDER BY genus ASC, Qubit_DNA_ng_ul DESC
"""

### RUNNING THE QUERY THROUGH PANDAS
query_name = "query5"
query= query5

conn = sqlite3.connect(path + db_name)
result_df = pd.read_sql_query(query, conn)
print(result_df)
result_df.to_csv(path + query_name+".csv", index=False)