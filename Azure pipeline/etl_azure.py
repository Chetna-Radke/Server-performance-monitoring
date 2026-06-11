import pandas as pd
import numpy as np
from azure.storage.filedatalake import DataLakeServiceClient
from sqlalchemy import create_engine
import io
import os

# ── CONFIG ─────────────────────────────────────────────────────────────────────
# Replace 'serverperfdata' with your actual storage account name if different
STORAGE_ACCOUNT = "serverperfdata"
STORAGE_KEY     = os.environ["ADLS_KEY"]      # set this as environment variable
CONTAINER_RAW   = "raw"
CONTAINER_PROC  = "processed"
EXCEL_FILENAME  = "server_data.xlsx"

SYNAPSE_SERVER  = "synapse-server-monitoring.sql.azuresynapse.net"
SYNAPSE_DB      = "ServerPerfDB"
SYNAPSE_USER    = "sqladmin"
SYNAPSE_PASSWORD = os.environ["SYNAPSE_PW"]   # set this as environment variable
# ───────────────────────────────────────────────────────────────────────────────


# ── 1. READ EXCEL FROM AZURE DATA LAKE ─────────────────────────────────────────
print("--- 1. Reading Excel from Azure Data Lake ---")

service_client = DataLakeServiceClient(
    account_url=f"https://{STORAGE_ACCOUNT}.dfs.core.windows.net",
    credential=STORAGE_KEY
)

file_system_client = service_client.get_file_system_client(CONTAINER_RAW)
file_client = file_system_client.get_file_client(EXCEL_FILENAME)
raw_bytes = file_client.download_file().readall()

xl = pd.ExcelFile(io.BytesIO(raw_bytes))
metadata_df = xl.parse("Server_Metadata")
station1_df = xl.parse("Server_Performance_Station1")
station2_df = xl.parse("Server_Performance_Station2")

print(f"Station1: {len(station1_df)} rows | Station2: {len(station2_df)} rows")
print("Excel loaded from Data Lake successfully.")


# ── 2. CLEAN PERFORMANCE LOGS ───────────────────────────────────────────────────
print("--- 2. Data Cleaning ---")

performance_df = pd.concat([station1_df, station2_df], ignore_index=True)
print(f"Combined rows before cleaning: {len(performance_df)}")

# Remove configuration-only columns not needed for analysis
columns_to_drop = ["Config_Version", "Last_Patch_Date", "Deployment_Token"]
performance_df = performance_df.drop(columns=columns_to_drop, errors="ignore")

# Remove rows with no Server_ID (no referential integrity)
performance_df = performance_df.dropna(subset=["Server_ID"])

# Remove duplicate log entries (same server + same timestamp)
performance_df = performance_df.drop_duplicates(subset=["Server_ID", "Log_Timestamp"])

# Impute missing numeric metrics with column median
performance_df["CPU_Utilization (%)"] = performance_df["CPU_Utilization (%)"].fillna(
    performance_df["CPU_Utilization (%)"].median()
)
performance_df["Memory_Usage (%)"] = performance_df["Memory_Usage (%)"].fillna(
    performance_df["Memory_Usage (%)"].median()
)

# Parse timestamp and extract date
performance_df["Log_Timestamp"] = pd.to_datetime(performance_df["Log_Timestamp"])
performance_df["Log_Date"] = performance_df["Log_Timestamp"].dt.date

print(f"Cleaned rows after dedup and imputation: {len(performance_df)}")


# ── 3. CLEAN SERVER METADATA ────────────────────────────────────────────────────
print("--- 3. Metadata Cleaning ---")
metadata_df = metadata_df.drop_duplicates(subset=["Server_ID"])
print(f"Unique servers in metadata: {len(metadata_df)}")


# ── 4. JOIN: FACT + DIMENSION ───────────────────────────────────────────────────
print("--- 4. Enrichment Join ---")
final_df = pd.merge(performance_df, metadata_df, on="Server_ID", how="left")
print(f"Final dataset: {len(final_df)} rows x {len(final_df.columns)} columns")

# Standardise column names for SQL / Power BI compatibility
final_df.columns = (
    final_df.columns
    .str.replace(" ", "_")
    .str.replace("[^A-Za-z0-9_]+", "", regex=True)
)


# ── 5. WRITE CLEANED DATA BACK TO DATA LAKE (processed container) ──────────────
print("--- 5. Saving Parquet to Data Lake processed container ---")
parquet_buffer = io.BytesIO()
final_df.to_parquet(parquet_buffer, index=False)
parquet_buffer.seek(0)

proc_fs = service_client.get_file_system_client(CONTAINER_PROC)
parquet_client = proc_fs.get_file_client("cleaned_server_data.parquet")
parquet_client.upload_data(parquet_buffer.read(), overwrite=True)
print("Parquet saved to Data Lake processed/cleaned_server_data.parquet")


# ── 6. LOAD INTO AZURE SYNAPSE SQL TABLES ──────────────────────────────────────
print("--- 6. Loading into Azure Synapse ---")

connection_string = (
    f"mssql+pyodbc://{SYNAPSE_USER}:{SYNAPSE_PASSWORD}"
    f"@{SYNAPSE_SERVER}/{SYNAPSE_DB}"
    f"?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
)
engine = create_engine(connection_string, fast_executemany=True)

# ── FactServerPerformance ──
fact_cols = [
    "Log_ID", "Server_ID", "Log_Timestamp", "Log_Date",
    "CPU_Utilization__", "Memory_Usage__", "Disk_IO__",
    "Network_Traffic_In_MBs", "Network_Traffic_Out_MBs",
    "Uptime_Hours", "Downtime_Hours", "Server_Cluster"
]
fact_df = final_df[[c for c in fact_cols if c in final_df.columns]].copy()
fact_df.to_sql(
    "FactServerPerformance", engine,
    if_exists="replace", index=False, schema="dbo"
)
print(f"FactServerPerformance loaded: {len(fact_df)} rows")

# ── DimServer ──
dim_server_cols = [
    "Server_ID", "Hostname", "IP_Address", "OS_Type",
    "Server_Location", "Admin_Name", "Server_Cluster", "Admin_Email"
]
dim_server_df = final_df[[c for c in dim_server_cols if c in final_df.columns]].drop_duplicates("Server_ID")
dim_server_df.to_sql(
    "DimServer", engine,
    if_exists="replace", index=False, schema="dbo"
)
print(f"DimServer loaded: {len(dim_server_df)} rows")

# ── DimDate (generated from log dates in the data) ──
from datetime import date
dates = pd.date_range(
    start=final_df["Log_Timestamp"].min(),
    end=final_df["Log_Timestamp"].max(),
    freq="D"
)
dim_date_df = pd.DataFrame({
    "Date_Key":   dates.strftime("%Y%m%d").astype(int),
    "Full_Date":  dates.date,
    "Day":        dates.day,
    "Month":      dates.month,
    "Month_Name": dates.strftime("%B"),
    "Quarter":    dates.quarter,
    "Year":       dates.year
})
dim_date_df.to_sql(
    "DimDate", engine,
    if_exists="replace", index=False, schema="dbo"
)
print(f"DimDate loaded: {len(dim_date_df)} rows")

print("\n✓ Azure ETL pipeline completed successfully.")
print(f"  Fact rows:   {len(fact_df)}")
print(f"  Dim servers: {len(dim_server_df)}")
print(f"  Dim dates:   {len(dim_date_df)}")
