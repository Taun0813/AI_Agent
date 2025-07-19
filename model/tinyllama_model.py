import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import os

# --- 1️⃣ Khởi tạo model 1 lần duy nhất ---
hf_token = os.getenv("HF_TOKEN")
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Load tokenizer 1 lần
tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)

# Load base model 1 lần, dùng float16 + device_map để tự chọn GPU
base_model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto",
    token=hf_token
)

# Load LoRA adapter (nếu bạn đang fine-tune)
model = PeftModel.from_pretrained(base_model, "./tinyllama-lora-adapter")

# Đặt về eval mode
model.eval()

# --- 2️⃣ Hàm sinh phản hồi ---
def generate_response(prompt, max_new_tokens=128, temperature=0.7):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response
