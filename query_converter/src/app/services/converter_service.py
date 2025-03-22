import re
from loguru import logger


class ConverterService:
    
    def convert_query(self, query_string):
        """
        Convert a simple query string to Elasticsearch query DSL
        
        Example:
        "Hostname = octoxlabs*" -> {"wildcard": {"Hostname": "octoxlabs*"}}
        """
        logger.info(f"Converting query: {query_string}")
        
        # Simple parser for "field = value" format
        pattern = r'(\w+)\s*=\s*(.+)'
        match = re.match(pattern, query_string.strip())
        
        if not match:
            logger.error(f"Invalid query format: {query_string}")
            raise ValueError(f"Invalid query format: {query_string}")
        
        field, value = match.groups()
        value = value.strip()
        logger.debug(f"Parsed field: {field}, value: {value}")
        
        # Determine query type based on value pattern
        if '*' in value:
            logger.debug("Using wildcard query")
            result = {
                "wildcard": {
                    f"{field}": value
                }
            }
        elif value.startswith('/') and value.endswith('/'):
            # Regex query
            regex_pattern = value[1:-1]
            logger.debug(f"Using regex query with pattern: {regex_pattern}")
            result = {
                "regexp": {
                    f"{field}": regex_pattern
                }
            }
        else:
            # Term query for exact match
            logger.debug("Using term query for exact match")
            result = {
                "term": {
                    f"{field}": value
                }
            }
            
        logger.info(f"Successfully converted query to: {result}")
        return result