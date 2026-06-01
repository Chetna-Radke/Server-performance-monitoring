import pandas as pd
import numpy as np

EXCEL_FILE = 'server_data.xlsx'
OUTPUT_FILE = 'cleaned_server_data.parquet'

# ----------------------------
# 1. Data Ingestion
# ----------------------------
print("--- 1. Data Ingestion ---")

metadata_df = pd.read_excel(EXCEL_FILE, sheet_name='Server_Metadata')
station1_df = pd.read_excel(EXCEL_FILE, sheet_name='Server_Performance_Station1')
station2_df = pd.read_excel(EXCEL_FILE, sheet_name='Server_Performance_Station2')

print(f"Station1 rows: {len(station1_df)}, Station2 rows: {len(station2_df)}")
print("Data loaded!")

# ----------------------------
# 2. Clean Performance Logs
# ----------------------------
print("--- 2. Data Cleaning ---")

performance_df = pd.concat([station1_df, station2_df], ignore_index=True)
print(f"Combined rows before cleaning: {len(performance_df)}")

# Remove unwanted columns
columns_to_drop = ['Config_Version', 'Last_Patch_Date', 'Deployment_Token']
performance_df = performance_df.drop(columns=columns_to_drop, errors='ignore')

# Remove rows with no Server_ID
performance_df = performance_df.dropna(subset=['Server_ID'])

# Remove duplicate entries (same server & timestamp)
performance_df = performance_df.drop_duplicates(subset=['Server_ID', 'Log_Timestamp'])

# Impute missing numeric values with median
performance_df['CPU_Utilization (%)'] = performance_df['CPU_Utilization (%)'].fillna(
    performance_df['CPU_Utilization (%)'].median()
)
performance_df['Memory_Usage (%)'] = performance_df['Memory_Usage (%)'].fillna(
    performance_df['Memory_Usage (%)'].median()
)

# Convert timestamp to datetime and extract date
performance_df['Log_Timestamp'] = pd.to_datetime(performance_df['Log_Timestamp'])
performance_df['Log_Date'] = performance_df['Log_Timestamp'].dt.date

print(f"Combined rows after cleaning: {len(performance_df)}")

# ----------------------------
# 3. Clean Server Metadata
# ----------------------------
print("--- 3. Metadata Cleaning ---")

metadata_df = metadata_df.drop_duplicates(subset=['Server_ID'])
print(f"Unique servers in metadata: {len(metadata_df)}")

# ----------------------------
# 4. Data Enrichment (Join)
# ----------------------------
print("--- 4. Data Enrichment (Join) ---")

final_df = pd.merge(
    performance_df,
    metadata_df,
    on='Server_ID',
    how='left'
)

print(f"Final dataset rows: {len(final_df)}, columns: {len(final_df.columns)}")

# Make column names Power BI friendly (no spaces or special characters)
final_df.columns = (
    final_df.columns
    .str.replace(" ", "_")
    .str.replace("[^A-Za-z0-9_]+", "", regex=True)
)

# ----------------------------
# 5. Export
# ----------------------------
final_df.to_parquet(OUTPUT_FILE, index=False)

print(f"\nSaved: {OUTPUT_FILE}")
print("\nSample output:")
print(final_df.head())
print("\nColumns:", list(final_df.columns))
