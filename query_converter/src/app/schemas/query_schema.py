from pydantic import BaseModel, Field, field_validator
from typing import Dict


class QueryRequest(BaseModel):
    query: str = Field(
        description="Query string to convert",
        example="Hostname=octoxlabs*",
        min_length=1,
        max_length=50,
    )

    @field_validator("query")
    @classmethod
    def validate_query_format(cls, v):
        if any(char in v for char in [";", "--", "/*", "*/"]):
            raise ValueError("Query contains invalid characters")

        field = v.split("=")[0].strip().lower()
        allowed_fields = {"hostname", "ip"}
        if field not in allowed_fields:
            raise ValueError(
                f"Invalid field name: {field}. Allowed fields are: {', '.join(allowed_fields)}"
            )
        return v


class QueryResponse(BaseModel):
    query: Dict = Field(description="Converted Elasticsearch query")
