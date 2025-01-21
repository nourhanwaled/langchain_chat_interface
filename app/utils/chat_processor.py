from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Chroma
from langchain.chains import ConversationChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.schema import HumanMessage
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
import logging
from typing import Tuple, List
from datetime import datetime
import os
from ..config import (
    GOOGLE_API_KEY, 
    EMBEDDING_MODEL, 
    CHAT_MODEL, 
    CHUNK_RETRIEVAL_K,
    VECTOR_STORE_PATH
)

logger = logging.getLogger(__name__)

class CustomMemory:
    def __init__(self):
        """Initialize custom memory to store conversation history."""
        self.history = []

    async def aget_messages(self) -> List[dict]:
        """Asynchronously return all messages stored in memory."""
        return [{"role": "user", "content": msg} for msg in self.history]

    async def aadd_message(self, message: str):
        """Asynchronously add a message to the history."""
        self.history.append(message)


class ChatProcessor:
    def __init__(self):
        """Initialize the chat processor with necessary components."""
        logger.info("Initializing ChatProcessor...")

        # Initialize the chat model
        self._chat_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_API_KEY,
            convert_system_message_to_human=True,
            temperature=0.7
        )

        # Initialize vector store and embeddings
        self._initialize_embeddings()
        self.initialize_vector_store()

        # Create conversation template
        template = """أنت مساعد ذكي. أجب بإيجاز ووضوح.

المحادثة السابقة:
{history}

السياق من قاعدة المعرفة:
{context}

السؤال الحالي: {input}

تعليمات مهمة:
١. استخدم المعلومات من المحادثات السابقة إذا كانت ذات صلة
٢. استخدم المعلومات من قاعدة المعرفة
٣. اربط بين المعلومات من المصدرين
٤. أجب باللغة العربية
٥. كن دقيقاً ومختصراً

الإجابة:"""

        prompt = PromptTemplate(
            input_variables=["history", "input", "context"],
            template=template
        )

        # Create the chain
        chain = prompt | self._chat_model | StrOutputParser()

        # Initialize custom memory
        self._memory = CustomMemory()

        # Add message history
        self._conversation_chain = RunnableWithMessageHistory(
            chain,
            lambda session_id: self._memory,
            input_messages_key="input",
            history_messages_key="history",
        )

    async def get_answer(self, question: str) -> Tuple[str, List[dict]]:
        """Get an answer for the given question using the conversation chain and vector store context."""
        try:
            # Retrieve relevant documents from the vector store
            docs = self._vector_store.similarity_search(question, k=185)
            docs_context = "\n\n".join([doc.page_content for doc in docs])

            # Retrieve the conversation history
            history = "\n".join([msg['content'] for msg in await self._memory.aget_messages()])

            # Prepare the input context for the conversation
            context_input = {
                "input": question,
                "context": docs_context,
                "history": history
            }

            # Generate response using the conversation chain
            response = await self._conversation_chain.ainvoke(
                context_input,
                config={"configurable": {"session_id": "default"}}
            )
            answer = response.strip()

            # Verify Arabic response
            if not any('\u0600' <= c <= '\u06FF' for c in answer):
                return f"عذراً، يجب أن تكون الإجابة باللغة العربية. الرجاء إعادة السؤال.", []

            # Add citation for the most relevant document
            most_relevant_doc = docs[0] if docs else None
            if most_relevant_doc:
                source = most_relevant_doc.metadata.get('source', 'Unknown')
                link = most_relevant_doc.metadata.get('link', 'No link available')
                logger.info(f"Document Source: {source}, Link: {link}")  # Debugging line
                citation = f"Source: {source}\nLink: {link}"
            else:
                citation = "Source: Unknown\nLink: No link available"

            answer_with_citation = f"{answer}\n\n---\n\n{citation}"

            # Update history
            await self._memory.aadd_message(f"Q: {question}\nA: {answer_with_citation}")

            # Return the answer with citation and the sources
            sources = [
                {
                    "source": source,
                    "content": most_relevant_doc.page_content[:200] + "...",
                    "link": link
                }
            ] if most_relevant_doc else []

            return answer_with_citation, sources

        except Exception as e:
            logger.error(f"Error getting answer: {str(e)}")
            raise

    def _initialize_embeddings(self):
        """Initialize the embedding model."""
        logger.info("Initializing embedding model...")
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        # Test embeddings
        test_embedding = self._embeddings.embed_query("Test query")
        logger.info(f"Embedding test successful. Vector dimension: {len(test_embedding)}")

    def initialize_vector_store(self):
        """Load the existing vector store from disk."""
        logger.info("Starting vector store initialization...")
        logger.info(f"Loading vector store from: {VECTOR_STORE_PATH}")

        if not os.path.exists(VECTOR_STORE_PATH):
            logger.error(f"Vector store not found at {VECTOR_STORE_PATH}")
            raise FileNotFoundError(f"Vector store not found at {VECTOR_STORE_PATH}")

        try:
            logger.info("Loading Chroma vector store...")
            self._vector_store = Chroma(
                persist_directory=VECTOR_STORE_PATH,
                embedding_function=self._embeddings
            )
            logger.info("Chroma initialization successful")
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            raise
