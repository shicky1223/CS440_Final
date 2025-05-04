import spacy
import re
import contractions
from collections import defaultdict
from word2number import w2n

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

    # --- Age Extraction (digits via NER requiring context) ---
    for ent in doc.ents:
        if ent.label_ in {"DATE", "CARDINAL"}:
            if any(word in ent.text.lower() for word in ["year", "old", "age"]):
                try:
                    possible_age = int([int(s) for s in ent.text.split() if s.isdigit()][0])
                    if 5 < possible_age < 100:
                        features["Age"] = possible_age
                        confidence_scores["Age"] = 0.9
                except Exception:
                    pass
    # --- Fallback: 'I am/I'm <word age> years old' spelled-out ---
    if features["Age"] is None:
        m = re.search(r"(?:i am|i'm)\s+([a-z\s-]+?)\s*(?:years?|yrs?)\s*old", text.lower())
        if m:
            try:
                features["Age"] = int(w2n.word_to_num(m.group(1)))
                confidence_scores["Age"] = 0.7
            except Exception:
                pass
    # --- Fallback: '<digits> years old' pattern ---
    if features["Age"] is None:
        m2 = re.search(r"(\d{1,3})\s*(?:years?|yrs?)\s*old", text.lower())
        if m2 and m2.group(1).isdigit():
            features["Age"] = int(m2.group(1))
            confidence_scores["Age"] = 0.8
    # --- Fallback: bare "I'm <digit>" ---
    if features["Age"] is None:
        m3 = re.search(r"(?:i am|i'm)\s+(\d{1,3})(?=\s|,|\.|$)", text.lower())
        if m3 and m3.group(1).isdigit():
            features["Age"] = int(m3.group(1))
            confidence_scores["Age"] = 0.6

    # --- Sleep Extraction ---
    sleep_patterns = [
        r"(?:sleep|get)\s+(?:about\s+)?(\d{1,2})\s*(?:hours|hrs)?",
        r"(\d{1,2})\s*(?:hours|hrs)\s*(?:of)?\s*(?:sleep|rest)"
    ]
    for pattern in sleep_patterns:
        sleep_match = re.search(pattern, text.lower())
        if sleep_match:
            hours = next((g for g in sleep_match.groups() if g and g.isdigit()), None)
            if hours:
                features["Sleep_Hours"] = float(hours)
                confidence_scores["Sleep_Hours"] = 0.8
                break
    # --- Fallback: sleep spelled-out ---
    if features["Sleep_Hours"] is None:
        m = re.search(r"(?:sleep|get)\s+([a-z\s-]+?)\s*(?:hours|hrs)", text.lower())
        if m:
            try:
                hrs = w2n.word_to_num(m.group(1))
                features["Sleep_Hours"] = float(hrs)
                confidence_scores["Sleep_Hours"] = 0.7
            except Exception:
                pass

    # --- Exercise Extraction ---
    exercise_patterns = [
        r"(\d{1,2})\s*(?:hours|hrs)\s*(?:of)?\s*(?:exercise|gym|workout)",
        r"\b(?:jog|run|gym|exercise|workout|hike)\b"
    ]
    exercise_matches = [m for pat in exercise_patterns for m in re.finditer(pat, text.lower())]
    if exercise_matches:
        total = 0
        for m in exercise_matches:
            num = m.group(1) if m.lastindex and m.group(1) else None
            total += int(num) if num and num.isdigit() else 1
        features["Physical_Activity_Hrs"] = total
        confidence_scores["Physical_Activity_Hrs"] = 0.8

    # --- Stress Extraction ---
    stress_keywords = {"overwhelmed", "anxious", "stressed", "burned out", "tense", "worried"}
    if any(token.lemma_.lower() in stress_keywords for token in doc if token.pos_ == "ADJ"):
        features["Stress_Level"] = "High"
        confidence_scores["Stress_Level"] = 0.9

    # --- Social Support Extraction ---
    social_phrases = {
        "High": ["a lot of support", "always there", "can count on"],
        "Medium": ["some support", "sometimes help", "occasionally talk"],
        "Low": ["no one", "isolated", "alone"]
    }
    for level, triggers in social_phrases.items():
        if any(trig in text.lower() for trig in triggers):
            features["Social_Support_Score"] = level
            confidence_scores["Social_Support_Score"] = 0.8
            break

    # --- Depression Extraction ---
    depression_keywords = {"sad", "hopeless", "worthless", "numb", "empty", "unmotivated"}
    depression_hits = sum(1 for token in doc if token.lemma_.lower() in depression_keywords)
    features["Depression_Score"] = min(21, depression_hits)
    confidence_scores["Depression_Score"] = 0.8

    # --- Self-Esteem Extraction ---
    self_esteem_phrases = {
        "Low": ["i hate myself", "i'm worthless", "i feel ashamed"],
        "Medium": ["i am okay", "i feel fine", "i feel neutral"],
        "High": ["i like myself", "i'm proud", "i feel confident"]
    }
    for level, phrases in self_esteem_phrases.items():
        if any(p in text.lower() for p in phrases):
            features["Self_Esteem_Score"] = level
            confidence_scores["Self_Esteem_Score"] = 0.7
            break

    # --- Life Satisfaction Extraction ---
    satisfaction_phrases = {
        "High": ["i love my life", "very satisfied", "things are great"],
        "Medium": ["life is okay", "can't complain", "so-so"],
        "Low": ["i hate my life", "not satisfied", "everything is bad"]
    }
    for level, phrases in satisfaction_phrases.items():
        if any(p in text.lower() for p in phrases):
            features["Life_Satisfaction_Score"] = level
            confidence_scores["Life_Satisfaction_Score"] = 0.8
            break

    # --- Loneliness Extraction ---
    loneliness_terms = {"alone", "isolated", "nobody", "no one", "lonely"}
    loneliness_hits = sum(1 for token in doc if token.lemma_.lower() in loneliness_terms)
    features["Loneliness_Score"] = min(3, loneliness_hits)
    confidence_scores["Loneliness_Score"] = 0.7

    # Normalize values
    if features.get("Age"):
        features["Age"] = min(features["Age"], 100)
    if features.get("Sleep_Hours"):
        features["Sleep_Hours"] = min(features["Sleep_Hours"], 24)
    if features.get("Physical_Activity_Hrs"):
        features["Physical_Activity_Hrs"] = min(features["Physical_Activity_Hrs"], 24)

    # Convert qualitative to numeric
    features["Stress_Level"] = map_level(features.get("Stress_Level"))
    features["Social_Support_Score"] = map_level(features.get("Social_Support_Score"))
    features["Self_Esteem_Score"] = map_level(features.get("Self_Esteem_Score"))
    features["Life_Satisfaction_Score"] = map_level(features.get("Life_Satisfaction_Score"))

    return dict(features), dict(confidence_scores)



if __name__ == "__main__":
    tests = [
        "I am 21 years old, sleep 7 hours, workout 5 hours, feel anxious, have a lot of support, sometimes sad, I love my life, but feel lonely sometimes.",
        "I'm thirty, sleep six hrs, run, feel overwhelmed, no one to talk to, life is okay."
    ]
    for t in tests:
        feats, conf = extract_features_spacy(t)
        print("Text:", t)
        print("Features:", feats)
        print("Confidence:", conf)
        print("-"*40)
