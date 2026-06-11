CREATE DATABASE ServerPerfDB;

USE ServerPerfDB;



CREATE TABLE dbo.DimServer (
    Server_ID        VARCHAR(20)    NOT NULL,
    Hostname         VARCHAR(100),
    IP_Address       VARCHAR(50),
    OS_Type          VARCHAR(50),
    Server_Location  VARCHAR(100),
    Admin_Name       VARCHAR(100),
    Server_Cluster   VARCHAR(50),
    Admin_Email      VARCHAR(150),
    CONSTRAINT PK_DimServer PRIMARY KEY NONCLUSTERED (Server_ID) NOT ENFORCED
);

CREATE TABLE dbo.DimDate (
    Date_Key         INT            NOT NULL,
    Full_Date        DATE,
    Day_Num          INT,
    Month_Num        INT,
    Month_Name       VARCHAR(20),
    Quarter          INT,
    Year_Num         INT,
    CONSTRAINT PK_DimDate PRIMARY KEY NONCLUSTERED (Date_Key) NOT ENFORCED
);

CREATE TABLE dbo.FactServerPerformance (
    Log_ID                  VARCHAR(50)    NOT NULL,
    Server_ID               VARCHAR(20),
    Log_Timestamp           DATETIME2,
    Log_Date                DATE,
    CPU_Utilization_pct     FLOAT,
    Memory_Usage_pct        FLOAT,
    Disk_IO_pct             FLOAT,
    Network_Traffic_In_MBs  FLOAT,
    Network_Traffic_Out_MBs FLOAT,
    Uptime_Hours            FLOAT,
    Downtime_Hours          FLOAT,
    Server_Cluster          VARCHAR(50),
    CONSTRAINT PK_Fact PRIMARY KEY NONCLUSTERED (Log_ID) NOT ENFORCED
);