from rest_framework import serializers

class SearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    
    def validate_query(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Query cannot be empty")
        return value

class SearchResultSerializer(serializers.Serializer):
    Hostname = serializers.CharField()
    Ip = serializers.ListField(child=serializers.CharField()) 