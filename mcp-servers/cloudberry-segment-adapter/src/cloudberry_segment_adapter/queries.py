"""SQL and row-shaping for the Cloudberry-specific tools.

Cursor-only: every function takes a DB-API cursor (a psycopg2
``RealDictCursor``-shaped cursor — rows come back as dicts) and returns
plain Python data. No MCP or network code lives here, which is what makes
these functions testable against a mocked cursor with no live database
(see ../tests/test_queries.py).

Column names verified against Apache Cloudberry's own docs (2026-08-27):
- gp_segment_configuration: https://cloudberry.apache.org/docs/sys-catalogs/sys-tables/gp-segment-configuration/
- gp_distribution_policy: https://cloudberry.apache.org/docs/sys-catalogs/sys-tables/gp-distribution-policy/
"""

import re

# gp_segment_configuration.status: 'u' = up, 'd' = down.
# gp_segment_configuration.mode:   's' = synchronized, 'n' = not in sync.
LIST_SEGMENTS_SQL = """\
SELECT dbid, content, role, preferred_role, mode, status, hostname, address, port
FROM gp_segment_configuration
ORDER BY content, role
"""

# distkey is an int2vector of pg_attribute.attnum; unnest + join resolves it
# to column names. An empty distkey_columns array with policytype='p' means
# DISTRIBUTED RANDOMLY (the docs don't spell this out explicitly — it
# follows from distkey having nothing to name).
DISTRIBUTION_POLICY_SQL = """\
SELECT
    c.relname,
    p.policytype,
    p.numsegments,
    COALESCE(
        (SELECT array_agg(a.attname ORDER BY k.ord)
         FROM unnest(p.distkey) WITH ORDINALITY AS k(attnum, ord)
         JOIN pg_attribute a ON a.attrelid = p.localoid AND a.attnum = k.attnum),
        ARRAY[]::text[]
    ) AS distkey_columns
FROM gp_distribution_policy p
JOIN pg_class c ON c.oid = p.localoid
WHERE c.relname = %s
"""

# {table} is filled with an already-validated, double-quoted identifier by
# check_data_skew() below — never with a raw caller-supplied string.
DATA_SKEW_SQL_TEMPLATE = (
    "SELECT gp_segment_id, count(*) AS row_count FROM {table}"
    " GROUP BY gp_segment_id ORDER BY gp_segment_id"
)

# Default skew threshold: a segment whose row count deviates from the mean
# by more than this fraction is flagged. This is this tool's own heuristic,
# not an official Cloudberry number.
DEFAULT_SKEW_THRESHOLD = 0.10

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _quote_identifier(name):
    """Validate a plain SQL identifier and double-quote it.

    Deliberately restrictive (word characters only, must start with a
    letter/underscore) rather than using psycopg2.sql.Identifier, so the
    resulting SQL is a plain string usable without a live connection —
    including in unit tests. Anything outside that character set is
    rejected rather than escaped.
    """
    if not _IDENTIFIER_RE.match(name):
        raise ValueError(f"invalid table name: {name!r}")
    return f'"{name}"'


def list_segments(cursor):
    """Return every segment's config, flagging down or out-of-sync rows."""
    cursor.execute(LIST_SEGMENTS_SQL)
    rows = cursor.fetchall()
    return {
        "segments": rows,
        "down": [r for r in rows if r["status"] == "d"],
        "unsynced": [r for r in rows if r["mode"] == "n"],
    }


def get_distribution_policy(cursor, table_name):
    """Return the distribution policy for table_name as a human label."""
    cursor.execute(DISTRIBUTION_POLICY_SQL, (table_name,))
    row = cursor.fetchone()
    if row is None:
        raise ValueError(f"no distribution policy found for table {table_name!r}")

    if row["policytype"] == "r":
        distribution = "REPLICATED"
    elif row["distkey_columns"]:
        distribution = f"HASH({', '.join(row['distkey_columns'])})"
    else:
        distribution = "RANDOM"

    return {
        "table": table_name,
        "policy_type": row["policytype"],
        "numsegments": row["numsegments"],
        "distribution": distribution,
    }


def check_data_skew(cursor, table_name, skew_threshold=DEFAULT_SKEW_THRESHOLD):
    """Return per-segment row counts for table_name, flagging skew."""
    quoted = _quote_identifier(table_name)
    cursor.execute(DATA_SKEW_SQL_TEMPLATE.format(table=quoted))
    rows = cursor.fetchall()

    if not rows:
        return {"segments": rows, "skewed": False, "skewed_segments": []}

    mean = sum(r["row_count"] for r in rows) / len(rows)
    # Flag only over-loaded segments (row_count above the mean by more than
    # the threshold), not under-loaded ones: an MPP cluster's response time
    # is bounded by its busiest segment (see Cloudberry's own Distribution
    # and Skew docs), so that's the direction that actually matters.
    # Comparing every segment to the whole-set mean (rather than the mean of
    # the *other* segments) means one outlier does pull the cutoff up a
    # little, but stays a defensible tool-chosen heuristic, not a bug.
    skewed_segments = [
        r for r in rows
        if mean > 0 and r["row_count"] > mean * (1 + skew_threshold)
    ]
    return {
        "segments": rows,
        "skewed": bool(skewed_segments),
        "skewed_segments": skewed_segments,
    }


def explain_segment_aware(cursor, query):
    """Run EXPLAIN on query, pulling out the Motion (redistribution) lines.

    query is caller-supplied and executed as-is inside EXPLAIN — the same
    trust model as every surveyed server's execute_sql/explain_query tools
    (see T20260827-203753's Findings); this tool doesn't widen that
    boundary, it just runs EXPLAIN instead of the raw query.
    """
    cursor.execute(f"EXPLAIN {query}")
    rows = cursor.fetchall()
    plan_lines = [row["QUERY PLAN"] for row in rows]
    return {
        "plan": "\n".join(plan_lines),
        "motion_lines": [line for line in plan_lines if "Motion" in line],
    }
