import os
import shutil
import logging
from typing import List
import time
from pathlib import Path
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from utils.document_processor import load_and_split_files
from config import (
    GOOGLE_API_KEY,
    DATA_FOLDER,
    VECTOR_STORE_PATH,
    EMBEDDING_MODEL
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_remove_vector_store():
    """Safely remove the vector store directory."""
    if not os.path.exists(VECTOR_STORE_PATH):
        logger.info("No existing vector store found.")
        return True
    
    max_attempts = 3
    attempt = 0
    while attempt < max_attempts:
        try:
            logger.info(f"Attempting to remove existing vector store (attempt {attempt + 1})")
            shutil.rmtree(VECTOR_STORE_PATH)
            logger.info("Successfully removed existing vector store")
            return True
        except PermissionError:
            attempt += 1
            if attempt < max_attempts:
                logger.warning("Vector store is in use. Waiting 5 seconds before retrying...")
                time.sleep(5)
            else:
                logger.error("Could not remove vector store after multiple attempts. Please ensure no other processes are using it.")
                return False
        except Exception as e:
            logger.error(f"Error removing vector store: {str(e)}")
            return False

def create_vector_store():
    """Create a new vector store from documents."""
    logger.info("Starting vector store creation process")
    
    # Initialize embedding model
    logger.info("Initializing embedding model...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY
    )
    
    # Try to remove existing vector store
    if not safe_remove_vector_store():
        logger.error("Failed to prepare for new vector store creation. Please close any applications using the vector store and try again.")
        return False
    
    try:
        # Load and split documents
        logger.info(f"Loading documents from {DATA_FOLDER}")
        chunks, metadatas = load_and_split_files(DATA_FOLDER)
        
        if not chunks:
            logger.error("No documents were loaded. Please check the data folder.")
            return False
        
        # Convert chunks and metadata into Document objects
        logger.info("Converting chunks to Document objects...")
        documents = []
        for i, (chunk, metadata) in enumerate(zip(chunks, metadatas)):
            try:
                doc = Document(page_content=chunk, metadata=metadata)
                documents.append(doc)
                if (i + 1) % 50 == 0:
                    logger.info(f"Processed {i + 1}/{len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Error processing chunk {i}: {str(e)}")
                continue
        
        logger.info(f"Successfully converted {len(documents)} document chunks")
        
        # Create new vector store
        logger.info("Creating new vector store...")
        try:
            # Ensure the directory exists
            os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
            
            # Create the vector store in batches
            batch_size = 50
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
                
                if i == 0:
                    # Create new vector store with first batch
                    vector_store = Chroma.from_documents(
                        documents=batch,
                        embedding=embeddings,
                        persist_directory=VECTOR_STORE_PATH
                    )
                else:
                    # Add subsequent batches
                    vector_store.add_documents(batch)
                
                # Persist after each batch
                vector_store.persist()
                logger.info(f"Processed and persisted {min(i + batch_size, len(documents))}/{len(documents)} documents")
        
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            logger.error("Full error:", exc_info=True)
            return False
        
        logger.info("Vector store created and persisted successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating vector store: {str(e)}")
        logger.error("Full error:", exc_info=True)
        return False

if __name__ == "__main__":
    success = create_vector_store()
    if success:
        logger.info("Vector store creation completed successfully")
    else:
        logger.error("Vector store creation failed") 