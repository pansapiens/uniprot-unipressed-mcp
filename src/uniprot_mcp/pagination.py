"""Cursor-based pagination utilities for UniProt MCP server."""

import base64
import json
from typing import Any


def encode_cursor(offset: int) -> str:
    """
    Encode pagination state into an opaque cursor string.

    Args:
        offset: The current offset position in the result set.

    Returns:
        A base64-encoded cursor string.
    """
    cursor_data = {"offset": offset}
    json_bytes = json.dumps(cursor_data).encode("utf-8")
    return base64.urlsafe_b64encode(json_bytes).decode("ascii")


def decode_cursor(cursor: str) -> int:
    """
    Decode an opaque cursor string back to pagination state.

    Args:
        cursor: The base64-encoded cursor string.

    Returns:
        The offset position encoded in the cursor.

    Raises:
        ValueError: If the cursor is invalid or malformed.
    """
    try:
        json_bytes = base64.urlsafe_b64decode(cursor.encode("ascii"))
        cursor_data = json.loads(json_bytes.decode("utf-8"))
        if "offset" not in cursor_data:
            raise ValueError("Cursor missing 'offset' field")
        offset = cursor_data["offset"]
        if not isinstance(offset, int) or offset < 0:
            raise ValueError("Invalid offset value in cursor")
        return offset
    except (json.JSONDecodeError, UnicodeDecodeError, base64.binascii.Error) as e:
        raise ValueError(f"Invalid cursor format: {e}") from e


def paginate_results(
    results: list[dict[str, Any]],
    offset: int,
    limit: int,
    total_available: int | None = None,
) -> dict[str, Any]:
    """
    Create a paginated response with results and optional next cursor.

    Args:
        results: The list of results for the current page.
        offset: The current offset position.
        limit: The page size limit.
        total_available: The total number of results available (if known).

    Returns:
        A dictionary with 'results', optional 'total', and optional 'nextCursor'.
    """
    response: dict[str, Any] = {"results": results}

    if total_available is not None:
        response["total"] = total_available

    # If we got a full page of results, there might be more
    if len(results) == limit:
        next_offset = offset + limit
        # Only add nextCursor if we haven't reached the end
        if total_available is None or next_offset < total_available:
            response["nextCursor"] = encode_cursor(next_offset)

    return response

