import spacy

nlp = spacy.load("en_core_web_sm")

def extract_features_spacy(text):
    doc = nlp(text)

    age = None
    sleep_hours = None
    exercise_freq = None
    stress_level = None
    social_support = None
    depression_score = None
    self_esteem_score = None
    life_satisfaction_score = None
    loneliness_score = None

    # using name entity recognition to extract age
    for ent in doc.ents:
        if ent.label_ in {"DATE", "AGE", "CARDINAL"}:
            if any(word in ent.text.lower() for word in ["year", "old", "age"]):
                try:
                    possible_age = int([int(s) for s in ent.text.split() if s.isdigit()][0])
                    if 5 < possible_age < 100:
                        age = possible_age
                except:
                    pass

    # using dependency parsing to extract sleep hours
    for token in doc:
        if token.lemma_ in ["sleep", "rest"]:
            for child in token.children:
                if child.like_num:
                    try:
                        sleep_hours = float(child.text)
                    except:
                        pass

    # using dependency parsing to extract stress level (adjectives)
    stress_words = {"overwhelmed", "anxious", "stressed", "burned out", "tense", "worried"}
    for token in doc:
        if token.pos_ == "ADJ" and token.lemma_.lower() in stress_words:
            stress_level = "High"
            break

    # using dependency parsing to extract exercise frequency (verbs and modifiers)
    for sent in doc.sents:
        if any(word in sent.text.lower() for word in ["jog", "run", "gym", "exercise", "workout"]):
            if any(freq in sent.text.lower() for freq in ["daily", "every", "often", "regularly", "weekly"]):
                exercise_freq = "Frequent"
            else:
                exercise_freq = "Rare"

    # using keywords to extract social support
    social_keywords = {"friends", "family", "support", "talk to", "trusted", "close to"}
    if any(word in text.lower() for word in social_keywords):
        if any(phrase in text.lower() for phrase in ["a lot of support", "always there", "can count on"]):
            social_support = "High"
        elif any(phrase in text.lower() for phrase in ["some support", "sometimes help", "occasionally talk"]):
            social_support = "Medium"
        else:
            social_support = "Low"

    # using keywords to extract depression score (adjectives)
    depression_keywords = {"sad", "hopeless", "worthless", "numb", "empty", "unmotivated"}
    depression_hits = sum(1 for token in doc if token.lemma_.lower() in depression_keywords)
    depression_score = min(3, depression_hits)  # simplistic scale 0–3

    # using keywords to extract self-esteem score (pronouns and adjectives)
    if "i hate myself" in text.lower() or "i'm worthless" in text.lower():
        self_esteem_score = "Low"
    elif "i like myself" in text.lower() or "i'm proud" in text.lower():
        self_esteem_score = "High"
    else:
        self_esteem_score = "Medium"

    # using keywords to extract life satisfaction score (tone)
    satisfaction_phrases = {
        "high": ["i love my life", "very satisfied", "things are great"],
        "medium": ["life is okay", "can't complain", "so-so"],
        "low": ["i hate my life", "not satisfied", "everything is bad"]
    }
    for k, phrases in satisfaction_phrases.items():
        if any(phrase in text.lower() for phrase in phrases):
            life_satisfaction_score = k.capitalize()

    # using keywords to extract loneliness score (social isolation terms)
    loneliness_terms = {"alone", "isolated", "nobody", "no one", "lonely"}
    loneliness_hits = sum(1 for token in doc if token.lemma_.lower() in loneliness_terms)
    loneliness_score = min(3, loneliness_hits)  # assigns a numerical value for how lonely the user feels (0-3)

    features = {
        "Age": age,
        "Sleep_Hours": sleep_hours,
        "Exercise": exercise_freq,
        "Stress_Level": stress_level,
        "Social_Support_Score": social_support,
        "Depression_Score": depression_score,
        "Self_Esteem_Score": self_esteem_score,
        "Life_Satisfaction_Score": life_satisfaction_score,
        "Loneliness_Score": loneliness_score
    }

    return features