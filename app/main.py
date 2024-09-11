from fastapi import FastAPI, UploadFile, Query, File, Form, HTTPException, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from services.pdf_processing import upload_pdf
from services.llama_service import stream_complete
from app.models import CreateTableRequest, SearchRequest
from app.database import SessionLocal, engine
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
from typing import Optional
from sqlalchemy import make_url
from llama_index.vector_stores.postgres import PGVectorStore
from app.config import database_config
import logging
import asyncpg
from app.retrieval import vector_query
from embeddings.embedding_model import get_embedding
from services.tts import  generate_speech_from_text
from pathlib import Path
from services.asr import transcribe_audio

# uvicorn app.main:app --host 172.17.17.192 --port 8000 --reload 

# uvicorn app.main:app --reload
app = FastAPI()

# Get the absolute path to the 'static' directory
static_directory = os.path.join(os.path.dirname(__file__), 'static')

# Serve static files from the 'static' directory
app.mount("/static", StaticFiles(directory=static_directory), name="static")

# Endpoints

# HTML interface

@app.get("/static/{file_path:path}")
async def get_static_file(file_path: str):
    return FileResponse(os.path.join(static_directory, file_path))


@app.get("/asr")
async def read_index():
    return FileResponse('app/static/asr.html')


@app.get("/")
async def read_index():
    return FileResponse('app/static/intro.html')

@app.get("/chat")
async def read_index():
    return FileResponse('app/static/index.html')

@app.get("/search")
async def read_index():
    return FileResponse('app/static/search.html')

@app.get("/rag_management")
async def read_db_management():
    return FileResponse('app/static/db_management.html')

# tts app 
@app.get("/tts")
async def read_tts():
    return FileResponse('app/static/audio.html')

@app.post("/create_table")
async def create_table(request: CreateTableRequest):
    try:
        table_name = request.table_name
        # Create the PGVectorStore instance
        vector = PGVectorStore.from_params(
            database="alfred_db",
            host="172.17.17.241",
            password="password",
            port=5432,
            user="alfred",
            table_name=table_name,
            embed_dim=384,
        )
        
        try:
            # Attempt to add a vector (this might trigger an AttributeError)
            vector.add([0])  # Replace this with appropriate data if needed
        except AttributeError as e:
            # Log detailed error information
            logging.error(f"Error adding vector: {e}", exc_info=True)
            # You can choose to continue or handle this case differently

        # Return a success message
        return {"message": "Table created successfully"}
    
    except Exception as e:
        # Log detailed error information for table creation issues
        logging.error(f"Error creating table: {e}", exc_info=True)
        # Raise an HTTPException with a detailed error message
        raise HTTPException(status_code=500, detail="Failed to create table.")
    

@app.post("/upload_pdf")
async def handle_upload_pdf(file: UploadFile = File(...), vector_table: str = Form(...)):
    return await upload_pdf(file, vector_table)

@app.get("/query_service")
async def query_service( prompt: str,
    use_rag: bool = Query(False),
    table: Optional[str] = Query(None)):
    async def generate():
        async for chunk in stream_complete(prompt, use_rag=use_rag, table=table):
            yield chunk
    return StreamingResponse(generate(), media_type="text/plain")


DATABASE_CONFIG = {
    "database": "alfred_db",
    "host": "172.17.17.241",
    "password": "password",
    "port": 5432,
    "user": "alfred",
}

async def get_connection():
    return await asyncpg.connect(**DATABASE_CONFIG)


@app.get("/list_tables")
async def list_tables():
    try:
        conn = await get_connection()
        tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        await conn.close()
        
        # Extract and clean table names from the result
        table_names = [row['table_name'] for row in tables]
        
        # Remove "data_" prefix from each table name
        cleaned_table_names = [name.replace("data_", "") for name in table_names]
        
        return cleaned_table_names
    except Exception as e:
        logging.error(f"Error listing tables: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list tables.")
    
@app.post("/semantic_search")
async def semantic_search(request: SearchRequest):
    try:
        embedded_query = get_embedding(request.query)
        answer = vector_query(embedded_query, request.table, fetch_all=True)
        return {"answer": answer}
    except Exception as e:
        logging.error(f"Error in semantic search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to perform semantic search.")
    



@app.post("/generate/")
async def generate_text_to_speech(request: Request, text: str = Form(...)):
    output_file = "app/static/audio/output.wav"
    generate_speech_from_text(text, output_file)
    return FileResponse(output_file, media_type="audio/wav")





@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Receive the input from the user
        data = await websocket.receive_text()
        prompt, use_rag, rag_table, voice_enabled = data.split('::')

        # Stream text completion
        async for text_chunk in stream_complete(prompt, use_rag=use_rag, table=rag_table):
            await websocket.send_text(f"text::{text_chunk}")
            
            # If voice is enabled, generate and send voice data as a file URL
            if voice_enabled == 'true':
                output_file = f"static/audio/{os.path.basename(prompt)}.wav"
                generate_speech_from_text(text_chunk, output_file=output_file)
                await websocket.send_text(f"audio::{output_file}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()
        
        



# API endpoint for uploading and transcribing audio
@app.post("/transcribe/")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    temp_audio_path = Path(f"./app/audio/{file.filename}")
    
    with open(temp_audio_path, "wb") as buffer:
        buffer.write(await file.read())

    # Call service to transcribe the audio
    transcription = transcribe_audio(temp_audio_path)
    
    # Optionally, delete the audio file after processing
    temp_audio_path.unlink()
    
    return {"transcription": transcription}