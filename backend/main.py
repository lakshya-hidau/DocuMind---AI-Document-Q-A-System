from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
import logging

from backend.rag_engine import RAGEngine

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# App Init
# --------------------------------------------------
app = FastAPI(title="RAG Q&A API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# RAG Engine (Singleton)
# --------------------------------------------------
rag_engine: RAGEngine | None = None

def get_rag_engine() -> RAGEngine:
    global rag_engine
    if rag_engine is None:
        rag_engine = RAGEngine()
    return rag_engine

# --------------------------------------------------
# Request Models
# --------------------------------------------------
class ChatRequest(BaseModel):
    session_id: str
    query: str

class UrlRequest(BaseModel):
    url: str

class TextRequest(BaseModel):
    text: str

# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.get("/")
def root():
    return {"message": "RAG Q&A API is running 🚀"}

# ---------------------------
# Process URL
# ---------------------------
@app.post("/process/url")
def process_url(request: UrlRequest):
    session_id = str(uuid.uuid4())
    try:
        engine = get_rag_engine()
        engine.process_input(session_id, "Link", request.url)
        return {
            "session_id": session_id,
            "message": "URL processed successfully"
        }
    except Exception as e:
        logger.exception("URL processing failed")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------
# Process Raw Text
# ---------------------------
@app.post("/process/text")
def process_text(request: TextRequest):
    session_id = str(uuid.uuid4())
    try:
        engine = get_rag_engine()
        engine.process_input(session_id, "Text", request.text)
        return {
            "session_id": session_id,
            "message": "Text processed successfully"
        }
    except Exception as e:
        logger.exception("Text processing failed")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------
# Process File
# ---------------------------
@app.post("/process/file")
async def process_file(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    filename = file.filename.lower()

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
        engine = get_rag_engine()
        engine.process_input(session_id, input_type, content)
        return {
            "session_id": session_id,
            "message": "File processed successfully"
        }
    except Exception as e:
        logger.exception("File processing failed")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------
# Chat (Non-Streaming)
# ---------------------------
@app.post("/chat")
def chat(request: ChatRequest):
    engine = get_rag_engine()

    if request.session_id not in engine.vectorstores:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please upload a document first."
        )

    try:
        answer = engine.answer_question(
            request.session_id,
            request.query
        )
        return {"response": answer}
    except Exception as e:
        logger.exception("Chat failed")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------
# Chat (Streaming)
# ---------------------------
@app.post("/chat/stream")
def chat_stream(request: ChatRequest):
    engine = get_rag_engine()

    if request.session_id not in engine.vectorstores:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please upload a document first."
        )

    def event_generator():
        try:
            for chunk in engine.answer_question_stream(
                request.session_id,
                request.query
            ):
                yield chunk
        except Exception as e:
            logger.exception("Streaming failed")
            yield f"\n[ERROR]: {str(e)}"

    return StreamingResponse(
        event_generator(),
        media_type="text/plain"
    )
