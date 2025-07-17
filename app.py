from fastapi import FastAPI
from pydantic import BaseModel
from model.embedder import Embedder
from pipeline.retriever import ProductRetriever
from pipeline.prompt_template import generate_prompt
from model.tinyllama_model import generate_response  # function, không phải class
import os
import numpy as np

# Khởi tạo FastAPI app
app = FastAPI()

# Load models và index
embedder = Embedder()
retriever = ProductRetriever(
    index_path="vectorstore/index.faiss",
    embedding_path="vectorstore/embeddings.npy",
    data_path="data/processed.json"  # hoặc dataset.json nếu bạn không tạo file xử lý
)

class ChatRequest(BaseModel):
    query: str
    max_new_tokens: int = 128
    temperature: float = 0.7

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # Bước 1: Vector hóa truy vấn người dùng
    query_vector = embedder.encode([req.query]).astype("float32")

    # Bước 2: Tìm sản phẩm gần nhất
    top_products = retriever.search(query_vector)

    # Bước 3: Tạo prompt đầu vào LLM
    prompt = generate_prompt(req.query, top_products)

    # Bước 4: Sinh phản hồi từ TinyLlama
    response = generate_response(
        prompt,
        max_new_tokens=req.max_new_tokens,
        temperature=req.temperature
    )

    return {
        "query": req.query,
        "top_products": top_products,  
        "response": response
    }

