# classifier.py

import os, pandas as pd, joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

MODEL_PATH = "anxiety_classifier.pkl"
CSV_PATH   = "anxiety_depression_data.csv"
FEATURE_ORDER = [
    "Age", "Sleep_Hours", "Physical_Activity_Hrs",
    "Social_Support_Score", "Depression_Score",
    "Stress_Level", "Self_Esteem_Score",
    "Life_Satisfaction_Score", "Loneliness_Score"
]
def get_anxiety_level(score):
    score = int(score)
    if score <= 4:  return "minimal"
    if score <= 9:  return "mild"
    if score <= 14: return "moderate"
    return "severe"

def train_and_dump():
    df = pd.read_csv(CSV_PATH)
    df["anxiety_level"] = df["Anxiety_Score"].apply(get_anxiety_level)

    features = [
      "Age", "Sleep_Hours", "Physical_Activity_Hrs",
      "Social_Support_Score", "Depression_Score",
      "Stress_Level", "Self_Esteem_Score",
      "Life_Satisfaction_Score", "Loneliness_Score"
    ]
    df = df.dropna(subset=features + ["anxiety_level"])

    X = df[features]
    y = df["anxiety_level"]
    X_train, X_test, y_train, y_test = train_test_split(
      X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH)
    return model

# load or train once at import time
if os.path.exists(MODEL_PATH):
    _model = joblib.load(MODEL_PATH)
else:
    _model = train_and_dump()

import pandas as pd

def classify_user(features: dict) -> str:
    # Build a clean row with exactly the nine model features,
    # coercing to float (and defaulting invalid/missing to 0.0)
    row = {}
    for col in FEATURE_ORDER:
        val = features.get(col, 0)
        try:
            row[col] = float(val)
        except Exception:
            row[col] = 0.0

    df_user = pd.DataFrame([row], columns=FEATURE_ORDER)

    # debug log: drop this once it works
    print("-- df_user dtypes --\n", df_user.dtypes)
    print("-- df_user head --\n", df_user)

    return _model.predict(df_user)[0]



# allow standalone training
if __name__ == "__main__":
    train_and_dump()
    print("Model trained and saved to", MODEL_PATH)
