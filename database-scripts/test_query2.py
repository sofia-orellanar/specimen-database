import sqlite3
import pandas as pd

path= "database-scripts/"
db_name = "cunha_invertebrate_specimens.db"

query= """
SELECT voucher, species, extraction_date, qubit_dna_ng_ul
FROM SpecimenData
JOIN EventData on SpecimenData.event_code = EventData.event_code
JOIN DNAExtractions on SpecimenData.lot_id= DNAExtractions.lot_id
WHERE qubit_dna_ng_ul > 100 AND Voucher != 'NA'
ORDER BY Qubit_DNA_ng_ul DESC
"""
query_name= 'test_query2'
conn = sqlite3.connect(path + db_name)
result_df = pd.read_sql_query(query, conn)
print(result_df)
result_df.to_csv(path + query_name+".csv", index=False)