import spacy
import re
import contractions
from collections import defaultdict

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Function to map text-based features to numeric scores
def map_level(value):
    """Maps qualitative levels to numeric values."""
    if value == "Low": return 1
    if value == "Medium": return 2
    if value == "High": return 3
    return 0  # fallback

def extract_features_spacy(text):
    # Expand contractions
    text = contractions.fix(text)

    # Initialize variables
    features = defaultdict(lambda: None)
    confidence_scores = defaultdict(lambda: 0.0)

    # Create a SpaCy document
    doc = nlp(text)

    # --- Age Extraction ---
    for ent in doc.ents:
        if ent.label_ in {"DATE", "AGE", "CARDINAL"}:
            if any(word in ent.text.lower() for word in ["year", "old", "age"]):
                try:
                    possible_age = int([int(s) for s in ent.text.split() if s.isdigit()][0])
                    if 5 < possible_age < 100:
                        features["Age"] = possible_age
                        confidence_scores["Age"] = 0.9  # High confidence
                except:
                    pass

    # --- Sleep Extraction ---
    sleep_patterns = [r"(sleep|get)\s+(about\s+)?(\d{1,2})\s*(hours|hrs)?", 
                      r"(\d{1,2})\s*(hours|hrs)\s*(of)?\s*(sleep|rest)"]
    for pattern in sleep_patterns:
        sleep_match = re.search(pattern, text.lower())
        if sleep_match:
            features["Sleep_Hours"] = float(sleep_match.group(3))
            confidence_scores["Sleep_Hours"] = 0.8  # Medium confidence

    # --- Exercise Extraction ---
    exercise_patterns = [r"(\d+)\s*(hours|hrs)\s*(of)?\s*(exercise|gym|workout)", 
                         r"(jog|run|gym|exercise|workout|hike)"]
    exercise_matches = []
    for pattern in exercise_patterns:
        exercise_match = re.search(pattern, text.lower())
        if exercise_match:
            exercise_matches.append(exercise_match)
    
    if exercise_matches:
        features["Physical_Activity_Hrs"] = sum([int(match.group(1)) for match in exercise_matches])
        confidence_scores["Physical_Activity_Hrs"] = 0.8  # Medium confidence

    # --- Stress Extraction ---
    stress_keywords = {"overwhelmed", "anxious", "stressed", "burned out", "tense", "worried"}
    stress_hits = [token for token in doc if token.pos_ == "ADJ" and token.lemma_.lower() in stress_keywords]
    if stress_hits:
        features["Stress_Level"] = "High"
        confidence_scores["Stress_Level"] = 0.9  # High confidence

    # --- Social Support Extraction ---
    social_keywords = {"friends", "family", "support", "talk to", "trusted", "close to"}
    social_phrases = {
        "High": ["a lot of support", "always there", "can count on"],
        "Medium": ["some support", "sometimes help", "occasionally talk"],
        "Low": ["no one", "isolated", "alone"]
    }
    for phrase, levels in social_phrases.items():
        if any(phrase in text.lower() for phrase in levels):
            features["Social_Support_Score"] = phrase
            confidence_scores["Social_Support_Score"] = 0.8  # Medium confidence

    # --- Depression Extraction ---
    depression_keywords = {"sad", "hopeless", "worthless", "numb", "empty", "unmotivated"}
    depression_hits = sum(1 for token in doc if token.lemma_.lower() in depression_keywords)
    features["Depression_Score"] = min(3, depression_hits)  # Numerical scale
    confidence_scores["Depression_Score"] = 0.8  # Medium confidence

    # --- Self-Esteem Extraction ---
    self_esteem_phrases = {"Low": ["i hate myself", "i'm worthless"],
                           "High": ["i like myself", "i'm proud"],
                           "Medium": []}
    for level, phrases in self_esteem_phrases.items():
        if any(phrase in text.lower() for phrase in phrases):
            features["Self_Esteem_Score"] = level
            confidence_scores["Self_Esteem_Score"] = 0.7  # Medium confidence

    # --- Life Satisfaction Extraction ---
    satisfaction_phrases = {
        "High": ["i love my life", "very satisfied", "things are great"],
        "Medium": ["life is okay", "can't complain", "so-so"],
        "Low": ["i hate my life", "not satisfied", "everything is bad"]
    }
    for level, phrases in satisfaction_phrases.items():
        if any(phrase in text.lower() for phrase in phrases):
            features["Life_Satisfaction_Score"] = level
            confidence_scores["Life_Satisfaction_Score"] = 0.8  # Medium confidence

    # --- Loneliness Extraction ---
    loneliness_terms = {"alone", "isolated", "nobody", "no one", "lonely"}
    loneliness_hits = sum(1 for token in doc if token.lemma_.lower() in loneliness_terms)
    features["Loneliness_Score"] = min(3, loneliness_hits)  # Numerical scale
    confidence_scores["Loneliness_Score"] = 0.7  # Medium confidence

    # Normalize values where necessary
    if features["Age"]:
        features["Age"] = min(features["Age"], 100)  # Cap age to 100
    if features["Sleep_Hours"]:
        features["Sleep_Hours"] = min(features["Sleep_Hours"], 24)  # Max 24 hours for sleep
    if features["Physical_Activity_Hrs"]:
        features["Physical_Activity_Hrs"] = min(features["Physical_Activity_Hrs"], 24)  # Max 24 hours of activity

    # Convert qualitative scores to numerical scores for easier processing later
    features["Stress_Level"] = map_level(features["Stress_Level"])
    features["Social_Support_Score"] = map_level(features["Social_Support_Score"])
    features["Self_Esteem_Score"] = map_level(features["Self_Esteem_Score"])
    features["Life_Satisfaction_Score"] = map_level(features["Life_Satisfaction_Score"])

    return dict(features), dict(confidence_scores)

