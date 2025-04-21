from dotenv import load_dotenv
load_dotenv()  # pip install python-dotenv
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("Please set $HF_TOKEN")

MODEL_ID     = "meta-llama/Llama-3.2-1B-Instruct"
SYSTEM_PROMPT = "You are a helpful, assistant."

print(f"Loading {MODEL_ID}…")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_auth_token=HF_TOKEN)
model     = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    use_auth_token=HF_TOKEN,
    torch_dtype=torch.float16,
    device_map="auto",
)

def generate_response(user_text: str,
                      history: list[tuple[str,str]] = None,
                      max_new_tokens: int = 128,
                      temperature: float    = 0.7) -> str:
    """
    user_text: the latest message from the user
    history:   optional list of (user,assistant) pairs from prior turns
    """
    # 1) build the prompt
    prompt = SYSTEM_PROMPT + "\n\n"
    if history:
        for u, a in history:
            prompt += f"User: {u}\nAssistant: {a}\n\n"
    prompt += f"User: {user_text}\nAssistant: "

    # 2) tokenize
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    input_len = inputs.input_ids.shape[1]

    # 3) generate
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )

    # 4) decode only the new tokens (so we don’t re‑decode the prompt)
    gen_tokens    = outputs[0][input_len:]
    gen_text_full = tokenizer.decode(gen_tokens, skip_special_tokens=True)

    # 5) trim off any accidental “User:” or extra “Assistant:” at the end
    #    (we only want the assistant’s immediate reply)
    for marker in ("User:", "Assistant:"):
        if marker in gen_text_full:
            gen_text_full = gen_text_full.split(marker)[0].strip()

    return gen_text_full

if __name__ == "__main__":
    # quick sanity check
    print(generate_response("Hi, how are you?", max_new_tokens=64))
