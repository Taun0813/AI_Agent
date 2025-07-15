import json
import numpy as np
import faiss
from model.embedder import Embedder

def create_description(product: dict) -> str:
    return (
        f"Model: {product.get('model', '')}, Brand: {product.get('brand_name', '')}, "
        f"Price: {product.get('price', '')} VND, Rating: {product.get('rating', '')}/100, "
        f"Camera: {product.get('primary_camera_rear', '')}MP (rear), {product.get('primary_camera_front', '')}MP (front), "
        f"Battery: {product.get('battery_capacity', '')}mAh, Fast Charging: {product.get('fast_charging', '')}W, "
        f"5G: {'Yes' if product.get('has_5g') else 'No'}, NFC: {'Yes' if product.get('has_nfc') else 'No'}, "
        f"RAM: {product.get('ram_capacity', '')}GB, Storage: {product.get('internal_memory', '')}GB, "
        f"Display: {product.get('screen_size', '')}inch {product.get('resolution_width', '')}x{product.get('resolution_height', '')} px"
    )

def preprocess_and_vectorize(
    input_json_path="data/dataset.json",
    output_json_path="data/processed.json",
    embedding_path="vectorstore/embeddings.npy",
    index_path="vectorstore/index.faiss"
):
    # Load raw data
    with open(input_json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Tạo mô tả + lọc dữ liệu
    processed_data = []
    descriptions = []
    for item in raw_data:
        desc = create_description(item)
        item["description"] = desc
        processed_data.append(item)
        descriptions.append(desc)

    # Save processed data
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

    # Vector hóa
    embedder = Embedder()
    embeddings = embedder.encode(descriptions).astype("float32")
    np.save(embedding_path, embeddings)

    # Tạo FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, index_path)

    print("Tiền xử lý và vector hóa hoàn tất.")

if __name__ == "__main__":
    preprocess_and_vectorize()