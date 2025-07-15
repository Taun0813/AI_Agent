import faiss
import numpy as np
import json

class ProductRetriever:
    def __init__(self, index_path, embedding_path, data_path):
        self.index = faiss.read_index(index_path)
        self.embeddings = np.load(embedding_path)
        
        print(f"[INFO] Loading dataset from: {data_path}")
        with open(data_path, "r", encoding="utf-8") as f:
            self.products = json.load(f)
        print(f"[INFO] Loaded {len(self.products)} products from dataset.")

    def search(self, query_vector, top_k=5):
        scores, indices = self.index.search(query_vector, top_k)
        return [self.products[i] for i in indices[0]]


