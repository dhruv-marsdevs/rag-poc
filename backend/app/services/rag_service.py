import os
import logging
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
import random

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document

from app.core.config import get_settings
from app.services.vector_store_service import query_vectorstore

settings = get_settings()
logger = logging.getLogger(__name__)

# Define the prompt template for generating answers
RAG_PROMPT_TEMPLATE = """
As a knowledge-bound assistant, adhere strictly to these rules:

Context-Only Responses

Base answers exclusively on the provided context. Never rely on prior knowledge or assumptions.

If the context is insufficient, explicitly state: "I don’t have sufficient context to address this."

Precision & Transparency

Acknowledge ambiguities/conflicts in the context (e.g., "The context suggests two possibilities...").

For partial answers, specify limitations (e.g., "The context only mentions X, but doesn’t cover Y").

Anti-Hallucination Safeguards

Never invent: names, dates, statistics, or domain-specific facts absent from the context.

Reject speculative phrasing like "probably," "likely," or "it’s possible that" unless explicitly stated.

Response Structure

Prioritize clarity over brevity. Use bullet points or numbered lists for multi-part answers.

Begin with a direct answer, followed by context-supported details.

Edge Case Handling

If the query is out of scope or nonsensical, respond: "Could you clarify or provide additional context?"

For ethically questionable requests, decline politely without elaboration.

For your reference, today's date is {date}.

Context:
{context}

Question: {question}

Answer (be detailed and include relevant source citations in parentheses):"""


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=5),
)
def get_llm():
    """
    Get the language model for generating answers.
    Uses retry logic for better resilience.
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OpenAI API key is required for the RAG functionality")

    # Use the model specified in settings
    return ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
    )


def format_documents(docs: List[Document]) -> str:
    """
    Format a list of documents into a string for the context.

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


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=5),
)
def query_documents(
    query: str, top_k: int = 3, user_id: Optional[str] = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Query documents and generate an answer with source citations.
    Uses retry logic for better resilience.

    Args:
        query: User query string
        top_k: Number of relevant documents to retrieve
        user_id: Optional user ID to filter results

    Returns:
        Tuple containing the answer and a list of source documents
    """
    try:
        # Query the vector store for relevant documents, optionally filtering by user_id
        docs = query_vectorstore(query, top_k=top_k, user_id=user_id)

        if not docs:
            return "No relevant documents found to answer your question.", []

        # Format documents for context
        context = format_documents(docs)

        # Create a prompt with the context and query
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

        # Extract the answer text
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

        # Log successful query
        logger.info(
            f"Query successful: '{query}' - found {len(docs)} relevant documents"
        )
        return answer_text, sources

    except Exception as e:
        logger.error(f"Error in RAG query: {str(e)}", exc_info=True)
        raise


def get_query_stats() -> Dict[str, Any]:
    """
    Get query statistics for the dashboard.
    
    In a production system, you would track these metrics in a database.
    For now, we'll return reasonable mock values.
    
    Returns:
        Dict with stats like query count, response times, etc.
    """
    # In a real system, you'd query a database for this data
    # For example:
    # today_count = db.query(func.count(Query.id)).filter(
    #     Query.created_at >= datetime.utcnow().date()
    # ).scalar() or 0
    
    # For now, we'll use mock data
    
    # Get current hour to make the stats somewhat realistic during the day
    current_hour = datetime.utcnow().hour
    activity_factor = max(0.1, min(current_hour / 24.0, 0.9))  # Between 0.1 and 0.9 based on time of day
    
    # Calculate stats with some randomness but within realistic ranges
    today_count = int(10 * activity_factor + random.randint(0, 5))
    active_users = max(1, int(5 * activity_factor + random.randint(0, 3)))
    
    # Response time between 0.2 and 0.8 seconds
    avg_response_time = 0.2 + 0.6 * activity_factor + random.random() * 0.2
    
    return {
        "today_count": today_count,
        "active_users": active_users,
        "avg_response_time": round(avg_response_time, 2)
    }
