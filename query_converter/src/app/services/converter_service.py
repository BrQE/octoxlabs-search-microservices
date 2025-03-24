from typing import Dict, Any
import re
from loguru import logger


class QueryType:
    """Constants for different query types."""

    WILDCARD = "wildcard"
    REGEXP = "regexp"
    TERM = "term"


class ConverterService:
    """Service for converting simple query strings to Elasticsearch query DSL."""

    def convert_query(self, query_string: str) -> Dict[str, Any]:
        """
        Convert a simple query string to Elasticsearch query DSL.

        Args:
            query_string (str): Query string in format "field = value"
                              Supports wildcard (*) and regex (/) patterns.

        Returns:
            Dict[str, Any]: Elasticsearch query DSL

        Raises:
            ValueError: If query format is invalid or empty

        Examples:
            >>> converter = ConverterService()
            >>> converter.convert_query("Hostname = octoxlabs*")
            {"wildcard": {"Hostname": "octoxlabs*"}}
            >>> converter.convert_query("IP = /192\.168\.1\.*/")
            {"regexp": {"IP": "192\.168\.1\.*"}}
            >>> converter.convert_query("Status = active")
            {"term": {"Status": "active"}}
        """
        if not query_string or not isinstance(query_string, str):
            raise ValueError("Query string must be a non-empty string")

        logger.info(f"Converting query: {query_string}")

        # Simple parser for "field = value" format
        pattern = r"(\w+)\s*=\s*(.+)"
        match = re.match(pattern, query_string.strip())

        if not match:
            logger.error(f"Invalid query format: {query_string}")
            raise ValueError(f"Invalid query format: {query_string}")

        field, value = match.groups()
        value = value.strip()
        logger.debug(f"Parsed field: {field}, value: {value}")

        result = self._create_query(field, value)
        logger.info(f"Successfully converted query to: {result}")
        return result

    def _create_query(self, field: str, value: str) -> Dict[str, Any]:
        """
        Create appropriate Elasticsearch query based on value pattern.

        Args:
            field (str): Field name
            value (str): Field value

        Returns:
            Dict[str, Any]: Elasticsearch query DSL
        """
        if "*" in value:
            logger.debug("Using wildcard query")
            return {QueryType.WILDCARD: {field: value}}
        elif value.startswith("/") and value.endswith("/"):
            # Regex query
            regex_pattern = value[1:-1]
            logger.debug(f"Using regex query with pattern: {regex_pattern}")
            return {QueryType.REGEXP: {field: regex_pattern}}
        else:
            # Term query for exact match
            logger.debug("Using term query for exact match")
            return {QueryType.TERM: {field: value}}
