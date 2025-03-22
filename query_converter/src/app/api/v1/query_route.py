from fastapi import APIRouter, HTTPException, Depends

from ...schemas.query_schema import QueryRequest, QueryResponse
from ...services.converter_service import ConverterService
from ...api.dependencies import get_converter_service


router = APIRouter(tags=["Query"])

@router.post("/convert", 
    response_model=QueryResponse,
    status_code=200,
    summary="Convert a query to Elasticsearch format",
    description="Convert a query to Elasticsearch format"
)
async def convert(
    request: QueryRequest, 
    converter_service: ConverterService = Depends(get_converter_service)
):
    """
    Convert a query string to Elasticsearch format
    
    Parameters:
    - **query**: Query string to convert (e.g., "Hostname=octoxlabs*")
    
    Returns:
    - Converted Elasticsearch query
    """
    try:
        es_query = converter_service.convert_query(request.query)
        return QueryResponse(query=es_query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query conversion failed: {str(e)}")
