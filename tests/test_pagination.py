"""Tests for pagination utilities."""

import pytest

from uniprot_mcp.pagination import decode_cursor, encode_cursor, paginate_results


class TestCursorEncoding:
    """Tests for cursor encoding and decoding."""

    def test_encode_decode_roundtrip(self):
        """Encoding then decoding should return the original offset."""
        for offset in [0, 1, 10, 100, 1000]:
            cursor = encode_cursor(offset)
            decoded = decode_cursor(cursor)
            assert decoded == offset

    def test_encode_produces_string(self):
        """Encoded cursor should be a string."""
        cursor = encode_cursor(42)
        assert isinstance(cursor, str)
        assert len(cursor) > 0

    def test_decode_invalid_cursor_raises(self):
        """Decoding an invalid cursor should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid cursor"):
            decode_cursor("not-a-valid-cursor!!!")

    def test_decode_wrong_json_structure_raises(self):
        """Decoding a cursor without 'offset' field should raise."""
        import base64
        import json

        bad_cursor = base64.urlsafe_b64encode(
            json.dumps({"wrong": "field"}).encode()
        ).decode()
        with pytest.raises(ValueError, match="missing 'offset'"):
            decode_cursor(bad_cursor)

    def test_decode_negative_offset_raises(self):
        """Decoding a cursor with negative offset should raise."""
        import base64
        import json

        bad_cursor = base64.urlsafe_b64encode(
            json.dumps({"offset": -5}).encode()
        ).decode()
        with pytest.raises(ValueError, match="Invalid offset"):
            decode_cursor(bad_cursor)


class TestPaginateResults:
    """Tests for paginate_results function."""

    def test_empty_results(self):
        """Empty results should return empty array with no cursor."""
        response = paginate_results([], offset=0, limit=10)
        assert response["results"] == []
        assert "nextCursor" not in response

    def test_partial_page_no_next_cursor(self):
        """Partial page should not have nextCursor."""
        results = [{"id": i} for i in range(5)]
        response = paginate_results(results, offset=0, limit=10)
        assert len(response["results"]) == 5
        assert "nextCursor" not in response

    def test_full_page_has_next_cursor(self):
        """Full page should have nextCursor."""
        results = [{"id": i} for i in range(10)]
        response = paginate_results(results, offset=0, limit=10)
        assert len(response["results"]) == 10
        assert "nextCursor" in response

    def test_next_cursor_decodes_to_correct_offset(self):
        """nextCursor should decode to offset + limit."""
        results = [{"id": i} for i in range(10)]
        response = paginate_results(results, offset=20, limit=10)
        next_offset = decode_cursor(response["nextCursor"])
        assert next_offset == 30

    def test_total_included_when_provided(self):
        """Total should be included when available."""
        results = [{"id": i} for i in range(5)]
        response = paginate_results(results, offset=0, limit=10, total_available=100)
        assert response["total"] == 100

    def test_no_next_cursor_at_end_of_results(self):
        """No nextCursor when we've reached the end."""
        results = [{"id": i} for i in range(10)]
        # At offset 90 with limit 10, and total 100, we're at the end
        response = paginate_results(results, offset=90, limit=10, total_available=100)
        assert "nextCursor" not in response

