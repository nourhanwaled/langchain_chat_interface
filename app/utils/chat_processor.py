from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from .document_processor import normalize_arabic
from ..config import (
    GOOGLE_API_KEY, 
    EMBEDDING_MODEL, 
    CHAT_MODEL, 
    CHUNK_RETRIEVAL_K,
    VECTOR_STORE_PATH
)
import os
import logging
from typing import Tuple, List
from langchain.schema import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

class ChatProcessor:
    def __init__(self):
        """Initialize the chat processor with necessary components."""
        logger.info("Initializing ChatProcessor...")
        
        # Log which models we're using
        logger.info(f"Using Google API models - Embedding: models/embedding-001, Chat: gemini-1.5-flash")
        
        # Initialize the embedding model
        logger.info("Testing embedding model...")
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        
        # Test the embedding model
        test_embedding = self._embeddings.embed_query("Test query")
        logger.info(f"Embedding test successful. Vector dimension: {len(test_embedding)}")
        
        # Initialize vector store
        logger.info("Starting vector store initialization...")
        self.initialize_vector_store()
        
        # Initialize the chat model
        self._chat_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_API_KEY,
            convert_system_message_to_human=True,
            temperature=0.7
        )

    def initialize_vector_store(self):
        """Load the existing vector store from disk."""
        logger.info("Starting vector store initialization...")
        logger.info(f"Loading vector store from: {VECTOR_STORE_PATH}")
        
        if not os.path.exists(VECTOR_STORE_PATH):
            logger.error(f"Vector store not found at {VECTOR_STORE_PATH}")
            logger.error("Please run create_vector_store.py first to create the vector store")
            raise FileNotFoundError(f"Vector store not found at {VECTOR_STORE_PATH}")
            
        try:
            logger.info("Loading Chroma vector store...")
            self._vector_store = Chroma(
                persist_directory=VECTOR_STORE_PATH,
                embedding_function=self._embeddings
            )
            logger.info("Chroma initialization successful")
            
            logger.info(f"Creating retriever with k={CHUNK_RETRIEVAL_K}")
            self.vector_index = self._vector_store.as_retriever(
                search_kwargs={"k": CHUNK_RETRIEVAL_K}
            )
            logger.info("Retriever created successfully")
            
            # Get collection stats
            collection = self._vector_store._collection
            count = collection.count()
            logger.info(f"Vector store loaded successfully with {count} documents")
            
            # Log sample documents
            if count > 0:
                logger.info("Retrieving sample documents...")
                sample_results = collection.peek(limit=2)
                logger.info(f"Retrieved {len(sample_results['documents'])} sample documents")
                
                for i, doc in enumerate(sample_results["documents"]):
                    logger.info(f"Sample document {i+1} content preview: {doc[:200]}...")
                    logger.info(f"Sample document {i+1} metadata: {sample_results['metadatas'][i]}")
            else:
                logger.warning("Vector store exists but contains no documents")
                
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            logger.exception("Full traceback:")
            raise
        
        logger.info("Vector store initialization completed successfully")

    async def get_answer(self, question: str) -> Tuple[str, List[dict]]:
        """
        Get an answer for the given question using the vector store and chat model.
        Returns the answer and a list of source documents.
        """
        try:
            # Search for relevant documents
            docs = self._vector_store.similarity_search(question, k=185)
            
            # Extract the content and create the context
            context = "\n\n".join([doc.page_content for doc in docs])
            logger.info(f"Combined context length: {len(context)} characters")
            
            # Create source information
            sources = [
                {
                    "source": doc.metadata.get("source", "Unknown"),
                    "content": doc.page_content[:200] + "..."
                }
                for doc in docs
            ]
            
            # Create the prompt
            prompt = f"""Based on the following context, answer the question in Arabic. If you cannot find a relevant answer in the context, say so.

Context:
{context}

Question: {question}

Answer:"""
            
            logger.info("Generating answer using AI model...")
            messages = [SystemMessage(content="You are a helpful assistant that answers questions based on the given context."),
                       HumanMessage(content=prompt)]
            
            response = await self._chat_model.agenerate([messages])
            answer = response.generations[0][0].text.strip()
            
            logger.info(f"Generated answer length: {len(answer)} characters")
            return answer, sources
            
        except Exception as e:
            logger.error(f"Error getting answer: {str(e)}")
            raise 

    def _format_arabic_answer(self, text: str) -> str:
        """Format Arabic text with proper styling."""
        # Split text into lines
        lines = text.split('*')
        
        # Process each line
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if line:
                # Add bullet point if line doesn't start with one
                if not line.startswith('•'):
                    line = '• ' + line
                formatted_lines.append(line)
        
        # Join lines with proper spacing
        text = '\n'.join(formatted_lines)
        
        # Add proper spacing after punctuation
        text = text.replace('،', '، ')
        text = text.replace(':', ':\n')
        
        # Clean up any extra whitespace
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        
        # Add right-to-left mark for proper text alignment
        text = '\u200F' + text
        
        return text 