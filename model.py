import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from dotenv import load_dotenv  

# Load environment variables from .env if present
load_dotenv()

# Retrieve your Hugging Face key from the environment
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise ValueError("Please set your HF_TOKEN environment variable.")

MODEL_NAME = "EleutherAI/gpt-neo-2.7B"
print(f"Loading model '{MODEL_NAME}'...")

# Load the tokenizer and model, dynamically passing your token.
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=hf_token)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,  # Use float16 for GPU acceleration; change to float32 if on CPU.
    device_map="auto",
    use_auth_token=hf_token
)
print("Model loaded successfully.")


def generate_response(prompt: str, 
                      max_new_tokens: int = 150, 
                      temperature: float = 0.7, 
                      top_p: float = 0.95) -> str:
    """
    Generate a response from the model given an input prompt.
    """
    # Tokenize the prompt and move inputs to the model's device.
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate response tokens.
    output = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=temperature,
        top_p=top_p,
        no_repeat_ngram_size=2  # Prevent repetitive generation.
    )
    
    # Decode and return the generated text.
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response


if __name__ == '__main__':
    # Test the setup with a simple prompt.
    sample_prompt = "Hello, who are you?"
    print("Prompt:", sample_prompt)
    result = generate_response(sample_prompt)
    print("Response:", result)
