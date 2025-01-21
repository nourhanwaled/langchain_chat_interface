import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from app.utils.chat_processor import ChatProcessor
from app.config import DATA_FOLDER
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
chat_processor = None

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class QuestionRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[dict]] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the chat processor on startup"""
    global chat_processor
    
    logger.info("Starting FastAPI server...")
    try:
        chat_processor = ChatProcessor()
        logger.info("Chat processor initialized successfully")
        logger.info(f"Documents directory: {os.path.abspath(DATA_FOLDER)}")
    except Exception as e:
        logger.error(f"Error initializing chat processor: {str(e)}")
        raise

@app.get("/")
async def root():
    return {"message": "Chat API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not chat_processor:
        raise HTTPException(status_code=500, detail="Chat processor not initialized")
    
    try:
        answer, sources = await chat_processor.get_answer(request.message)
        return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Process a question and return an answer."""
    if not chat_processor:
        raise HTTPException(status_code=500, detail="Chat processor not initialized")
    
    try:
        logger.info(f"Received question: {request.question}")
        answer, sources = await chat_processor.get_answer(request.question)
        return {"answer": answer, "sources": sources}
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/check-vector-store")
async def check_vector_store():
    """Endpoint to check the contents of the vector store"""
    if not chat_processor:
        raise HTTPException(status_code=500, detail="Chat processor not initialized")
    
    try:
        # Get the number of documents in the vector store
        count = chat_processor._vector_store._collection.count()
        
        # Get a sample query result
        test_query = "ما هي القيم الأخلاقية؟"
        results = chat_processor._vector_store.similarity_search(test_query, k=2)
        
        sample_docs = []
        for doc in results:
            sample_docs.append({
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata
            })
        
        return {
            "status": "success",
            "document_count": count,
            "sample_query": test_query,
            "sample_results": sample_docs
        }
    except Exception as e:
        logger.error(f"Error checking vector store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get("/stream")
async def stream(question: str):
    if not chat_processor:
        raise HTTPException(status_code=500, detail="Chat processor not initialized")

    async def event_generator():
        answer, _ = await chat_processor.get_answer(question)
        for part in answer.split():
            yield f"data: {part}\n\n"
            time.sleep(0.5)  # Adjust timing as needed

    return StreamingResponse(event_generator(), media_type="text/event-stream")