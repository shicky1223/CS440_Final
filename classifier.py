import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.linear_model import LogisticRegression

import joblib

df = pd.read_csv("anxiety_depression_data.csv")

df = df.dropna(subset=["Anxiety_Score"])

# defines function that maps GAD-7 scores into 4 anxiety categories
def get_anxiety_level(score):
    score = int(score)
    if score <= 4:
        return "minimal"
    elif score <= 9:
        return "mild"
    elif score <= 14:
        return "moderate"
    else:
        return "severe"

# new column is created, stores the axiety categories based on the scores
df["anxiety_level"] = df["Anxiety_Score"].apply(get_anxiety_level)

# select relevant numeric features from the columns in the dataset
features = [
    "Age", "Sleep_Hours", "Physical_Activity_Hrs", "Social_Support_Score",
    "Depression_Score", "Stress_Level", "Self_Esteem_Score",
    "Life_Satisfaction_Score", "Loneliness_Score"
]

# drop rows with any missing values in the features
df = df.dropna(subset=features)

# set the input features (X) and target label (y)
X = df[features]
y = df["anxiety_level"]

# split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# initialize and train the logistic regression model
model = LogisticRegression(max_iter=1000)  # increase max_iter for convergence
model.fit(X_train, y_train)

joblib.dump(model, "anxiety_classifier.pkl")
