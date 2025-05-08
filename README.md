# CS440_Final  
CS 440 Final Project

This Flask web application combines a logistic regression–based anxiety classifier with a Llama-3.2-1B-Instruct conversational agent to provide personalized mental health check-ins. Users can register, complete a brief wellness questionnaire, receive an anxiety level assessment, and chat with a therapeutic assistant model.

## Features

- User authentication and management (Flask-Login & Flask-Bcrypt)  
- Questionnaire-driven data collection (Age, Sleep, Exercise, Stress, etc.)  
- Feature extraction using spaCy  
- Anxiety level classification via scikit-learn LogisticRegression  
- Conversational AI responses powered by meta-llama/Llama-3.2-1B-Instruct  
- Data persistence with SQLAlchemy (SQLite by default)  

## Setup

```bash
git clone git@github.com:shicky1223/CS440_Final.git
cd CS440_Final
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # create your own .env file


This project uses python-dotenv to load sensitive values. In your project root, edit .env to include:
# Hugging Face API token for loading the language model
HF_TOKEN=your_huggingface_token_here

# Flask secret key for securing sessions and flash messages
SECRET_KEY=your_flask_secret_key_here

# (Optional) Database connection URL; defaults to SQLite if unset
DATABASE_URL=your_database_url_here
