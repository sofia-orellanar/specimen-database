import sqlite3
import pandas as pd
import os


event_df = pd.read_csv("Panama2021-Main-Dataset\Panama2021-DNAextractions.csv")
specimen_df = pd.read_csv("Panama2021-Main-Dataset\Panama2021-SpecimenData.csv")
dna_df = pd.read_csv("Panama2021-Main-Dataset\Panama2021-DNAextractions.csv")
library_df = pd.read_csv("Panama2021-Main-Dataset\Panama2021-GenomicLibraries.csv")

print(f"\nEvent Data:        {event_df.shape[0]} rows, {event_df.shape[1]} columns")
print(f"Specimen Data:     {specimen_df.shape[0]} rows, {specimen_df.shape[1]} columns")
print(f"DNA Extractions:   {dna_df.shape[0]} rows, {dna_df.shape[1]} columns")
print(f"Genomic Libraries: {library_df.shape[0]} rows, {library_df.shape[1]} columns")

print("\n--- Event Data column names ---")
print(list(event_df.columns))

print("\n--- Specimen Data column names ---")
print(list(specimen_df.columns))

print("\n--- DNA Extraction column names ---")
print(list(dna_df.columns))

print("\n--- Genomic Library column names ---")
print(list(library_df.columns))
