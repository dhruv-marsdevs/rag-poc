from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.schemas.user import User
from app.schemas.document import QueryRequest, QueryResponse, SourceDocument
from app.services.rag_service import query_documents
from typing import List

router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def query(
    *,
    request: QueryRequest,
    current_user: User = Depends(deps.get_current_user_from_token_or_key),
):
    """
    Query documents using RAG.

    Retrieves relevant documents matching the query and generates an answer
    with source citations.
    """
    try:
        # Query documents with the user's ID to restrict access
        answer, sources = query_documents(
            query=request.query, top_k=request.top_k, user_id=current_user.id
        )

        # Format the sources for the response
        formatted_sources = []
        for source in sources:
            formatted_sources.append(
                SourceDocument(
                    page=source.get("page"),
                    document=source.get("document", ""),
                    text=source.get("text", ""),
                )
            )

        return QueryResponse(answer=answer, sources=formatted_sources)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying documents: {str(e)}",
        )
