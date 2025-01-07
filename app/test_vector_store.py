import logging
from app.config import VECTOR_STORE_PATH, GOOGLE_API_KEY
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_vector_store():
    try:
        # Initialize embeddings
        logger.info("Initializing embeddings model...")
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )

        # Load the existing vector store
        logger.info(f"Loading vector store from {VECTOR_STORE_PATH}")
        vector_store = Chroma(
            persist_directory=VECTOR_STORE_PATH,
            embedding_function=embeddings
        )

        # Get collection stats
        collection = vector_store._collection
        count = collection.count()
        logger.info(f"Vector store contains {count} documents")

        # Test queries
        test_queries = [
            "ما هي قيمة الصدق؟",
            "ما هي قيمة الأمانة؟",
            "كيف نعلم أطفالنا النظافة؟",
            "ما هي أهمية التعاون؟"
        ]

        for query in test_queries:
            logger.info(f"\nTesting query: {query}")
            results = vector_store.similarity_search_with_relevance_scores(query, k=2)
            
            for i, (doc, score) in enumerate(results):
                logger.info(f"\nResult {i+1} (Relevance Score: {score:.4f}):")
                logger.info(f"Source: {doc.metadata['source']}")
                logger.info(f"Content: {doc.page_content[:300]}...")
                logger.info("-" * 80)

    except Exception as e:
        logger.error(f"Error testing vector store: {str(e)}")
        raise

if __name__ == "__main__":
    test_vector_store() 