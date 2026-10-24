# Pharma Manufacturing Data Schema
The dataset consists of **three relational tables**, designed to mirror real MES, historian, and LIMS systems used in pharmaceutical manufacturing.

## 1. Table: `batch_log` (Parent / MES-Level Table)
The `batch_log` table represents one manufactured batch per row and serves as the parent table for all other datasets.

### Columns

1. **Batch_ID**
   Unique identifier for each manufacturing batch.

2. **Product_ID**
   Name of the product being manufactured.
   Example values:

   * `CardioStat_IR` (Mixing-sensitive)
   * `NeuroCalm_IR` (Granulation-sensitive)
   * `GastroEase_CR` (Coating-sensitive)

3. **Start_Timestamp**
   Date and time when batch manufacturing began.

4. **Operator**
   Operator responsible for running the batch.

5. **Line_ID**
   Manufacturing line on which the batch was produced.


## 2. Table: `process_params` (Process / Equipment / Historian Data)
The `process_params` table captures process-level measurements in a vertical Entity–Attribute–Value (EAV) format.
Each batch produces multiple rows in this table—one per parameter per manufacturing step.

### Columns

1. **Batch_ID**
   Foreign key referencing `batch_log.Batch_ID`.

2. **Step**
   Manufacturing step where the parameter was recorded.
   Values: `Mixing`, `Granulation`, `Coating`

3. **Param_Name**
   Name of the measured process parameter.

4. **Param_Value**
   Numeric value recorded for the parameter.

## 3. Table: `quality_qc` (Quality / LIMS Data)
The `quality_qc` table contains final quality outcomes for each batch and provides the target variable for modeling.

### Columns

1. **Batch_ID**
   Foreign key referencing `batch_log.Batch_ID`.

2. **Assay**
   Active ingredient purity percentage.

3. **Dissolution**
   Percentage of drug dissolved within the specified time.

4. **Impurity**
   Percentage of unwanted chemical impurities.

5. **Hardness**
   Tablet hardness measurement.

6. **OOS_Flag**
   Out-of-Spec indicator:

   * `1` → Batch failed specifications
   * `0` → Batch passed specifications

## 4. Product-Specific Risk Profiles
Each product has different dominant risk drivers, making the dataset realistic and industry-grade.

| Product_ID    | Primary Sensitivity   |
| ------------- | --------------------- |
| CardioStat_IR | Mixing-sensitive      |
| NeuroCalm_IR  | Granulation-sensitive |
| GastroEase_CR | Coating-sensitive     |

## 5. Process Parameters: Critical vs Supporting
Each manufacturing step contains:

* **Critical parameters** → Can directly cause batch failure
* **Supporting parameters** → Modify or amplify risk but rarely cause failure alone

Supporting parameters may:

* Compensate for minor deviations in critical parameters, or
* Amplify the impact of critical parameters when they are out of control

### 5.1 Mixing Parameters

| Parameter        | Type       |
| ---------------- | ---------- |
| Mixing_Speed_RPM | Critical   |
| Mixing_Time_Min  | Critical   |
| Blender_Load_%   | Supporting |

### 5.2 Granulation Parameters

| Parameter              | Type       |
| ---------------------- | ---------- |
| Granulation_Temp_C     | Critical   |
| Granulation_Moisture_% | Critical   |
| Granulation_Time_Min   | Supporting |

### 5.3 Coating Parameters

| Parameter          | Type       |
| ------------------ | ---------- |
| Coating_Spray_Rate | Critical   |
| Inlet_Temp_C       | Critical   |
| Coating_Time_Min   | Supporting |

> Target specification ranges for all parameters will be defined later.

## 6. Causal OOS Logic (Core Design Principle)
Out-of-Spec (OOS) outcomes are not randomly assigned.

OOS probability is driven by a combination of:

1. Distance from specification limits
2. **Product-specific sensitivity
3. Compounding parameter effects
4. Random process noise

### Conceptual Examples

* **NeuroCalm_IR**
  High granulation temperature and high moisture
  → Increased impurity
  → Higher OOS risk

* **CardioStat_IR**
  Low mixing speed
  → Poor content uniformity
  → Assay failure

* **GastroEase_CR**
  High coating spray rate and low inlet temperature
  → Poor coating quality
  → Dissolution failure

This causal structure ensures explainable and realistic analytics.

## 7. OOS Rate Assumption
* Target OOS rate: 8–12%
* Chosen to balance realism and model learnability

## 8. Data Volume
* Total batches: 1,000–1,500
* Suitable for SQL analysis, EDA, modeling, and debugging

## 9. Mental Model of Data Generation
High-level logic used to generate the dataset:

```
For each batch:
    Assign product, operator, and manufacturing line
    Generate process parameters (within and outside spec ranges)
    Compute quality metrics using causal rules
    Add controlled random noise
    Assign OOS_Flag based on quality thresholds
```