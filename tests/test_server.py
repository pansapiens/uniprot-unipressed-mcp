"""Tests for MCP server tools."""

import os
from typing import Any

import pytest

from uniprot_mcp.server import _uniprot_search_impl, _uniprot_fetch_impl

# Skip integration tests unless RUN_INTEGRATION_TESTS environment variable is set
skip_integration = pytest.mark.skipif(
    not os.getenv("RUN_INTEGRATION_TESTS"),
    reason="Integration tests require network access. Set RUN_INTEGRATION_TESTS=1 to run them.",
)


class TestUniprotSearchValidation:
    """Tests for uniprot_search input validation."""

    def test_empty_query_raises(self):
        """Empty query should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            _uniprot_search_impl(query="")

    def test_whitespace_query_raises(self):
        """Whitespace-only query should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            _uniprot_search_impl(query="   ")

    def test_invalid_database_raises(self):
        """Invalid database should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid database"):
            _uniprot_search_impl(query="gene:BRCA1", database="invalid")

    def test_limit_too_low_raises(self):
        """Limit below 1 should raise ValueError."""
        with pytest.raises(ValueError, match="between 1 and 100"):
            _uniprot_search_impl(query="gene:BRCA1", limit=0)

    def test_limit_too_high_raises(self):
        """Limit above 100 should raise ValueError."""
        with pytest.raises(ValueError, match="between 1 and 100"):
            _uniprot_search_impl(query="gene:BRCA1", limit=101)

    def test_invalid_cursor_raises(self):
        """Invalid cursor should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid cursor"):
            _uniprot_search_impl(query="gene:BRCA1", cursor="bad-cursor!!!")
    
    def test_invalid_format_raises(self):
        """Invalid format should raise ValueError."""
        with pytest.raises(ValueError, match="Format must be"):
            _uniprot_search_impl(query="gene:BRCA1", response_format="invalid")


class TestUniprotFetchValidation:
    """Tests for uniprot_fetch input validation."""

    def test_empty_ids_raises(self):
        """Empty IDs list should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            _uniprot_fetch_impl(ids=[])

    def test_whitespace_only_ids_raises(self):
        """List with only whitespace IDs should raise ValueError."""
        with pytest.raises(ValueError, match="No valid IDs"):
            _uniprot_fetch_impl(ids=["", "   "])

    def test_invalid_database_raises(self):
        """Invalid database should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid database"):
            _uniprot_fetch_impl(ids=["P62988"], database="invalid")
    
    def test_invalid_format_raises(self):
        """Invalid format should raise ValueError."""
        with pytest.raises(ValueError, match="Format must be"):
            _uniprot_fetch_impl(ids=["P62988"], response_format="invalid")


class TestUniprotSearchIntegration:
    """Integration tests for uniprot_search (requires network)."""

    @pytest.mark.integration
    @skip_integration
    def test_basic_search(self):
        """Basic search should return results."""
        result = _uniprot_search_impl(query="gene:BRCA1 AND organism_id:9606", limit=5, response_format="json")
        assert isinstance(result, dict)
        assert "results" in result
        assert isinstance(result["results"], list)
        assert len(result["results"]) <= 5

    @pytest.mark.integration
    @skip_integration
    def test_search_with_fields(self):
        """Search with specific fields should limit returned data."""
        result = _uniprot_search_impl(
            query="accession:P62988",
            fields=["accession", "gene_names"],
            limit=1,
            response_format="json",
        )
        assert isinstance(result, dict)
        assert "results" in result
        if result["results"]:
            entry = result["results"][0]
            # Should have the requested fields
            assert "primaryAccession" in entry or "accession" in entry


class TestUniprotFetchIntegration:
    """Integration tests for uniprot_fetch (requires network)."""

    @pytest.mark.integration
    @skip_integration
    def test_fetch_single_id(self):
        """Fetching a single ID should return one result."""
        result = _uniprot_fetch_impl(ids=["P62988"], response_format="json")
        assert isinstance(result, dict)
        assert "results" in result
        assert result["found"] == 1
        assert result["requested"] == 1

    @pytest.mark.integration
    @skip_integration
    def test_fetch_multiple_ids(self):
        """Fetching multiple IDs should return multiple results."""
        result = _uniprot_fetch_impl(ids=["A0A0C5B5G6", "A0A1B0GTW7"], response_format="json")
        assert isinstance(result, dict)
        assert "results" in result
        assert result["requested"] == 2
        assert result["found"] <= 2

    @pytest.mark.integration
    @skip_integration
    def test_fetch_nonexistent_id(self):
        """Fetching nonexistent ID should return empty results."""
        result = _uniprot_fetch_impl(ids=["NOTREAL123"], response_format="json")
        assert isinstance(result, dict)
        assert result["found"] == 0
        assert result["requested"] == 1

