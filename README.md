TL;DR: Built an end-to-end credit risk pipeline (SQL + Python) that prioritizes interpretability and policy-driven threshold selection over raw metric optimization.

Credit Risk Prediction — End-to-End Project
Overview

This project builds an end-to-end credit risk pipeline, from raw data ingestion to feature engineering, exploratory analysis, and interpretable modeling.

The goal is not to maximize a metric at all costs, but to demonstrate reasonable, defensible modeling choices under realistic constraints — similar to how credit risk is handled in practice.

The final model estimates the probability that a client will default on their credit card payment next month and evaluates different decision thresholds based on policy tradeoffs.

Dataset

Source: UCI Machine Learning Repository
Default of Credit Card Clients Dataset

Size: ~30,000 clients

Target:

default_next_month (1 = default, 0 = no default)

The raw data is ingested from Excel, cleaned, and stored locally in DuckDB for reproducible querying.

Project Structure
credit-risk-prediction/

│
├── sql/
# Clean & semantic client view
│   ├── 01_create_v_clients.sql 

# Feature engineering layer
│   ├── 02_create_v_features.sql 

# Data validation & sanity checks
│   └── 03_diagnostics.sql           
│

├── src/

# Excel → Parquet conversion 
├── convert_xls.py 
# DuckDB database creation
│   ├── make_duckdb.py 
# Data loading utilities
│   ├── data_access.py 
# Reproducible model training script
│   └── train_logreg.py 
│

├── notebooks/

# Exploratory analysis
│   ├── 01_eda_risk_signals.ipynb 
# Model comparison & threshold analysis
│   └── model_baselines.ipynb         
│
# (ignored) trained models
├── models/       
# (ignored) metrics & artifacts
├── reports/     


└── README.md


SQL Feature Pipeline

Feature engineering is handled entirely in SQL using DuckDB views, following a layered approach:

raw_default_clients
Physical table loaded from Parquet.

v_clients

Renames raw columns (X1 → limit_bal, etc.)

Removes the duplicated header row

Defines clean, typed client records

v_features

Encodes recent delinquency (pay_0)

Aggregates delinquency history (e.g. n_months_late_6m)

Computes utilization and payment behavior ratios

Produces a stable, modeling-ready feature table

This separation makes the pipeline:

reproducible

debuggable

easy to extend without breaking downstream code

Exploratory Data Analysis

EDA focuses on risk signals, not just distributions.

Key findings:

Recent delinquency (pay_0) is the strongest single predictor

Persistent delinquency over time is more informative than isolated events

High utilization and low payment ratios are associated with higher default risk

Default risk increases monotonically with late-payment severity

These insights directly informed feature selection and modeling decisions.

Modeling Approach

Two baseline models were evaluated:

Logistic Regression

Decision Tree

Both models achieved similar ranking performance (ROC AUC ≈ 0.74–0.77).

Final Choice: Logistic Regression

Logistic regression was selected because:

Performance was comparable to the decision tree

Coefficients are interpretable and stable

The model aligns better with explainability requirements common in credit risk

Threshold Selection & Policy Tradeoff

Rather than relying on a fixed 0.5 cutoff, the project evaluates decision thresholds explicitly.

Chosen threshold: 0.4

Rationale:

Increases recall of defaulters by ~9 percentage points

Accepts more false positives to reduce missed defaults

Reflects a risk-averse lending policy where defaults are more costly than customer inconvenience

This emphasizes that modeling decisions are policy decisions, not purely technical ones.

Results (Logistic Regression @ threshold = 0.4)

ROC AUC: ~0.74

PR AUC: ~0.51

Recall (defaulters): ~72%

Precision (defaulters): ~36%

At the selected threshold, the model captures ~72% of defaulters while accepting a higher false-positive rate, reflecting a risk-averse lending strategy.

The model is not perfect — and is not presented as such — but it provides a reasonable and explainable risk ranking suitable for decision support.

Reproducibility

After setting up the DuckDB database and SQL views, the full training pipeline can be reproduced with:

python src/train_logreg.py


This script:

Loads features from v_features

Trains the logistic regression model

Evaluates performance at the chosen threshold

Exports metrics and coefficients (ignored by Git)

Key Takeaways

Feature engineering matters more than model complexity

Threshold choice often matters more than algorithm choice

Interpretability and policy alignment are central in credit risk

SQL + Python separation leads to cleaner, more maintainable pipelines

Possible Extensions

Cost-sensitive optimization using expected loss

Time-based validation split

Monitoring population drift

Comparison with regularized or ensemble models

Final note

This project is intentionally focused on clarity, structure, and reasoning, rather than chasing marginal metric improvements.
