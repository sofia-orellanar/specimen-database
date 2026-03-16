EventData
- 782 rows, 19 columns
- linking key is `event_code`
--- Event Data column names ---
['extraction_id', 'lot_id', 'species', 'plate_id', 'plate_well', 'extraction_date', 'extraction_kit', 'elution_ul', 'Qubit_DNA_[ng/ul]', 'Nanodrop_[ng/ul]', 'Nanodrop_260/280', 'Nanodrop_260/230', 'Qubit : Nanodrop', 'clip_over', 'contamination_plate', 'contamination_wells', 'extraction_notes', 'piece_size', 'Qubit_after_SpeedVac']

Specimen Data
- 1,106 rows, 21 columns
- each specimen has a `lot_id`
- each specimen links to an `event_code`

--- Specimen Data column names ---
['lot_id', 'sufix', 'event_code', 'species', 'genus', 'epithet', 'clade', 'family', 'development', 'habitat', 'fixation_method', 'specimens', 'parts', 'vial', 'operculum', 'notes', 'photos_org', 'identification_by', 'Voucher', 'SecondVoucherClip', 'Unnamed: 20']  

DNAExtractions
- 782 rows, 19 columns
- each has an `extraction_id`
- each links to a `lot_id`

--- DNA Extraction column names ---
['extraction_id', 'lot_id', 'species', 'plate_id', 'plate_well', 'extraction_date', 'extraction_kit', 'elution_ul', 'Qubit_DNA_[ng/ul]', 'Nanodrop_[ng/ul]', 'Nanodrop_260/280', 'Nanodrop_260/230', 'Qubit : Nanodrop', 'clip_over', 'contamination_pla'Qubit_after_SpeedVac']

Genomic Libraries
- 11 rows, 24 columns
- each references an `extraction_id`

--- Genomic Library column names ---
['library_id', 'extraction_id', 'lot_id', 'species', 'library_date', 'library_kit', 'Qubit_DNA_[ng/ul]', 'input_mass_ng', 'input_vol_ul', 'EB_complement_ul', 'frag_time_min', 'cycles', 'elution_ul', 'Qubit_lib_[ng/ul]', 'size_selection', 'Qubit_size-selection_[ng/ul]', 'IDT xGen UDI Primer Pair Well', 'Primer Name', 'i5 index', 'i7 index', 'Bioanalyzer_avg_size', 'insert_size', '[C]_nM_estimate', 'Data_Target_GB']

**Event->Specimen->Extraction->Library**

SQLite stores entire database as a single `.db` file

1. Load and clean CSVs with pandas
2. Create database with proper links
3. Load all 4 Panama datasets
4. Test queries

[DB Browser for SQLite](https://sqlitebrowser.org) -- possible early-stage GUI

**Schema are the rules the db uses**
PRIMARY KEY: every row has a unique identifier
FOREIGN KEY: a column in one table must match a valid value in another table
Data types: TEXT, INTEGER, REAL, etc

**Querying**
WHERE: filter by a condition
JOIN ... ON: combine information across tables by matching shared ID columns
GROUP BY with COUNT(*): lets you ask aggregate questions e.g. "how many specimens per species?"
LIKE 'USNM%': pattern match, where % means "anything after this"