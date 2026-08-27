"""MCP server wiring — registers the 4 Cloudberry-specific tools.

Thin on purpose: each tool opens a connection, delegates to queries.py for
the actual SQL/parsing, and closes the connection. All the logic worth unit
testing lives in queries.py against a mocked cursor (see ../tests/); this
module is exercised by talking MCP over stdio, not by a unit test.
"""

from mcp.server import MCPServer

from . import db, queries

mcp = MCPServer("cloudberry-segment-adapter")


@mcp.tool()
def list_segments() -> dict:
    """List Cloudberry segment configuration, flagging down or out-of-sync segments."""
    conn = db.get_connection()
    try:
        with conn.cursor() as cursor:
            return queries.list_segments(cursor)
    finally:
        conn.close()


@mcp.tool()
def get_distribution_policy(table_name: str) -> dict:
    """Return a table's Cloudberry distribution policy (replicated/random/hash-key)."""
    conn = db.get_connection()
    try:
        with conn.cursor() as cursor:
            return queries.get_distribution_policy(cursor, table_name)
    finally:
        conn.close()


@mcp.tool()
def check_data_skew(table_name: str) -> dict:
    """Report per-segment row counts for a table and flag over-loaded segments."""
    conn = db.get_connection()
    try:
        with conn.cursor() as cursor:
            return queries.check_data_skew(cursor, table_name)
    finally:
        conn.close()


@mcp.tool()
def explain_segment_aware(query: str) -> dict:
    """Run EXPLAIN on a query and pull out the Motion (redistribution) plan lines."""
    conn = db.get_connection()
    try:
        with conn.cursor() as cursor:
            return queries.explain_segment_aware(cursor, query)
    finally:
        conn.close()


def main():
    mcp.run()


if __name__ == "__main__":
    main()
