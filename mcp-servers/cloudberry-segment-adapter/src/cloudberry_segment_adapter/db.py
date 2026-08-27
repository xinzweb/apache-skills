"""Connection factory.

Reads DATABASE_URL, the same env-var convention T20260827-203753's survey
confirmed for mcp-alchemy / sql-alchemy-mcp / helloscoopa/mcp-postgres — a
user already running one of those alongside this adapter reuses the same
connection string.
"""

import os

import psycopg2
import psycopg2.extras


def get_connection(database_url=None):
    """Open a psycopg2 connection whose cursors return dict-shaped rows."""
    database_url = database_url or os.environ["DATABASE_URL"]
    return psycopg2.connect(database_url, cursor_factory=psycopg2.extras.RealDictCursor)
