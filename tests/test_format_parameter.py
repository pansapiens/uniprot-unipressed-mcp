"""Tests to verify the response_format parameter works correctly."""

import pytest


def test_response_format_parameter_validation():
    """Test that invalid response_format values are rejected."""
    from uniprot_mcp.server import _uniprot_search_impl, _uniprot_fetch_impl
    
    # Should raise ValueError for invalid format
    with pytest.raises(ValueError, match="Format must be"):
        _uniprot_search_impl(query="gene:BRCA1", response_format="invalid_format")
    
    with pytest.raises(ValueError, match="Format must be"):
        _uniprot_fetch_impl(ids=["P62988"], response_format="invalid_format")


def test_response_format_parameter_in_implementation():
    """Test that response_format parameter exists in implementation functions."""
    import inspect
    from uniprot_mcp.server import _uniprot_search_impl, _uniprot_fetch_impl
    
    # Check _uniprot_search_impl
    sig_search = inspect.signature(_uniprot_search_impl)
    assert "response_format" in sig_search.parameters, "response_format parameter missing from _uniprot_search_impl"
    
    # Check _uniprot_fetch_impl
    sig_fetch = inspect.signature(_uniprot_fetch_impl)
    assert "response_format" in sig_fetch.parameters, "response_format parameter missing from _uniprot_fetch_impl"
    
    # Verify default value
    assert sig_search.parameters["response_format"].default == "toon"
    assert sig_fetch.parameters["response_format"].default == "toon"
