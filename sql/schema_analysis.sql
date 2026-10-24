-- ==============================================================================
-- Pharma OOS Early-Warning System: Database Setup & Analytical Query
-- Author: Kunal Rao
-- RDBMS: MySQL
-- ==============================================================================

-- 1. Create and Use Schema
CREATE SCHEMA IF NOT EXISTS pharma_project;
USE pharma_project;

-- ==============================================================================
-- 2. DDL: Create Tables
-- ==============================================================================

select * from quality_table;
select * from process_parameters;
select * from batch_log;

CREATE TABLE batch_log (
    Batch_ID VARCHAR(50) PRIMARY KEY,
    Product_ID VARCHAR(50),
    Line_ID VARCHAR(50),
    Operator VARCHAR(50),
    StartTimestamp DATETIME
);

CREATE TABLE quality_table (
    Batch_ID VARCHAR(50) PRIMARY KEY,
    Assay DECIMAL(10,4),
    Dissolution DECIMAL(10,4),
    Impurity DECIMAL(10,4),
    Hardness INT,
    OOS_Flag INT
);

CREATE TABLE process_parameters (
    Batch_ID VARCHAR(50),
    Param_Name VARCHAR(100),
    Param_Value DECIMAL(10,4)
);

-- ==============================================================================
-- 3. Data Loading Instructions
-- ==============================================================================
-- INSTRUCTIONS FOR MYSQL WORKBENCH USERS:
-- Option A (Easiest): Right-click each table in the Schema Navigator on the left -> "Table Data Import Wizard" -> Select your CSV.
-- Option B: Uncomment and update the file paths below to use LOAD DATA LOCAL INFILE.

/*
LOAD DATA LOCAL INFILE '/path/to/data/raw/batch_log.csv'
INTO TABLE batch_log
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '/path/to/data/raw/quality_table.csv'
INTO TABLE quality_table
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '/path/to/data/raw/process_parameters.csv'
INTO TABLE process_parameters
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
*/

-- ==============================================================================
-- 4. Analytical Processing (CTEs, Pivoting, Window Functions)
-- ==============================================================================

WITH raw_logs AS (
    SELECT 
        b.Batch_ID,
        b.Product_ID,
        b.Line_ID,
        b.Operator,
        b.StartTimestamp,
        q.OOS_Flag,
        q.Assay,
        q.Dissolution
    FROM batch_log b
    LEFT JOIN quality_table q 
        ON b.Batch_ID = q.Batch_ID
),

process_pivoted AS (
    -- Pivoting the process params to get 1 row per batch
    SELECT 
        Batch_ID,
        MAX(CASE WHEN Param_Name = 'Mixing_Speed_RPM' THEN Param_Value END) AS mix_speed,
        MAX(CASE WHEN Param_Name = 'Granulation_Temp_C' THEN Param_Value END) AS gran_temp,
        MAX(CASE WHEN Param_Name = 'Coating_Spray_Rate' THEN Param_Value END) AS spray_rate,
        MAX(CASE WHEN Param_Name = 'Granulation_Moisture_%' THEN Param_Value END) AS moisture
    FROM process_parameters
    GROUP BY Batch_ID
),

combined_data AS (
    SELECT 
        r.Batch_ID,
        r.Product_ID,
        r.Line_ID,
        r.Operator,
        r.StartTimestamp,
        p.mix_speed,
        p.gran_temp,
        p.spray_rate,
        p.moisture,
        r.OOS_Flag
    FROM raw_logs r
    JOIN process_pivoted p 
        ON r.Batch_ID = p.Batch_ID
),

rolling_features AS (
    SELECT 
        *,
        -- 5 batch moving avg for temp on the same line to check for equipment drift
        AVG(gran_temp) OVER (
            PARTITION BY Line_ID 
            ORDER BY StartTimestamp 
            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
        ) AS line_rolling_temp,
        
        -- Rank operators by how many batches they have run so far (experience metric)
        DENSE_RANK() OVER (
            PARTITION BY Operator 
            ORDER BY StartTimestamp
        ) AS operator_batch_count,
        
        -- Difference in mix speed from the previous batch on the same line
        mix_speed - LAG(mix_speed, 1) OVER (
            PARTITION BY Line_ID ORDER BY StartTimestamp
        ) AS mix_speed_delta
    FROM combined_data
)

-- Final selection for EDA rules and ML feature ingestion
SELECT 
    Batch_ID,
    Product_ID,
    Line_ID,
    Operator,
    mix_speed,
    gran_temp,
    line_rolling_temp,
    mix_speed_delta,
    operator_batch_count,
    OOS_Flag,
    -- Risk categorisation based on initial manual EDA limits
    CASE 
        WHEN mix_speed < 130 AND gran_temp > 60 THEN 'High Risk'
        WHEN moisture > 3.0 THEN 'Moisture Warning'
        ELSE 'Normal'
    END AS manual_risk_category
FROM rolling_features
WHERE StartTimestamp >= '2023-01-01'
ORDER BY StartTimestamp DESC;
