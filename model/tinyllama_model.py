import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

# Load token từ biến môi trường
hf_token = os.getenv("HF_TOKEN")

model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float32,
    token=hf_token
).to("cpu")

def generate_response(prompt, max_new_tokens=128, temperature=0.7):
    inputs = tokenizer(prompt, return_tensors="pt").to("cpu")
    output = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=True
    )
    return tokenizer.decode(output[0], skip_special_tokens=True)
