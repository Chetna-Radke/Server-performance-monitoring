# Server Performance Monitoring — Data Engineering & Analytics

**Author:** Chetna Radke  
**Role:** Data Analyst  
**Tools:** Python (Pandas), Power BI, Excel

---

## Project Overview

XYZ Corporation operates multiple virtual servers supporting critical applications. This project implements an end-to-end data pipeline that ingests raw server performance logs, applies data cleaning and transformation, models the data using a star schema, and delivers actionable insights through an interactive Power BI dashboard.

---

## Architecture

```
Raw Excel Files
      ↓
Python ETL Pipeline (Pandas)
      ↓
Cleaned Parquet Dataset
      ↓
Power BI Star Schema Model
      ↓
Interactive Power BI Dashboard
```

---

## Project Files

| File | Description |
|---|---|
| `ETL_PIPELINE.py` | Python ETL script — ingests, cleans, enriches, and exports data |
| `server_data.xlsx` | Raw input data (Server_Metadata, Station1 & Station2 performance logs) |
| `cleaned_server_data.parquet` | Output of the ETL pipeline — used by Power BI |
| `server_performance_monitoring_dashboard.pbix` | Power BI dashboard file |
| `Case_Study_Documentation.docx` | Full case study writeup |
| `requirements.txt` | Python dependencies |

---

## How to Run

**1. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**2. Run the ETL pipeline**

```bash
python ETL_PIPELINE.py
```

This reads `server_data.xlsx`, cleans the data, and outputs `cleaned_server_data.parquet`.

**3. Open the dashboard**

Open `server_performance_monitoring_dashboard.pbix` in Power BI Desktop and refresh the data source to point to the generated `.parquet` file.

---

## Data Model — Star Schema

**Fact Table**
- `FactServerPerformance` — CPU utilization, disk I/O, downtime hours, log date

**Dimension Tables**
- `DimServer` — OS type, cluster, administrator, server location
- `DimDate` — date, month, quarter, year

---

## ETL Pipeline Steps

1. **Ingestion** — reads three Excel sheets (Server_Metadata, Station1, Station2)
2. **Cleaning** — removes irrelevant columns, drops rows with missing Server IDs, deduplicates on Server_ID + timestamp
3. **Imputation** — fills missing CPU and memory values with the median
4. **Enrichment** — joins performance logs with server metadata
5. **Export** — saves the final dataset as Parquet for efficient downstream use

---

## Key Business Insights

- A small subset of servers contributes disproportionately to overall downtime
- Performance trends vary by time period, indicating potential seasonal patterns
- Downtime differs by OS type, highlighting platform-level considerations
- Cluster-based filtering enables prioritized infrastructure optimization

---

## Scalability & Future Enhancements

This solution is designed for extension into a cloud-native architecture:

| Component | Current | Future (Azure) |
|---|---|---|
| Orchestration | Manual script execution | Azure Data Factory |
| Storage | Local / GitHub | Azure Data Lake Storage Gen2 |
| Processing | Pandas (local) | Azure Synapse Analytics |
| Scheduling | Manual | ADF Pipelines (automated) |
| Monitoring | Power BI manual refresh | Power BI Premium auto-refresh |

Additional future enhancements:
- Real-time streaming ingestion
- Anomaly detection and automated alerting
- Incremental data loads instead of full refresh

---

## Requirements

```
pandas
numpy
openpyxl
pyarrow
```

Python 3.8 or higher recommended.
