from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


from data_access import load_features

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
MODELS_DIR.mkdir(parents = True, exist_ok = True)
REPORTS_DIR.mkdir(parents = True, exist_ok =  True)

FEATURE_COLUMNS = [
    "default_next_month",
    "limit_bal",
    "age",
    "sex", "education", "marriage",
    "pay_0",
    "utilization_ratio",
    "payment_ratio", "payment_ratio_missing",
    "avg_bill_3m", "avg_pay_3m", "net_bill_minus_pay_3m",
    "n_months_late_6m",
    "max_late_6m"

]

CAT_COLS = ["sex", "education", "marriage"]

def build_pipeline(num_cols: list[str], cat_cols: list[str]) -> Pipeline:
    preprocess = ColumnTransformer(
        transformers=[
            ("num", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]), num_cols),
            ("cat", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ]), cat_cols),
        ],
        remainder="drop",
    )

    clf = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
    )

    return Pipeline(steps=[
        ("prep", preprocess),
        ("clf", clf),
    ])
def threshold_sweep(y_true: np.ndarray, proba: np.ndarray, thresholds: list[float]) -> pd.DataFrame:
    rows = []
    for t in thresholds:
        pred = (proba >= t).astype(int)
        rows.append({
            "threshold": t,
            "precision": float(precision_score(y_true, pred, zero_division=0)),
            "recall": float(recall_score(y_true, pred, zero_division = 0)),
            "flag_rate": float(pred.mean())  # fraction predicted as 1
        })

    return pd.DataFrame(rows)
    
    
    
def extract_coefficients(pipe: Pipeline, num_cols: list[str], cat_cols: list[str]) -> pd.DataFrame:  
    prep: ColumnTransformer = pipe.named_steps["prep"]
    clf: LogisticRegression = pipe.named_steps["clf"]

    "numeric features names"
    features_names = list(num_cols)

    "categorical expanded names"
    ohe: OneHotEncoder = prep.named_transformers_["cat"].named_steps["onehot"]
    cat_names = list(ohe.get_feature_names_out(cat_cols))
    features_names.extend(cat_names)

    coefs = clf.coef_.ravel()
    out = pd.DataFrame({"feature": features_names, "coef": coefs})
    out["abs_coef"] = out["coef"].abs()
    return out.sort_values("abs_coef", ascending = False).drop(columns=["abs_coef"])

def main() -> None:
    df = load_features(FEATURE_COLUMNS)

    # Split
    X = df.drop(columns = ["default_next_month"])
    y = df["default_next_month"].astype(int).to_numpy()
    
    num_cols = [c for c in X.columns if c not in CAT_COLS]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size = 0.25,
        random_state = 42,
        stratify = y
    )

    pipe = build_pipeline(num_cols = num_cols, cat_cols = CAT_COLS)
    pipe.fit(X_train, y_train)

    proba = pipe.predict_proba(X_test)[:, 1]

    # Core metrics (threshold free)
    roc = float(roc_auc_score(y_test, proba))
    pr = float(average_precision_score(y_test, proba))

    # Policy threshold evaluation
    THRESHOLD = 0.4 #default choice
    pred = (proba >= THRESHOLD).astype(int)
    cm = confusion_matrix(y_test, pred).tolist()
    report = classification_report(y_test, pred, digits = 3, output_dict = True)

    metrics = {
        "model" : "logistic_regression",
        "threshold": THRESHOLD,
        "roc_auc": roc,
        "pr_auc": pr,
        "confusion_matrix": cm,
        "classification_report": report,
    }

    #save artifacts
    dump(pipe, MODELS_DIR / "logreg_pipeline.joblib")

    with open(REPORTS_DIR / "metrics_logreg.json", "w", encoding = "utf-8") as f:
        json.dump(metrics, f, indent = 2)

    sweep = threshold_sweep(y_test, proba, thresholds = [0.2,0.3,0.4,0.5,0.6,0.7])
    sweep.to_csv(REPORTS_DIR / "thresholds_sweep.csv", index = False)

    coef_df = extract_coefficients(pipe, num_cols = num_cols, cat_cols =  CAT_COLS)
    coef_df.to_csv(REPORTS_DIR / "coefficients.csv", index = False)

    #console summary (quick feedback)
    print("Saved model: ", MODELS_DIR / "logreg_pipeline.joblib")
    print("ROC AUC: ", roc)
    print("PR AUC: ", pr)
    print("Threshold: ", THRESHOLD)
    print("Confusion matrix: ", cm)
    print('Top coefficients: ')
    print(coef_df.head(12).to_string(index = False))

if __name__ == "__main__":
    main()



