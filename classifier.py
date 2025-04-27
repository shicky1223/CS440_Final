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

def classify_user(features: dict) -> str:
    row = {col: features.get(col, 0) for col in FEATURE_ORDER}
    df_user = pd.DataFrame([row], columns=FEATURE_ORDER)
    return _model.predict(df_user)[0]


# allow standalone training
if __name__ == "__main__":
    train_and_dump()
    print("Model trained and saved to", MODEL_PATH)
