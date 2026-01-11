from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import logging
from backend.rag_engine import RAGEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Q&A API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_engine = RAGEngine()

class ChatRequest(BaseModel):
    session_id: str
    query: str

class UrlRequest(BaseModel):
    url: str

class TextRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"message": "RAG Q&A API is running"}

@app.post("/process/url")
def process_url(request: UrlRequest):
    session_id = str(uuid.uuid4())
    try:
        rag_engine.process_input(session_id, "Link", request.url)
        return {"session_id": session_id, "message": "URL processed successfully"}
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/text")
def process_text(request: TextRequest):
    session_id = str(uuid.uuid4())
    try:
        rag_engine.process_input(session_id, "Text", request.text)
        return {"session_id": session_id, "message": "Text processed successfully"}
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/file")
async def process_file(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    content_type = file.content_type
    filename = file.filename.lower()
    
    input_type = None
    if filename.endswith(".pdf"):
        input_type = "PDF"
    elif filename.endswith(".docx"):
        input_type = "DOCX"
    elif filename.endswith(".txt"):
        input_type = "TXT"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        content = await file.read()
        rag_engine.process_input(session_id, input_type, content)
        return {"session_id": session_id, "message": "File processed successfully"}
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = rag_engine.answer_question(request.session_id, request.query)
        if "Session not found" in str(response):
             raise HTTPException(status_code=404, detail=str(response))
        return {"response": response}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        # Check if session exists first to avoid complex error handling in stream
        if request.session_id not in rag_engine.vectorstores:
             raise HTTPException(status_code=404, detail="Session not found. Please upload a document first.")
             
        async def event_generator():
            for chunk in rag_engine.answer_question_stream(request.session_id, request.query):
                yield chunk

        return StreamingResponse(event_generator(), media_type="text/plain")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat_stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))
