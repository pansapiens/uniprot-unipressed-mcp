"""Tests for client factory."""

import pytest

from unipressed import UniprotkbClient, UniparcClient, UnirefClient

from uniprot_mcp.clients import get_client, validate_database, VALID_DATABASES


class TestGetClient:
    """Tests for get_client function."""

    def test_get_uniprotkb_client(self):
        """Should return UniprotkbClient for 'uniprotkb'."""
        client = get_client("uniprotkb")
        assert client is UniprotkbClient

    def test_get_uniparc_client(self):
        """Should return UniparcClient for 'uniparc'."""
        client = get_client("uniparc")
        assert client is UniparcClient

    def test_get_uniref_client(self):
        """Should return UnirefClient for 'uniref'."""
        client = get_client("uniref")
        assert client is UnirefClient

    def test_invalid_database_raises(self):
        """Should raise ValueError for invalid database."""
        with pytest.raises(ValueError, match="Invalid database"):
            get_client("invalid")


class TestValidateDatabase:
    """Tests for validate_database function."""

    def test_valid_databases(self):
        """Should accept all valid database names."""
        for db in VALID_DATABASES:
            result = validate_database(db)
            assert result == db

    def test_case_insensitive(self):
        """Should be case-insensitive."""
        assert validate_database("UniProtKB") == "uniprotkb"
        assert validate_database("UNIPARC") == "uniparc"
        assert validate_database("UniRef") == "uniref"

    def test_invalid_raises(self):
        """Should raise ValueError for invalid database."""
        with pytest.raises(ValueError, match="Invalid database"):
            validate_database("notadb")


class TestValidDatabases:
    """Tests for VALID_DATABASES constant."""

    def test_contains_expected_databases(self):
        """Should contain all three expected databases."""
        assert "uniprotkb" in VALID_DATABASES
        assert "uniparc" in VALID_DATABASES
        assert "uniref" in VALID_DATABASES
        assert len(VALID_DATABASES) == 3

