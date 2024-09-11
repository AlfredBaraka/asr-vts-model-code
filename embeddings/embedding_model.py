from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing import List

model_path = '/home/egovridc/Desktop/learn/model/swahili_bge/'

embed_model = HuggingFaceEmbedding(model_name=model_path)

def get_embedding(prompt: str, desired_dim: int = 384) -> List[float]:
    # Get the embedding from the model
    embedding = embed_model.get_text_embedding(prompt)
    
    # Truncate or pad the embedding to the desired dimension
    if len(embedding) > desired_dim:
        return embedding[:desired_dim]
    elif len(embedding) < desired_dim:
        return embedding + [0.0] * (desired_dim - len(embedding))
    else:
        return embedding
