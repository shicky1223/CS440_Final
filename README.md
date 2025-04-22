# CS440_Final
CS 440 Final Project

- Model used currently: meta-llama/Llama-3.2-1B-Instruct
- We are still experimenting with models from HuggingFace 
- using sqlite for now --> may switch to hosted service later


## Setup

```bash
git clone git@github.com:shicky1223/CS440_Final.git # using SSH key 
cd CS440_Final
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in your HF_TOKEN --> ask me for the HF_TOKEN or use your own and secret key
