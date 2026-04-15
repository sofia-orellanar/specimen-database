import sqlite3

#connecting to database
conn = sqlite3.connect("database-scripts/cunha_invertebrate_specimens.db")
cursor = conn.cursor()

#running ALTER TABLE statements
cursor.executescript("""
ALTER TABLE SpecimenData ADD COLUMN museum TEXT;
ALTER TABLE SpecimenData ADD COLUMN specimenlocation_id TEXT;
ALTER TABLE SpecimenData ADD COLUMN specimenlocation_shelf TEXT;

ALTER TABLE GenomicLibraries ADD COLUMN librarylocation_id TEXT;
ALTER TABLE GenomicLibraries ADD COLUMN librarylocation_shelf TEXT;
ALTER TABLE GenomicLibraries ADD COLUMN librarylocation_rack TEXT;
ALTER TABLE GenomicLibraries ADD COLUMN librarylocation_box TEXT;

ALTER TABLE DNAExtractions ADD COLUMN dnalocation_id TEXT;
ALTER TABLE DNAExtractions ADD COLUMN dnalocation_shelf TEXT;
ALTER TABLE DNAExtractions ADD COLUMN dnalocation_rack TEXT;
ALTER TABLE DNAExtractions ADD COLUMN dnalocation_box TEXT;
""")

#committing changes
conn.commit()
conn.close()