from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.vectorstores import Chroma
from langchain.embeddings.google_palm import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    # Load the embeddings model
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # Specify the directory where the vector index was extracted
    persist_directory = "../app/vector_index_storage"

    # Load the persisted vector index
    vector_index = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings.embed_query
    )
    print("Vector index loaded successfully!")

except Exception as e:
    print(f"Error initializing vector store: {str(e)}")
    raise

class SearchQuery(BaseModel):
    query: str

@app.post("/search")
async def search(query: SearchQuery):
    try:
        # Search for similar documents
        docs = vector_index.similarity_search(query.query, k=3)
        
        # Extract and return the content
        results = [doc.page_content for doc in docs]
        return {"results": results}
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"} 