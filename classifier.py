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

# new column is created, stores the anxiety categories based on the scores
df["anxiety_level"] = df["Anxiety_Score"].apply(get_anxiety_level)

# selects relevant numeric features from the columns in the dataset
features = [
    "Age", "Sleep_Hours", "Physical_Activity_Hrs", "Social_Support_Score",
    "Depression_Score", "Stress_Level", "Self_Esteem_Score",
    "Life_Satisfaction_Score", "Loneliness_Score"
]

# drops any rows with any missing values in the features
df = df.dropna(subset=features)

# sets the input features (X) and target label (y)
X = df[features]
y = df["anxiety_level"]

# splits into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# initializes and trains the logistic regression model
model = LogisticRegression(max_iter=1000)  # if needed, increase max_iter for convergence
model.fit(X_train, y_train)

joblib.dump(model, "anxiety_classifier.pkl")


# loads the model for prediction
def predict_anxiety_level(user_data: dict) -> str:

    # format of the dictionary that should be passed into this function:
    # this is just an example
    """
    user_data = {
    "Age": 20,
    "Sleep_Hours": 6.5,
    "Physical_Activity_Hrs": 2,
    "Social_Support_Score": 7,
    "Depression_Score": 4,
    "Stress_Level": 6,
    "Self_Esteem_Score": 5,
    "Life_Satisfaction_Score": 6,
    "Loneliness_Score": 3
}
    """
    df = pd.DataFrame([user_data])  # wraps in list to make single-row DataFrame
    prediction = model.predict(df)
    return prediction[0]
