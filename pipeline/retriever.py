import faiss
import numpy as np
import json
import re


class ProductRetriever:
    def __init__(self, index_path, embedding_path, data_path):
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        # Load original embeddings (nếu cần kiểm tra)
        self.embeddings = np.load(embedding_path)

        # Load dữ liệu sản phẩm gốc
        print(f"[INFO] Loading dataset from: {data_path}")
        with open(data_path, "r", encoding="utf-8") as f:
            self.products = json.load(f)
        print(f"[INFO] Loaded {len(self.products)} products from dataset.")

    def search(self, query_vector, user_query: str, top_k=20):
        # Lấy top K gần đúng nhất từ FAISS
        scores, indices = self.index.search(query_vector, top_k)
        retrieved = [self.products[i] for i in indices[0]]

        # Trích xuất yêu cầu cụ thể từ câu hỏi
        filters = self._extract_filters_from_query(user_query)

        # Lọc lại theo thuộc tính chính xác
        filtered = [p for p in retrieved if self._match_filters(p, filters)]

        return filtered[:5]  # Trả lại tối đa 5 sản phẩm phù hợp nhất

    def _extract_filters_from_query(self, query):
        filters = {}
        # Tìm pin
        if match := re.search(r"pin\s*(\d+)", query):
            filters["battery_capacity"] = int(match.group(1))
        # Tìm giá
        if match := re.search(r"giá\s*(\d+)", query):
            filters["price"] = int(match.group(1))
        # Tìm RAM
        if match := re.search(r"ram\s*(\d+)", query):
            filters["ram_capacity"] = int(match.group(1))
        # Tìm 5G
        if match := re.search(r"5G\s*(\d+)", query):
            filters["has_5g"] = True
        return filters

    def _match_filters(self, product, filters):
        for key, value in filters.items():
            if key not in product:
                continue
            if isinstance(value, (int, float)):
                if product[key] != value:
                    return False
            elif isinstance(value, str):
                if str(product[key]).lower() != value.lower():
                    return False
        return True
