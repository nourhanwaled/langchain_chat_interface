import logging
import os
import shutil
from app.utils.document_processor import load_and_split_files
from app.config import DATA_FOLDER, VECTOR_STORE_PATH, GOOGLE_API_KEY
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_document_loading():
    # Use the path from config
    folder_path = DATA_FOLDER
    
    logger.info(f"Testing document loading from path: {folder_path}")
    logger.info(f"Absolute path: {os.path.abspath(folder_path)}")
    
    # First, let's list all .docx files in the directory
    logger.info("Scanning for .docx files...")
    all_docx_files = []
    for root, dirs, files in os.walk(folder_path):
        docx_files = [f for f in files if f.endswith('.docx')]
        if docx_files:
            logger.info(f"Found in {root}:")
            for file in docx_files:
                full_path = os.path.join(root, file)
                all_docx_files.append(full_path)
                logger.info(f"  - {file} (Size: {os.path.getsize(full_path)} bytes)")
    
    logger.info(f"\nTotal .docx files found: {len(all_docx_files)}")
    
    # Now load and split the documents
    logger.info("\nProcessing documents...")
    chunks, metadatas = load_and_split_files(folder_path)
    
    logger.info(f"\nProcessing Results:")
    logger.info(f"Total chunks created: {len(chunks)}")
    
    # Group chunks by source file
    files_chunks = {}
    for chunk, metadata in zip(chunks, metadatas):
        source = metadata['source']
        if source not in files_chunks:
            files_chunks[source] = []
        files_chunks[source].append(chunk)
    
    logger.info("\nChunks per file:")
    for source, file_chunks in files_chunks.items():
        logger.info(f"  - {source}: {len(file_chunks)} chunks")
        if file_chunks:
            logger.info(f"    First chunk preview: {file_chunks[0][:100]}...")

    # Test vector store creation
    logger.info("\nTesting vector store creation...")
    
    # Remove existing vector store if it exists
    if os.path.exists(VECTOR_STORE_PATH):
        logger.info(f"Removing existing vector store at {VECTOR_STORE_PATH}")
        shutil.rmtree(VECTOR_STORE_PATH)
    
    try:
        # Initialize embeddings
        logger.info("Initializing embeddings model...")
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        
        # Create vector store
        logger.info(f"Creating vector store with {len(chunks)} chunks...")
        vector_store = Chroma.from_texts(
            chunks,
            embeddings,
            metadatas=metadatas,
            persist_directory=VECTOR_STORE_PATH
        )
        vector_store.persist()
        
        # Verify vector store
        logger.info("Verifying vector store...")
        collection = vector_store._collection
        count = collection.count()
        logger.info(f"Vector store contains {count} documents")
        
        if count > 0:
            # Test retrieval
            logger.info("\nTesting document retrieval...")
            test_query = "ما هي قيمة الأمانة؟"
            logger.info(f"Test query: {test_query}")
            
            results = vector_store.similarity_search(test_query, k=2)
            logger.info(f"Retrieved {len(results)} results")
            
            for i, doc in enumerate(results):
                logger.info(f"\nResult {i+1}:")
                logger.info(f"Source: {doc.metadata['source']}")
                logger.info(f"Content preview: {doc.page_content[:200]}...")
        
        logger.info("\nVector store test completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing vector store: {str(e)}")
        raise

if __name__ == "__main__":
    test_document_loading() 