import os
import re
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

def normalize_arabic(text):
    """Normalize Arabic text by unifying forms and removing diacritics."""
    text = re.sub(r"[\u064B-\u0652]", "", text)  # Remove diacritics
    text = re.sub(r"[إأآا]", "ا", text)  # Normalize alef
    text = re.sub(r"ة", "ه", text)  # Normalize taa marbuta
    text = re.sub(r"ى", "ي", text)  # Normalize yaa
    return text

def load_and_split_files(folder_path):
    """Load and split .docx files into chunks."""
    logger.info(f"Starting document loading from: {folder_path}")
    
    if not os.path.exists(folder_path):
        logger.error(f"Directory does not exist: {folder_path}")
        return [], []
        
    logger.info(f"Directory exists and is accessible")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    all_chunks = []
    metadatas = []
    total_files = 0
    processed_files = 0

    # Log all directories first
    for root, dirs, files in os.walk(folder_path):
        logger.info(f"Scanning directory: {root}")
        logger.info(f"Found subdirectories: {dirs}")
        docx_files = [f for f in files if f.endswith('.docx')]
        logger.info(f"Found .docx files in {root}: {docx_files}")
        total_files += len(docx_files)
        
        for file in docx_files:
            try:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, folder_path)
                logger.info(f"Processing file: {relative_path}")
                logger.info(f"Full file path: {os.path.abspath(file_path)}")
                
                # Verify file exists and is readable
                if not os.path.isfile(file_path):
                    logger.error(f"File does not exist: {file_path}")
                    continue
                    
                logger.info(f"File exists and is readable: {file_path}")
                
                doc = Document(file_path)
                paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
                logger.info(f"Found {len(paragraphs)} non-empty paragraphs in {file}")
                
                if not paragraphs:
                    logger.warning(f"No content found in file: {file}")
                    continue
                
                content = "\n".join([normalize_arabic(p) for p in paragraphs])
                logger.info(f"Total content length for {file}: {len(content)} characters")
                
                chunks = text_splitter.split_text(content)
                logger.info(f"Split into {len(chunks)} chunks")
                
                if not chunks:
                    logger.warning(f"No chunks created for file: {file}")
                    continue
                
                all_chunks.extend(chunks)
                metadatas.extend([{
                    "file_name": file,
                    "source": relative_path,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                } for i in range(len(chunks))])
                
                processed_files += 1
                logger.info(f"Successfully processed {file}")
                
            except Exception as e:
                logger.error(f"Error processing file {file}: {str(e)}")
                logger.exception("Full traceback:")
                continue

    logger.info(f"Document processing complete. Processed {processed_files}/{total_files} files")
    logger.info(f"Total chunks created: {len(all_chunks)}")
    
    if not all_chunks:
        logger.warning("No content was extracted from any documents")
    else:
        # Log sample of first chunk to verify content
        logger.info(f"Sample from first chunk: {all_chunks[0][:200]}...")
    
    return all_chunks, metadatas 