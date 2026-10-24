# 📊 Pharma OOS Early-Warning System (End-to-End ML Project)

## 1. Executive Summary

Out-of-Specification (OOS) results in pharmaceutical manufacturing lead to batch rejections, regulatory investigations, and significant cost.
This project develops an **early-warning machine learning system** that predicts whether a batch is likely to go OOS **before QC testing**, using **only batch execution logs and process parameters**.

The solution prioritizes **catching OOS batches early** over raw accuracy and is designed with **regulatory realism**, **data leakage prevention**, and **business trade-offs** in mind.

---

## 2. Business Objective

- Predict **OOS_Flag**

- `0` → In-Specification
- `1` → Out-of-Specification
- Use **only pre-QC data**
- Minimize **missed OOS batches** (high-risk events)
- Accept controlled false alarms (operationally manageable)

---

## 3. Project Structure

```
pharma-OOS-analysis/
│
├── app/             ← Frontend Streamlit application script (app.py)
├── data/            ← Raw, cleaned datasets, and final engineered features
├── models/          ← Exported machine learning models (pharma_oos_model.pkl)
├── notebooks/       ← Sequential Jupyter Notebooks for data processing and modeling
├── sql/             ← SQL scripts for data extraction and aggregation
├── README.md        ← Project documentation
└── requirements.txt ← Environment dependencies
```

---

## 4. Stage 1 – Data Generation

**Notebook:** `01_data_generation.ipynb`

A realistic, pharma-style synthetic dataset was created to simulate:

- Batch execution logs
- Process parameters (mixing, granulation, coating, inlet temperature)
- QC outcomes used **only to generate the target**, never as features

**Key design principles:**

- Process variability near specification limits
- Product- and line-specific behavior
- OOS events driven by combinations of process conditions

> ⚠️ Note: The dataset is **synthetically generated** but designed to reflect real manufacturing failure modes.

---

## 5. Stage 2 – Exploratory Data Analysis (EDA)

**Notebook:** `02_eda.ipynb`

EDA focused on **understanding process behavior**, not model building.

Key analyses:

- Distribution of process parameters
- OOS vs non-OOS comparisons
- Product-wise and line-wise OOS rates
- Early identification of **potential leakage risks**

📸 *Example (add your screenshot):*

```markdown
![EDA – OOS Distribution](images/eda_oos_distribution.png)
```

---

## 6. Stage 3 – ETL & Data Cleaning

**Notebook:** `03_etl_cleaning.ipynb`

Key actions:

- Merged batch logs, process parameters, and QC tables
- Handled missing values and data consistency issues
- Explicitly **removed identifiers and QC columns** from modeling features
- Created a clean modeling table

This step ensured **model-ready data without target leakage**.

---

## 7. Stage 4 – Feature Engineering

**Notebook:** `04_feature_engineering.ipynb`

Feature engineering was **domain-driven**, not generic.

### Feature types created:

- **Process parameters**

- Mixing speed, granulation temperature, moisture, coating spray rate
- **Near-spec indicators**

- `_near_low`, `_near_high` flags
- **Risk flags**

- `mixing_risk_flag`
- `granulation_risk_flag`
- `coating_risk_flag`
- **Variability features**

- Rolling standard deviations per line
- **Categorical encoding**

- Product, Line, Operator (one-hot encoded)

📸 *Example:*

```markdown
![Feature Engineering](images/feature_engineering.png)
```

---

## 8. Stage 5 – Baseline Modeling (Logistic Regression)

**Notebook:** `05_base_modeling.ipynb`

### Why Logistic Regression?

- Interpretable
- Stable
- Suitable for regulated environments
- Clear probability outputs

### Model setup:

- Standard scaling
- `class_weight="balanced"` to handle imbalance
- Stratified train-test split

---

## 9. Threshold Tuning (Critical Step)

Instead of optimizing accuracy, the model was tuned using **decision thresholds**.

### Why?

- Default threshold (0.5) is arbitrary
- Business goal: **minimize missed OOS batches**

### Thresholds tested:

`0.3 → 0.7`

### Final selected threshold:

**✅ 0.6**

---

## 10. Final Logistic Regression Results (Threshold = 0.6)

### Confusion Matrix

```
[[412  59]
 [ 18 111]]
```

### Classification Report

| Class       | Precision | Recall   | F1   |
| ----------- | --------- | -------- | ---- |
| 0 (In-Spec) | 0.96      | 0.87     | 0.91 |
| 1 (OOS)     | 0.65      | **0.86** | 0.74 |

**Accuracy:** 0.87

### Interpretation:

- **86% of OOS batches caught early**
- Significant reduction in high-risk misses
- False alarms are acceptable for operational review

---

## 11. Feature Importance – Logistic Regression

Top OOS risk drivers:

- Mixing risk flag
- Granulation risk flag
- Granulation moisture
- Granulation temperature near high
- Product-specific effects

📸 *Example:*

```markdown
![Logistic Regression Feature Importance](images/lr_feature_importance.png)
```

---

## 12. Alternative Model – Random Forest (Benchmark)

A Random Forest classifier was trained as a **non-linear benchmark**.

### Results

**Accuracy:** 0.985

**Confusion Matrix**

```
[[471   0]
 [  9 120]]
```

**OOS Recall:** 0.93
**OOS Precision:** 1.00

---

## 13. Model Comparison & Decision

Although Random Forest achieved very high test performance, the **magnitude of improvement** over Logistic Regression suggests it may be capturing dataset-specific patterns that may not generalize reliably in future manufacturing scenarios.

### Final Model Selected:

✅ **Logistic Regression with threshold = 0.6**

### Rationale:

- More realistic generalization
- Transparent decision logic
- Easier regulatory justification
- Controlled and explainable risk trade-offs

Random Forest is retained as a **benchmark**, not the deployed model.

---

## 14. SQL Usage (Supporting Analysis)

SQL was used for:

- Batch-level aggregations
- Product and line-wise OOS rates
- Feature extraction logic prior to modeling

Example:

```sql
SELECT
    product_id,
    line_id,
    COUNT(*) AS total_batches,
    SUM(oos_flag) AS oos_batches
FROM batch_log
GROUP BY product_id, line_id;
```

---

## 15. Key Business Takeaways

- Model acts as an **early warning system**
- Enables proactive investigation **before QC failure**
- Reduces:

- Batch rejection risk
- Investigation workload
- Compliance exposure

---

## 16. Application Deployment

The final Logistic Regression model is deployed via a **Streamlit web application**. The dashboard serves as a live inference simulator, allowing quality control teams to select historical batches, view real-time probability scores, and analyze core process parameters through interactive Plotly visualizations. 

---

## 17. Limitations & Future Work

- Synthetic dataset (real data would improve validation)
- Temporal validation can be added
- SHAP-based explainability
- Cost-based threshold optimization
- IoT Sensor Integration for live manufacturing feeds

---

## 18. Tech Stack

- Python
- Pandas, NumPy
- Scikit-learn
- Plotly
- Streamlit
- SQL
- Jupyter Notebook

---

## 19. Conclusion

This project demonstrates an **industry-grade ML workflow**:

- Strong data discipline
- Leakage-aware modeling
- Business-driven evaluation
- Thoughtful model selection

The focus is on **correct decisions**, not inflated metrics.