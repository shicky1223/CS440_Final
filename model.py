#model
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "EleutherAI/gpt-neo-2.7B"

print(f"Loading model '{MODEL_NAME}'...")
# Load the tokenizer and model.
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32,  # Use float16 for GPU acceleration; change to float32 if on CPU.
    device_map="auto"           # Automatically assign model layers to available devices.
)
print("Model loaded successfully.")


def generate_response(prompt: str, 
                      max_new_tokens: int = 150, 
                      temperature: float = 0.7, 
                      top_p: float = 0.95) -> str:
    """
    Generate a response from the Llama-2 chat model given an input prompt.

    Args:
        prompt (str): The user-provided input prompt.
        max_new_tokens (int): Maximum number of tokens to generate.
        temperature (float): Controls randomness in the generation process.
        top_p (float): Nucleus sampling parameter.

    Returns:
        str: The generated response text.
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
    
    # Decode the tokens to a human-readable string, skipping special tokens.
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response

if __name__ == '__main__':
    # A simple test to verify that the model is working as expected.
    sample_prompt = "Hello, who are you?"
    print("Prompt:", sample_prompt)
    result = generate_response(sample_prompt)
    print("Response:", result)