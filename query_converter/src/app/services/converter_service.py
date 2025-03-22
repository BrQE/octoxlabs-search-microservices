import re


class ConverterService:
    
    def convert_query(self, query_string):
        """
        Convert a simple query string to Elasticsearch query DSL
        
        Example:
        "Hostname = octoxlabs*" -> {"wildcard": {"Hostname.keyword": "octoxlabs*"}}
        """
        # Simple parser for "field = value" format
        pattern = r'(\w+)\s*=\s*(.+)'
        match = re.match(pattern, query_string.strip())
        
        if not match:
            raise ValueError(f"Invalid query format: {query_string}")
        
        field, value = match.groups()
        value = value.strip()
        
        # Determine query type based on value pattern
        if '*' in value:
            return {
                "wildcard": {
                    f"{field}": value
                }
            }
        elif value.startswith('/') and value.endswith('/'):
            # Regex query
            regex_pattern = value[1:-1]
            return {
                "regexp": {
                    f"{field}": regex_pattern
                }
            }
        else:
            # Term query for exact match
            return {
                "term": {
                    f"{field}": value
                }
            }