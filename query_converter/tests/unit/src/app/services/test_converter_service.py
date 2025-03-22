import pytest

from src.app.services.converter_service import ConverterService


class TestConverterService:
    def setup_method(self):
        self.converter = ConverterService()

    def test_convert_wildcard_query(self):
        query = "Hostname = octoxlabs*"
        expected = {
            "wildcard": {
                "Hostname": "octoxlabs*"
            }
        }
        result = self.converter.convert_query(query)
        assert result == expected

    def test_convert_regex_query(self):
        query = "Hostname = /octoxlabs.*/"
        expected = {
            "regexp": {
                "Hostname": "octoxlabs.*"
            }
        }
        result = self.converter.convert_query(query)
        assert result == expected

    def test_convert_term_query(self):
        query = "Hostname = octoxlabs"
        expected = {
            "term": {
                "Hostname": "octoxlabs"
            }
        }
        result = self.converter.convert_query(query)
        assert result == expected

    def test_convert_query_with_spaces(self):
        query = "Hostname  =  octoxlabs"
        expected = {
            "term": {
                "Hostname": "octoxlabs"
            }
        }
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
        assert "Invalid query format" in str(exc_info.value)

    def test_query_without_equals(self):
        query = "Hostname octoxlabs"
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_query(query)
        assert "Invalid query format" in str(exc_info.value)
