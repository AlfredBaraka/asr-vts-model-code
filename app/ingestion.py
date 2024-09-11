from embeddings.embedding_model import get_embedding
from app.database import SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from llama_index.vector_stores.postgres import PGVectorStore

def initialize_vector_store(table_name: str) -> PGVectorStore:
    vector_store = PGVectorStore.from_params(
        database="alfred_db",
        host="172.17.17.241",
        password="password",
        port="5432",
        user="alfred",
        table_name=table_name,
        embed_dim=384
    )
    return vector_store

def save_pdf_to_vector_store(file_path: str, vector_store: PGVectorStore):
    # Logic for processing PDF and adding to vector store
    pass
