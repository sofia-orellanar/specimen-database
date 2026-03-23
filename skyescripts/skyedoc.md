# Skye's Notes

### Possible Interface

[DB Browser for SQLite](https://sqlitebrowser.org) -- possible early-stage GUI

## Workflow

1. Load and clean CSVs with pandas
2. Create database with proper links
3. Load all 4 Panama datasets
4. Test queries

- pandas handles the loading and cleaning
- SQLite handles everything else (db structure and querying)
- SQLite stores entire database as a single `.db` file

### Relational Databases

A relational database stores data in multiple tables that are LINKED to each other through shared ID columns called "keys." This avoids storing the same information in multiple places (redundancy).
 
In our database, the links work like this:

    EventData   <-- (event_code) --> SpecimenData
    SpecimenData <-- (lot_id)    --> DNAExtractions
    DNAExtractions <-- (extraction_id) --> GenomicLibraries
 
So if you want to know WHERE a DNA extraction came from geographically,
you only need to store the lot_id in the extractions table.
You can always "link" back to EventData to get the GPS coordinates. 

## PANDAS AND CLEANING

### DATA INSPECTION

EventData
- 33 rows, 25 columns
- linking key is `event_code`
--- Event Data column names ---
['trip_id', 'event_code', 'fieldwork_status', 'year', 'month', 'day', 'date', 'waypoint', 'latitude', 'longitude', 'environment', 'low_tide', 'collecting_method', 'depth', 'population', 'locality', 'locality_details', 'city_district', 'province', 'area', 'photos_env', 'country', 'collector', 'notes', 'use_in_map']

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


### CLEANED COLUMNS
- normalized column names
- removed use_in_map and population from EventData
- removed unnamed columns from SpecimenData


Cleaned Event columns:    ['trip_id', 'event_code', 'fieldwork_status', 'year', 'month', 'day', 'date', 'waypoint', 'latitude', 'longitude', 'environment', 'low_tide', 'collecting_method', 'depth', 'locality', 'locality_details', 'city_district', 'province', 'area', 'photos_env', 'country', 'collector', 'event_notes']

Cleaned Specimen columns: ['lot_id', 'suffix', 'event_code', 'species', 'genus', 'epithet', 'clade', 'family', 'development', 'habitat', 'fixation_method', 'specimen_count', 'parts', 'vial', 'operculum', 'specimen_notes', 'photos_org', 'identification_by', 'voucher', 'second_voucher_clip']

Cleaned DNA columns: ['extraction_id', 'lot_id', 'species', 'plate_id', 'plate_well', 'extraction_date', 'extraction_kit', 'elution_ul', 'qubit_dna_ng_ul', 'nanodrop_ng_ul', 'nanodrop_260_280', 'nanodrop_260_230', 'qubit_nanodrop_ratio', 'clip_over', 'contamination_plate', 'contamination_wells', 'extraction_notes', 'piece_size', 'qubit_after_speedvac']

Cleaned Genomic Library columns: ['library_id', 'extraction_id', 'lot_id', 'species', 'library_date', 'library_kit', 'qubit_dna_ng_ul', 'input_mass_ng', 'input_vol_ul', 'eb_complement_ul', 'frag_time_min', 'cycles', 'elution_ul', 'qubit_lib_ng_ul', 'size_selection', 'qubit_size_selection_ng_ul', 'idt_primer_well', 'primer_name', 'i5_index', 'i7_index', 'bioanalyzer_avg_size', 'insert_size', 'concentration_nm_estimate', 'data_target_gb']

### LOADING

**Schema are the rules the db uses**

PRIMARY KEY: every row has a unique identifier
FOREIGN KEY: a column in one table must match a valid value in another table
Data types: TEXT, INTEGER, REAL, etc

NOT NULL: this column must always have a value (can't be empty)
TEXT:stores text/string data
REAL:stores decimal numbers (floating point)
INTEGER:stores whole numbers

MUST BE in the order:

**Event->Specimen->Extraction->Library**

since later tables reference columns in previous tables (e.g. event_code)

## TEST QUERIES

**Querying**

WHERE: filter by a condition
JOIN ... ON: combine information across tables by matching shared ID columns
GROUP BY with COUNT(*): lets you ask aggregate questions e.g. "how many specimens per species?"
LIKE '%': pattern match, where % means "anything after this"

---- Query 1: List all collection events with locations and dates ----
('PAN21E020', '1-Apr-2021', 'Playa Estero', 7.62392, -81.24229, 'rocks')
('PAN20E001', '10-Feb-2020', 'Taboga', 8.80424, -79.56308, 'rocky beach')
('PAN20E002', '11-Feb-2020', 'Chepillo', 8.95329, -79.1236, 'rocks')
('PAN20E003', '11-Feb-2020', 'Chepillo', 8.94914, -79.13191, 'rocky outcrop')
('PAN20E009', '11-Mar-2020', 'Chumical', None, None, None)
  ... (33 total events)

---- Query 2: Find all specimens of a specific species ----
('PAN20E001S018', 'Fissurella virescens', 'PAN20E001', None)
('PAN20E001S019', 'Fissurella virescens', 'PAN20E001', 'USNM1665307')
('PAN20E001S020', 'Fissurella virescens', 'PAN20E001', None)
('PAN20E002S028', 'Fissurella virescens', 'PAN20E002', 'USNM1665308')
('PAN20E002S029', 'Fissurella virescens', 'PAN20E002', 'USNM1665309')
  (100 specimens found)

---- Query 3: All specimens from family Fissurellidae ----
('PAN20E001S005', 'Diodora inaequalis', 'Diodora', 'PAN20E001')
('PAN20E002S043', 'Diodora alta cf.', 'Diodora', 'PAN20E002')
('PAN20E004S070', 'Diodora alta', 'Diodora', 'PAN20E004')
('PAN20E004S071', 'Diodora alta', 'Diodora', 'PAN20E004')
('PAN20E004S082', 'Diodora alta', 'Diodora', 'PAN20E004')
  ... (135 total Fissurellidae specimens)

 ---- Query 4: JOIN two tables (combine specimen and event information
('PAN20E001S001', 'Vasula melones', 'Taboga', 8.80424, -79.56308, '10-Feb-2020')
('PAN20E001S002', 'Vasula melones', 'Taboga', 8.80424, -79.56308, '10-Feb-2020')
('PAN20E001S003', 'Columbellidae? sp.1', 'Taboga', 8.80424, -79.56308, '10-Feb-2020')       
('PAN20E001S004', 'Columbellidae? sp.1', 'Taboga', 8.80424, -79.56308, '10-Feb-2020')       
('PAN20E001S005', 'Diodora inaequalis', 'Taboga', 8.80424, -79.56308, '10-Feb-2020')        

---- Query 5: Specimens with associated DNA extractions ----
('gDNA-0002', 'PAN20E004S072', 'Lucapinella elenorae cf.', '10-Feb-2021', 95.3)
('gDNA-0010', 'PAN20E017S420', 'Diodora alta', '10-Feb-2021', 46.8)
('gDNA-0590', 'PAN21E030S942', 'Scurria stipulata', '10-Feb-2022', 25.8)
('gDNA-0591', 'PAN22E033S1060', 'Scurria stipulata', '10-Feb-2022', 7.98)
('gDNA-0592', 'PAN21E031S989', 'Scurria stipulata', '10-Feb-2022', 45.0)
  (782 total extractions in database)

 ---- Query 6: JOIN specimen, event, and extraction (three tables)----
Lot ID               Species                        Locality        Date            Extraction    DNA (ng/ul)
---------------------------------------------------------------------------------------------------------
PAN20E012S203        Diodora alta                   Playa El Uverito 17-Nov-2020     gDNA-0265           200.0
PAN20E015S319        Scurria stipulata              Playa Libertad, Punta Bejuco 15-Dec-2020     gDNA-0376           184.0
PAN20E017S436X01     Crepidula incurva              Estero de la Montaña 17-Dec-2020     gDNA-0731           181.0
PAN21E018S442X01     Nerita funiculata              Pedro González  29-Mar-2021     gDNA-0769           162.0
PAN20E014S266        Nerita funiculata              Playa El Salado 15-Nov-2020     gDNA-0520           146.0
PAN20E014S265        Nerita funiculata              Playa El Salado 15-Nov-2020     gDNA-0518           134.0
PAN21E021S600        Acanthais brevidentata         Playa Toro      25-Apr-2021     gDNA-0402           129.0
PAN20E004S082        Diodora alta                   Venado          12-Feb-2020     gDNA-0263           119.0

 ---- Query 7: Count specimens per species (aggregate query) ----
  Siphonaria palmata                       115 specimens
  Acanthais brevidentata                   107 specimens
  Fissurella virescens                     100 specimens
  Vasula melones                           97 specimens
  Scurria stipulata                        95 specimens
  Lottia filosa                            91 specimens
  Crepidula incurva                        88 specimens
  Nerita funiculata                        86 specimens
  Tegula picta                             66 specimens
  Tegula verrucosa                         33 specimens

 ---- Query 8: Specimens with voucher numbers----
('PAN20E004S064', 'Crepidula incurva', 'USNM1664595')
('PAN20E004S064B', 'Crepidula incurva', 'USNM1664596')
('PAN20E004S066', 'Crepidula incurva', 'USNM1664597')
('PAN20E004S066B', 'Crepidula incurva', 'USNM1664598')
('PAN20E004S064', 'Crepidula incurva', 'USNM1664595')
('PAN20E004S064B', 'Crepidula incurva', 'USNM1664596')
('PAN20E004S066', 'Crepidula incurva', 'USNM1664597')
('PAN20E004S066B', 'Crepidula incurva', 'USNM1664598')
('PAN20E004S064B', 'Crepidula incurva', 'USNM1664596')
('PAN20E004S066', 'Crepidula incurva', 'USNM1664597')
('PAN20E004S066B', 'Crepidula incurva', 'USNM1664598')
('PAN20E004S066', 'Crepidula incurva', 'USNM1664597')
('PAN20E004S066B', 'Crepidula incurva', 'USNM1664598')
('PAN20E004S066B', 'Crepidula incurva', 'USNM1664598')
('PAN20E004S067', 'Crepidula incurva', 'USNM1664599')
('PAN20E004S068', 'Crepidula incurva', 'USNM1664600')
('PAN20E004S068B', 'Crepidula incurva', 'USNM1664601')
('PAN20E004S069', 'Crepidula incurva', 'USNM1664602')
  ... (898 total USNM vouchers)

# Roadmap

1. Wrap queries into their own functions? e.g. `get_specimens_by_species("Fissurella virescens")`









