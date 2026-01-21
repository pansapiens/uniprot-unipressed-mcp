"""Client factory for selecting the appropriate UniProt database client."""

from typing import Literal

from unipressed import UniprotkbClient, UniparcClient, UnirefClient

DatabaseType = Literal["uniprotkb", "uniparc", "uniref"]

VALID_DATABASES: set[DatabaseType] = {"uniprotkb", "uniparc", "uniref"}

# Map database names to their client classes
CLIENT_MAP = {
    "uniprotkb": UniprotkbClient,
    "uniparc": UniparcClient,
    "uniref": UnirefClient,
}


def get_client(database: DatabaseType):
    """
    Get the appropriate unipressed client for the specified database.

    Args:
        database: The UniProt database to query. One of: uniprotkb, uniparc, uniref

    Returns:
        The client class for the specified database.

    Raises:
        ValueError: If the database is not supported.
    """
    if database not in VALID_DATABASES:
        raise ValueError(
            f"Invalid database '{database}'. Must be one of: {', '.join(VALID_DATABASES)}"
        )
    return CLIENT_MAP[database]


def validate_database(database: str) -> DatabaseType:
    """
    Validate and normalise the database parameter.

    Args:
        database: The database name to validate.

    Returns:
        The validated database name as a DatabaseType.

    Raises:
        ValueError: If the database is not supported.
    """
    db_lower = database.lower()
    if db_lower not in VALID_DATABASES:
        raise ValueError(
            f"Invalid database '{database}'. Must be one of: {', '.join(VALID_DATABASES)}"
        )
    return db_lower  # type: ignore

