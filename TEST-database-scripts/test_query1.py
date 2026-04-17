import sqlite3
import pandas as pd

path= "TEST-database-scripts/"
db_name = "cunha_invertebrate_specimens.db"

query= """
SELECT species, COUNT(*) AS specimen_count
FROM SpecimenData
GROUP BY species
ORDER BY specimen_count DESC
LIMIT 10
"""
query_name= 'test_query1'
conn = sqlite3.connect(path + db_name)
result_df = pd.read_sql_query(query, conn)
print(result_df)
result_df.to_csv(path + query_name+".csv", index=False)