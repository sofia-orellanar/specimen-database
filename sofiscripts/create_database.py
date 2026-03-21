import sqlite3
import csv

db_path = "Invertebrate_Database.db"
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

#Create tables
cursor.executescript('''
PRAGMA foreign_keys = ON; -- allows for links

CREATE TABLE IF NOT EXISTS EventData (
    event_code TEXT PRIMARY KEY,
    trip_id TEXT,
    event_date TEXT NOT NULL,
    latitude REAL CHECK(latitude BETWEEN -90 AND 90),
    longitude REAL CHECK(longitude BETWEEN -180 AND 180),
    city TEXT,
    country TEXT,
    province TEXT,   
    collector TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS SpecimenData (
    lot_id TEXT PRIMARY KEY,
    voucher TEXT,
    identification_by TEXT,
    event_code TEXT,
    species TEXT,
    genus TEXT,
    family TEXT,
    development TEXT,          
    fixation_method TEXT,
    notes TEXT,
    -- this creates the link between the two tables:
    FOREIGN KEY (event_code) REFERENCES EventData (event_code) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);
                     
CREATE TABLE IF NOT EXISTS DNAextraction (
    extraction_id TEXT PRIMARY KEY,
    lot_id TEXT NOT NULL,
    extraction_date TEXT,
    FOREIGN KEY (lot_id) REFERENCES SpecimenData (lot_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS GenomicLibraries (
    library_id TEXT PRIMARY KEY,
    extraction_id TEXT NOT NULL,
    lot_id TEXT,
    species TEXT,
    library_date TEXT,
    library_kit TEXT,
    qubit_dna REAL,
    input_mass_ng REAL,
    input_vol_ul REAL,
    eb_complement_ul REAL,
    frag_time_min REAL,
    cycles INTEGER,
    elution_ul REAL,
    qubit_lib REAL,
    size_selection TEXT,
    qubit_size_selection REAL,
    primer_well TEXT,
    primer_name TEXT,
    i5_index TEXT,
    i7_index TEXT,
    bioanalyzer_avg_size REAL,
    insert_size REAL,
    concentration_nM REAL,
    data_target_gb REAL,
    FOREIGN KEY (extraction_id) REFERENCES DNAextraction (extraction_id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);
'''
)