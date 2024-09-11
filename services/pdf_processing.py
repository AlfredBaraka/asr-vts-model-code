from fastapi import UploadFile, HTTPException
from app.ingestion import save_pdf_to_vector_store
from llama_index.readers.file import PyMuPDFReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from embeddings.embedding_model import get_embedding
from llama_index.vector_stores.postgres import PGVectorStore
from app.ingestion import initialize_vector_store
import os
import logging
import re

# Ensure this directory exists
os.makedirs('./data', exist_ok=True)

def clean_text(text: str) -> str:
    """Convert text to lowercase and remove unnecessary characters while retaining spaces."""
    # Convert to lowercase
    text = text.lower()
    # Remove characters except alphabets, numbers, periods, commas, and spaces
    text = re.sub(r'[^a-zA-Z0-9.,\s]', '', text)
    return text


async def upload_pdf(file: UploadFile, vector_table: str):
    file_location = f"./data/{file.filename}"
    
    try:
        # Write file to disk
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # Load and process the PDF
        loader = PyMuPDFReader()
        documents = loader.load(file_path=file_location)

        text_parser = SentenceSplitter(chunk_size=1024)
        text_chunks = []
        doc_idxs = []
        for doc_idx, doc in enumerate(documents):
            cur_text_chunks = text_parser.split_text(doc.text)
            cur_text_chunks = [clean_text(chunk) for chunk in cur_text_chunks]
            text_chunks.extend(cur_text_chunks)
            doc_idxs.extend([doc_idx] * len(cur_text_chunks))

        nodes = []
        for idx, text_chunk in enumerate(text_chunks):
            node = TextNode(text=text_chunk)
            src_doc = documents[doc_idxs[idx]]
            node.metadata = src_doc.metadata
            nodes.append(node)

        for node in nodes:
            node_embedding = get_embedding(node.get_content(metadata_mode="all"))
            node.embedding = node_embedding

        vector_store = initialize_vector_store(vector_table)
        vector_store.add(nodes)

        # Clean up the file after processing
        os.remove(file_location)

        return {"message": "PDF uploaded and processed successfully."}

    except Exception as e:
        logging.error(f"Error processing PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process PDF.")
