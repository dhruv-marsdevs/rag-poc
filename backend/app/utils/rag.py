import os
import logging
from typing import List, Dict, Tuple, Any
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from dotenv import load_dotenv
from app.utils.vector_store import get_vector_store, query_vectorstore

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define the prompt template for generating answers
RAG_PROMPT_TEMPLATE = """You are a helpful assistant that answers questions based on the provided context. 
Your answers should be comprehensive yet concise, and you must only use information from the provided context.
If the context doesn't contain the answer, say "I don't have enough information to answer this question" rather than making up an answer.

For your reference, today's date is {date}.

Context:
{context}

Question: {question}

Answer (be concise and include relevant source citations in parentheses):"""


def get_llm():
    """
    Get the language model for generating answers
    """
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is required for the RAG functionality")

    # Use gpt-3.5-turbo by default, can be upgraded to gpt-4 for better performance
    return ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model="gpt-3.5-turbo",
        temperature=0,
    )


def format_documents(docs: List[Document]) -> str:
    """
    Format a list of documents into a string for the context

    Args:
        docs: List of Document objects

    Returns:
        Formatted string of documents with source information
    """
    formatted_docs = []

    for i, doc in enumerate(docs):
        # Format the source citation
        page_info = (
            f" (Page {doc.metadata.get('page')})" if doc.metadata.get("page") else ""
        )
        source = f"{doc.metadata.get('document', 'Unknown document')}{page_info}"

        # Add document with source citation
        formatted_docs.append(f"Document {i+1} [{source}]:\n{doc.page_content}\n")

    return "\n".join(formatted_docs)


def query_documents(query: str, top_k: int = 3) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Query documents and generate an answer with source citations

    Args:
        query: User query string
        top_k: Number of relevant documents to retrieve

    Returns:
        Tuple containing the answer and a list of source documents
    """
    try:
        # Query the vector store for relevant documents
        docs = query_vectorstore(query, top_k=top_k)

        if not docs:
            return "No relevant documents found to answer your question.", []

        # Format documents for context
        context = format_documents(docs)

        # Create a prompt with the context and query
        from datetime import datetime

        current_date = datetime.now().strftime("%Y-%m-%d")

        prompt = PromptTemplate(
            template=RAG_PROMPT_TEMPLATE,
            input_variables=["context", "question", "date"],
        )

        # Get the language model
        llm = get_llm()

        # Generate the answer
        chain = prompt | llm
        answer = chain.invoke(
            {"context": context, "question": query, "date": current_date}
        )

        # Extract the answer text (depends on OpenAI response format)
        answer_text = answer.content if hasattr(answer, "content") else str(answer)

        # Prepare source documents for the response
        sources = []
        for doc in docs:
            source = {
                "document": doc.metadata.get("document", "Unknown document"),
                "page": doc.metadata.get("page"),
                "text": doc.page_content,
            }
            sources.append(source)

        return answer_text, sources

    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        return f"An error occurred while processing your query: {str(e)}", []
