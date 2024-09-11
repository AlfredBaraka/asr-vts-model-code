from typing import AsyncIterator
from llama_cpp import Llama
from app.config import DATABASE_URL
from app.retrieval import vector_query
from app.utils import process_search_results
from embeddings.embedding_model import get_embedding

ega = """
Mamlaka ya Serikali Mtandao (e-GA) ni taasisi ya umma iliyoanzishwa kwa Sheria ya Serikali Mtandao Na. 10 ya mwaka 2019. Ni taasisi yenye jukumu la kuratibu, kusimamia na kukuza jitihada za Serikali Mtandao pamoja na kuhimiza utekelezaji wa Sera, Sheria, Kanuni, Viwango na Miongozo ya Serikali Mtandao kwa taasisi za umma."""

llm = Llama(
    model_path="/home/egovridc/Desktop/learn/model/swahili4.gguf",
    chat_format="llama-3",
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=33,
)

async def stream_complete(prompt: str, use_rag: bool = False, table: str = "") -> AsyncIterator[str]:
    if use_rag:
        query_embedding = get_embedding(prompt)
        search_results = vector_query(query_embedding, table)
        print(search_results)
        # result_content = process_search_results(search_results)
        combined_prompt = f"Based on the documents found: {search_results}\n\n{prompt}"
    else:
        combined_prompt = prompt

    output = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": f"You are an assistant in kiswahili for Tanzanians you recognized samia suluhu hassan the current and sixth president of Tanzania and {ega}."},
            {"role": "user", "content": combined_prompt}
        ],
        stream=True
    )

    for chunk in output:
        delta = chunk['choices'][0]['delta']
        if 'content' in delta:
            yield delta['content']
