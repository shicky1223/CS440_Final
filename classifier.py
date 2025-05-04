import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

MODEL_PATH = "anxiety_classifier.pkl"
CSV_PATH = "anxiety_depression_data.csv"
FEATURE_ORDER = [
    "Age", "Sleep_Hours", "Physical_Activity_Hrs",
    "Social_Support_Score", "Depression_Score",
    "Stress_Level", "Self_Esteem_Score",
    "Life_Satisfaction_Score", "Loneliness_Score"
]
persistent_features = { col: 0.0 for col in FEATURE_ORDER }

def get_anxiety_level(score):
    score = int(score)
    if score <= 4:  
        return "minimal"
    if score <= 9:  
        return "mild"
    if score <= 14: 
        return "moderate"
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

# Load or train once at import time
if os.path.exists(MODEL_PATH):
    _model = joblib.load(MODEL_PATH)
else:
    _model = train_and_dump()

import pandas as pd

def classify_user(features_tuple: tuple) -> str:
    global persistent_features
    new_feats, confidence_scores = features_tuple

    # only overwrite keys the user _actually_ mentioned:
    for col, val in new_feats.items():
        try:
            persistent_features[col] = float(val)
        except Exception:
            # non-numeric or missing → leave the old value
            pass

    # now build your DF from the merged state:
    df_user = pd.DataFrame([persistent_features], columns=FEATURE_ORDER)

    # debug
    print("-- df_user dtypes --\n", df_user.dtypes)
    print("-- df_user head --\n", df_user)

    return _model.predict(df_user)[0]

# Allow standalone training
if __name__ == "__main__":
    train_and_dump()
    print("Model trained and saved to", MODEL_PATH)
