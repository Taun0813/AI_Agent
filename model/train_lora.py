import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, default_data_collator
from peft import LoraConfig, get_peft_model
from datasets import Dataset
import os

hf_token = os.getenv("HF_TOKEN")
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Load model base
base_model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float32,
    device_map={"": "cpu"},
    token=hf_token
)

# LoRA config
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(base_model, lora_config)
model.print_trainable_parameters()

# Tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
tokenizer.pad_token = tokenizer.eos_token

# Dataset
data = [
    {"conversations": [
        {"role": "user", "content": "Điện thoại nào pin trâu dưới 10 triệu?"},
        {"role": "assistant", "content": "Redmi Note 13 Pro, Realme 11x đều rất tốt về pin trong tầm giá này."}
    ]}
]

def conversation_to_prompt(data_item):
    conv = data_item["conversations"]
    prompt = ""
    for turn in conv:
        role = "User" if turn["role"] == "user" else "Assistant"
        prompt += f"{role}: {turn['content']}\n"
    return {"text": prompt}

raw_dataset = Dataset.from_list(data)
dataset = raw_dataset.map(conversation_to_prompt)

def tokenize_function(examples):
    tokens = tokenizer(examples["text"], truncation=True, padding="max_length", max_length=256)
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

tokenized_dataset = dataset.map(tokenize_function, batched=True)
tokenized_dataset = tokenized_dataset.remove_columns(["conversations", "text"])
tokenized_dataset.set_format("torch")

# Trainer
args = TrainingArguments(
    output_dir="./tinyllama-lora-adapter",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    num_train_epochs=3,
    learning_rate=2e-4,
    logging_steps=1,
    save_strategy="epoch",
    report_to="none",
    disable_tqdm=False
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_dataset,
    data_collator=default_data_collator
)

trainer.train()

# Save LoRA adapter
model.save_pretrained("./tinyllama-lora-adapter")
tokenizer.save_pretrained("./tinyllama-lora-adapter")
