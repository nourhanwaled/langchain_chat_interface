from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.embeddings.google_palm import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the embeddings model
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Specify the directory where the vector index was extracted
persist_directory = "../vector_index_storage"

# Load the persisted vector index
vector_index = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings.embed_query
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Get the most similar documents
        docs = vector_index.similarity_search(request.message, k=3)
        
        # Combine the content of the documents
        response = "\n\n".join([doc.page_content for doc in docs])
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 