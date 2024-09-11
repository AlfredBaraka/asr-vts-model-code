from typing import List, Dict, Any
from llama_index.vector_stores.postgres import PGVectorStore
# export PYTHONPATH=/home/egovridc/Desktop/learn


def process_search_results(results: List[Dict[str, Any]]) -> str:
    # Convert search results to readable text
    return " ".join([r['content'] for r in results])
