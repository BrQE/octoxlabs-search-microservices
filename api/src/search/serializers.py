from rest_framework import serializers

class SearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    
    def validate_query(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Query cannot be empty")

        if any(char in value for char in [';', '--', '/*', '*/']):
            raise serializers.ValidationError("Query contains invalid characters")

        field = value.split('=')[0].strip().lower()
        allowed_fields = {'hostname', 'ip'}
        if field not in allowed_fields:
            raise serializers.ValidationError(f"Invalid field name: {field}. Allowed fields are: {', '.join(allowed_fields)}")

        return value

class SearchResultSerializer(serializers.Serializer):
    Hostname = serializers.CharField()
    Ip = serializers.ListField(child=serializers.CharField()) 