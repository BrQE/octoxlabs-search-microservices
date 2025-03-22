from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(
        description="Query string to convert",
        example="Hostname=octoxlabs*"
    )

class QueryResponse(BaseModel):
    query: dict = Field(
        description="Converted Elasticsearch query"
    )