import os

# Google API Key
GOOGLE_API_KEY = "AIzaSyDsWLnodFOeRJj1bDjEG8LQ5uCRwNoGkLQ"

# Paths
DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data", "ملحقات القيم")
VECTOR_STORE_PATH = os.path.join(os.path.dirname(__file__), "vector_index_storage")

# Model Settings
EMBEDDING_MODEL = "models/embedding-001"
CHAT_MODEL = "gemini-1.5-flash"

# Vector Store Settings
CHUNK_RETRIEVAL_K = 185  # Number of most relevant chunks to retrieve 