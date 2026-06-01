import pandas as pd
import numpy as np

EXCEL_FILE = 'server_data.xlsx'
OUTPUT_FILE = 'cleaned_server_data.parquet'

print("--- 1. Data Ingestion ---")

metadata_df = pd.read_excel(EXCEL_FILE, sheet_name='Server_Metadata')
station1_df = pd.read_excel(EXCEL_FILE, sheet_name='Server_Performance_Station1')
station2_df = pd.read_excel(EXCEL_FILE, sheet_name='Server_Performance_Station2')

print("Data loaded!")

# -----------------------------
# 2. Clean Performance Logs


performance_df = pd.concat([station1_df, station2_df], ignore_index=True)



#cleaning
print("--- 2. Data Cleaning ---")

# Remove unwanted columns
columns_to_drop = ['Config_Version', 'Last_Patch_Date', 'Deployment_Token']
performance_df = performance_df.drop(columns=columns_to_drop, errors='ignore')

# Remove no-server rows
performance_df = performance_df.dropna(subset=['Server_ID'])

# Fix duplicates (same server & timestamp)
performance_df = performance_df.drop_duplicates(subset=['Server_ID', 'Log_Timestamp'])

# Imputations
performance_df['CPU_Utilization (%)'] = performance_df['CPU_Utilization (%)'].fillna(
    performance_df['CPU_Utilization (%)'].median()
)

performance_df['Memory_Usage (%)'] = performance_df['Memory_Usage (%)'].fillna(
    performance_df['Memory_Usage (%)'].median()
)

# Convert timestamp to datetime
performance_df['Log_Timestamp'] = pd.to_datetime(performance_df['Log_Timestamp'])

# Add pure date column
performance_df['Log_Date'] = performance_df['Log_Timestamp'].dt.date

# -----------------------------
# 3. Clean Server Metadata (DIM)


# Remove duplicate Server_IDs
metadata_df = metadata_df.drop_duplicates(subset=['Server_ID'])

# -----------------------------


print("--- 4. Data Enrichment (Join) ---")
# 4. Join

final_df = pd.merge(
    performance_df,
    metadata_df,
    on='Server_ID',
    how='left'
)

# Make names Power-BI friendly
final_df.columns = (
    final_df.columns
    .str.replace(" ", "_")
    .str.replace("[^A-Za-z0-9_]+", "", regex=True)
)

# Save
final_df.to_parquet(OUTPUT_FILE, index=False)

print("SAVED:", OUTPUT_FILE)
print(final_df.head())
