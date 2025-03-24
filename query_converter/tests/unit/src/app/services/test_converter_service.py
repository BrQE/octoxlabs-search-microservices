import pytest

from src.app.services.converter_service import ConverterService, QueryType


class TestConverterService:
    def setup_method(self):
        self.converter = ConverterService()

    def test_convert_wildcard_query(self):
        query = "Hostname = octoxlabs*"
        expected = {QueryType.WILDCARD: {"Hostname": "octoxlabs*"}}
        result = self.converter.convert_query(query)
        assert result == expected

    def test_convert_regex_query(self):
        query = "Hostname = /octoxlabs./"
        expected = {QueryType.REGEXP: {"Hostname": "octoxlabs."}}
        result = self.converter.convert_query(query)
        assert result == expected

    def test_convert_term_query(self):
        query = "Hostname = octoxlabs"
        expected = {QueryType.TERM: {"Hostname": "octoxlabs"}}
        result = self.converter.convert_query(query)
        assert result == expected

    def test_convert_query_with_spaces(self):
        query = "Hostname  =  octoxlabs"
        expected = {QueryType.TERM: {"Hostname": "octoxlabs"}}
        result = self.converter.convert_query(query)
        assert result == expected

    def test_invalid_query_format(self):
        query = "invalid query format"
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_query(query)
        assert "Invalid query format" in str(exc_info.value)

    def test_empty_query(self):
        query = ""
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_query(query)
        assert "Query string must be a non-empty string" in str(exc_info.value)

    def test_query_without_equals(self):
        query = "Hostname octoxlabs"
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_query(query)
        assert "Invalid query format" in str(exc_info.value)

    def test_non_string_query(self):
        query = None
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_query(query)
        assert "Query string must be a non-empty string" in str(exc_info.value)

    def test_query_with_special_characters(self):
        query = "IP = /192\.168\.1\./"
        expected = {QueryType.REGEXP: {"IP": "192\.168\.1\.*"}}
        result = self.converter.convert_query(query)
        assert result == expected

    def test_query_with_multiple_wildcards(self):
        query = "Domain = *.example.*"
        expected = {QueryType.WILDCARD: {"Domain": "*.example.*"}}
        result = self.converter.convert_query(query)
        assert result == expected
