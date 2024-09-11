from typing import List, Dict, Any
from fastapi import HTTPException
import psycopg2
from psycopg2 import sql
from app.config import DATABASE_URL
from llama_index.core.vector_stores import VectorStoreQuery
from app.ingestion import initialize_vector_store
from embeddings.embedding_model import get_embedding

    

def vector_query(query_embedding, table, fetch_all=False):
    vector_store = initialize_vector_store(table)
    query_mode = "default"
    vector_store_query = VectorStoreQuery(
        query_embedding=query_embedding, similarity_top_k=2, mode=query_mode
    )
    query_result = vector_store.query(vector_store_query)
    
    if fetch_all:
        # Return the content of all top results
        return [node.get_content() for node in query_result.nodes]
    else:
        # Return only the content of the first result
        return query_result.nodes[0].get_content()

