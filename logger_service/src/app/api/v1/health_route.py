from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health",
    summary="Health Check",
    description="Check if the API is up and running",
    response_description="Returns the health status of the API"
)
async def health_check():
    """
    Perform a health check of the API
    
    Returns:
    - Health status of the API
    """
    return {"status": "healthy"}