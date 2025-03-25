from rest_framework import serializers


class SearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=True, max_length=50)

    def validate_query(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Query cannot be empty")

        # Check minimum length
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Query must be at least 3 characters long"
            )

        # Check for SQL injection patterns
        sql_patterns = [
            ";",
            "--",
            "/*",
            "*/",
            "union",
            "select",
            "drop",
            "delete",
            "update",
            "insert",
            "exec",
            "execute",
            "declare",
            "create",
        ]
        value_lower = value.lower()
        for pattern in sql_patterns:
            if pattern in value_lower:
                raise serializers.ValidationError(
                    f"Query contains forbidden pattern: {pattern}"
                )

        field = value.split("=")[0].strip().lower()
        allowed_fields = {"hostname", "ip"}
        if field not in allowed_fields:
            raise serializers.ValidationError(
                f"Invalid field name: {field}. Allowed fields are: {', '.join(allowed_fields)}"
            )

        return value


class SearchResultSerializer(serializers.Serializer):
    Hostname = serializers.CharField()
    Ip = serializers.ListField(child=serializers.CharField())
