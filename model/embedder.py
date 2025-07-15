from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    def __init__(self, model_name: str = "intfloat/multilingual-e5-base"):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True)

