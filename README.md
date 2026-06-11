# Server Performance Monitoring

###### Author: Chetna Radke  

###### Role: Data Analyst  

###### Tools: Python (Pandas), Power BI, Excel, Azure 

###### 

\---

XYZ Corporation had no central way to track how their servers were performing. Metrics like CPU usage, disk I/O, and downtime were sitting in raw Excel files across two monitoring stations with no visibility. I built an end-to-end data pipeline to fix that — from raw data to a Power BI dashboard stakeholders can actually use.

\---

## What this project does

Takes raw server logs from two monitoring stations, cleans and joins them with server metadata, loads everything into a star schema, and delivers an interactive Power BI dashboard. The same pipeline was then migrated to Microsoft Azure for cloud-scale deployment.

\---

## Tech stack

Python (Pandas) · Power BI · Azure Data Lake Storage Gen2 · Azure Data Factory · Azure Synapse Analytics · Excel · Parquet

\---

## Repository structure

```
server-performance-project/
├── ETL\_PIPELINE.py                        # Local ETL — runs on your machine
├── server\_data.xlsx                       # Raw source data
├── cleaned\_server\_data.parquet            # ETL output
├── server\_performance\_dashboard.pbix      # Power BI dashboard
├── Case\_Study\_Documentation.docx          # Full project writeup
├── requirements.txt                       # Python dependencies
├── azure-pipeline/                        # Cloud version of the pipeline
│   ├── etl\_azure.py                       # ETL adapted for Azure
│   ├── create\_synapse\_tables.sql          # Star schema DDL
│   ├── requirements\_azure.txt             # Azure dependencies
│   └── README\_azure.md                    # Azure pipeline documentation
└── screenshots/                           # Evidence of working pipeline
```

\---

## Local pipeline — how to run

```bash
pip install -r requirements.txt
python ETL\_PIPELINE.py
```

Then open the `.pbix` file in Power BI Desktop and refresh.

\---

## What the ETL does

The raw data had several issues that needed handling:

* Station 1 and Station 2 logs were in separate sheets — concatenated them
* Some rows had no Server\_ID — dropped those
* CPU and memory had nulls — filled with column median
* Duplicate entries for the same server at the same timestamp — deduplicated
* Joined performance logs with server metadata on Server\_ID
* Saved output as Parquet — faster to read, smaller file size than CSV

\---

## Data model — star schema

`FactServerPerformance` holds the metrics: CPU %, memory %, disk I/O, network traffic in/out, uptime hours, downtime hours. One row per server per log entry.

`DimServer` holds server attributes: OS type, cluster, location, administrator.

`DimDate` holds the calendar hierarchy for time-based filtering.

\---

## Dashboard highlights

* 4 KPI cards: total servers, total downtime hours, average CPU, average disk I/O
* Line chart: CPU utilization trend over time
* Bar chart: top servers by downtime
* Donut chart: downtime split by OS type
* Slicers: filter by year, month, OS type, server cluster

\---

## Azure pipeline

The `azure-pipeline/` folder contains the full cloud migration of this project. See `azure-pipeline/README\_azure.md` for details.

**Services used:** Azure Data Lake Storage Gen2 · Azure Data Factory · Azure Synapse Analytics

**What was achieved on Azure free tier:**

* Raw Excel file uploaded to Data Lake Storage Gen2 (raw container)
* ETL pipeline executed inside Azure Synapse Notebook — 4940 rows processed
* Cleaned Parquet and CSV files saved to Data Lake processed container
* Star schema tables created in Azure Synapse dedicated SQL pool
* Azure Data Factory pipeline created with daily schedule trigger

**Known limitation:** Automated Spark-to-Synapse SQL loading and Power BI cloud refresh require an organisational Microsoft account, which is not available on a personal Azure free trial. Data is available in the Data Lake processed container as Parquet and CSV for downstream use.

\---

## Requirements

```
pandas
numpy
openpyxl
pyarrow
```

Python 3.8+

