from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import LiteralString, cast

from fastapi import Request
from neo4j import Driver, GraphDatabase, Query
from neo4j.exceptions import Neo4jError
from slowapi import Limiter
from slowapi.util import get_remote_address

from palimpsest.utils.config import settings

logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit],
)


def create_neo4j_driver() -> Driver:
    """Create a Neo4j driver with connection pooling.

    Returns:
        Neo4j driver instance.
    """

    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
        max_connection_pool_size=50,
        connection_timeout=10.0,
    )


def get_neo4j_driver(request: Request) -> Driver:
    """Get shared Neo4j driver from FastAPI application state.

    Args:
        request: FastAPI request object.

    Returns:
        Shared Neo4j driver.
    """

    return cast(Driver, request.app.state.neo4j_driver)


def run_query(
    driver: Driver,
    cypher: LiteralString,
    parameters: Mapping[str, object],
    timeout_seconds: float = 120.0,
) -> Sequence[dict[str, object]]:
    """Execute a read query and return records as dictionaries.

    Args:
        driver: Shared Neo4j driver.
        cypher: Parameterized Cypher query text.
        parameters: Cypher parameters.
        timeout_seconds: Query timeout in seconds.

    Returns:
        Query result records as dictionaries.

    Raises:
        Neo4jError: If query execution fails.
    """

    query = Query(text=cypher, timeout=timeout_seconds)
    with driver.session(database="neo4j") as session:
        result = session.run(query, dict(parameters))
        return [record.data() for record in result]


def check_neo4j_connectivity(driver: Driver) -> bool:
    """Check whether Neo4j is reachable.

    Args:
        driver: Shared Neo4j driver.

    Returns:
        True if connected, False otherwise.
    """

    try:
        driver.verify_connectivity()
    except Neo4jError:
        return False
    return True
