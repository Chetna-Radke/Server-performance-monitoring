# Azure Pipeline

This folder is the cloud migration of the local ETL pipeline to Microsoft Azure.

\---

## What was built

The same ETL logic from `ETL\_PIPELINE.py` was adapted to run entirely inside Azure — reading data from Azure Data Lake, processing it in a Synapse Notebook, and saving output back to the cloud.

\---

## What was achieved

|Step|Status|Details|
|-|-|-|
|Upload raw data to Azure Data Lake|Done|server\_data.xlsx in raw/ container|
|Run ETL inside Synapse Notebook|Done|4940 rows processed, 20 columns|
|Save Parquet to Data Lake|Done|processed/cleaned\_server\_data.parquet|
|Save CSVs to Data Lake|Done|fact and dim tables as CSV|
|Create Synapse star schema tables|Done|FactServerPerformance, DimServer, DimDate|
|Azure Data Factory daily trigger|Done|pl\_server\_etl pipeline with schedule|
|Power BI cloud refresh|Not set up|Requires organisational Microsoft account|

\---

## Why Power BI cloud refresh was not connected

Power BI Service and Azure Data Lake/Synapse connections require an organisational Microsoft account (work or school email). Personal Gmail-based Azure free trial accounts are blocked from this connection by Microsoft. This is a licensing restriction, not a technical limitation of the pipeline itself.

The Power BI dashboard works fully when connected to the local Parquet output.

\---

## Services used

|Service|Purpose|Cost|
|-|-|-|
|Azure Data Lake Storage Gen2|Stores raw Excel and processed output|Free up to 5 GB|
|Azure Data Factory|Schedules and triggers the ETL daily|Free 1000 runs/month|
|Azure Synapse Analytics|Cloud data warehouse, star schema SQL tables|Free serverless + dedicated pool|

\---

## Files

|File|What it is|
|-|-|
|`etl\_azure.py`|ETL script using os.environ for safe credential handling|
|`create\_synapse\_tables.sql`|SQL DDL for the star schema in Synapse|
|`requirements\_azure.txt`|Python dependencies for Azure|

\---

## How to run locally against Azure

```bash
pip install -r requirements\_azure.txt

# Windows
set ADLS\_KEY=your\_storage\_account\_key
set SYNAPSE\_PW=your\_synapse\_password

# Mac/Linux
export ADLS\_KEY=your\_storage\_account\_key
export SYNAPSE\_PW=your\_synapse\_password

python etl\_azure.py
```

\---

## Architecture

```
server\_data.xlsx
      |
Azure Data Lake Storage Gen2 (raw/ container)
      |
Azure Data Factory — daily schedule trigger
      |
Synapse Notebook (etl\_azure.py logic)
      |
      |-----> Data Lake processed/ container (Parquet + CSV)
      |
Azure Synapse Analytics — ServerPerfDB
      ├── dbo.FactServerPerformance
      ├── dbo.DimServer
      └── dbo.DimDate
```

