import spacy
import re

nlp = spacy.load("en_core_web_sm")

def extract_features(text: str) -> dict:
    #doc = nlp(text)
    features = {}

    # Age
    age_match = re.search(r"\b(i'?m|i am|my age is)\s+(\d{1,2})\b", text, flags=re.IGNORECASE)
    if age_match:
        features["Age"] = int(age_match.group(2))

    # Sleep
    sleep_match = re.search(r"sleep.*?(\d{1,2})(\.\d+)?\s*(hours|hrs)", text, flags=re.IGNORECASE)
    if sleep_match:
        features["Sleep_Hours"] = float(sleep_match.group(1) + (sleep_match.group(2) or ""))

    # Physical Activity
    physical_activity_match = re.search(r"(exercise|workout|gym).*(\d+)(\.\d+)?\s*(hours|hrs)", text, flags=re.IGNORECASE)
    if physical_activity_match:
        features["Physical_Activity_Hrs"] = float(physical_activity_match.group(2) + (physical_activity_match.group(3) or ""))

    # Social Support
    social_match = re.search(r"(social.*?support|friends|family)\s*score.*?(\d+)(\.\d+)?", text, flags=re.IGNORECASE)
    if social_match:
        features["Social_Support_Score"] = float(social_match.group(2) + (social_match.group(3) or ""))

    # Depression
    depression_match = re.search(r"(depression|sadness|mood|sad|depressed|down)\s*score.*?(\d+)(\.\d+)?", text, flags=re.IGNORECASE)
    if depression_match:
        features["Depression_Score"] = float(depression_match.group(2) + (depression_match.group(3) or ""))

    # Stress
    stress_match = re.search(r"(stress|anxiety|pressure)\s*score.*?(\d+)(\.\d+)?", text, flags=re.IGNORECASE)
    if stress_match:
        features["Stress_Level"] = float(stress_match.group(2) + (stress_match.group(3) or ""))

    # Self-Esteem
    self_esteem_match = re.search(r"(self-esteem|confidence|confident)\s*score.*?(\d+)(\.\d+)?", text, flags=re.IGNORECASE)
    if self_esteem_match:
        features["Self_Esteem_Score"] = float(self_esteem_match.group(2) + (self_esteem_match.group(3) or ""))

    # Life Satisfaction
    life_satisfaction_match = re.search(r"(life satisfaction|happiness|happy)\s*score.*?(\d+)(\.\d+)?", text, flags=re.IGNORECASE)
    if life_satisfaction_match:
        features["Life_Satisfaction_Score"] = float(life_satisfaction_match.group(2) + (life_satisfaction_match.group(3) or ""))

    # Loneliness
    loneliness_match = re.search(r"(loneliness|lonely|alone)\s*score.*?(\d+)(\.\d+)?", text, flags=re.IGNORECASE)
    if loneliness_match:
        features["Loneliness_Score"] = float(loneliness_match.group(2) + (loneliness_match.group(3) or ""))

    return features
