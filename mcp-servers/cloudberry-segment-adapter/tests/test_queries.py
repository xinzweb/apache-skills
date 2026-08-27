"""Unit tests for cloudberry_segment_adapter.queries.

No live Cloudberry cluster is available in this environment, so every test
mocks a psycopg2 RealDictCursor-shaped cursor (``execute`` records the SQL
it was called with; ``fetchone``/``fetchall`` return canned dict rows). See
dev/TODO/T20260827-107079-cloudberry-mcp-segment-adapter.md's Test plan.
"""

from unittest.mock import MagicMock

import pytest

from cloudberry_segment_adapter import queries


def make_cursor(fetchall_result=None, fetchone_result=None):
    cursor = MagicMock()
    cursor.fetchall.return_value = fetchall_result or []
    cursor.fetchone.return_value = fetchone_result
    return cursor


def test_list_segments_flags_down_and_unsynced():
    rows = [
        {
            "dbid": 1, "content": -1, "role": "p", "preferred_role": "p",
            "mode": "s", "status": "u", "hostname": "coord", "address": "coord",
            "port": 5432,
        },
        {
            "dbid": 2, "content": 0, "role": "p", "preferred_role": "p",
            "mode": "s", "status": "d", "hostname": "seg0", "address": "seg0",
            "port": 40000,
        },
        {
            "dbid": 3, "content": 0, "role": "m", "preferred_role": "m",
            "mode": "n", "status": "u", "hostname": "seg0m", "address": "seg0m",
            "port": 40001,
        },
    ]
    cursor = make_cursor(fetchall_result=rows)

    result = queries.list_segments(cursor)

    cursor.execute.assert_called_once_with(queries.LIST_SEGMENTS_SQL)
    assert result["segments"] == rows
    assert [r["dbid"] for r in result["down"]] == [2]
    assert [r["dbid"] for r in result["unsynced"]] == [3]


@pytest.mark.parametrize(
    "row,expected_label",
    [
        (
            {"relname": "t1", "policytype": "r", "numsegments": 3, "distkey_columns": []},
            "REPLICATED",
        ),
        (
            {"relname": "t2", "policytype": "p", "numsegments": 3, "distkey_columns": []},
            "RANDOM",
        ),
        (
            {
                "relname": "t3", "policytype": "p", "numsegments": 3,
                "distkey_columns": ["id", "region"],
            },
            "HASH(id, region)",
        ),
    ],
)
def test_distribution_policy_labels_replicated_random_hash(row, expected_label):
    cursor = make_cursor(fetchone_result=row)

    result = queries.get_distribution_policy(cursor, row["relname"])

    cursor.execute.assert_called_once_with(
        queries.DISTRIBUTION_POLICY_SQL, (row["relname"],)
    )
    assert result["distribution"] == expected_label
    assert result["table"] == row["relname"]


def test_distribution_policy_raises_for_unknown_table():
    cursor = make_cursor(fetchone_result=None)

    with pytest.raises(ValueError, match="no distribution policy"):
        queries.get_distribution_policy(cursor, "does_not_exist")


def test_data_skew_flags_deviation():
    # mean = 100; segment 2 is 40% over the mean -> flagged at the 10% threshold
    rows = [
        {"gp_segment_id": 0, "row_count": 100},
        {"gp_segment_id": 1, "row_count": 100},
        {"gp_segment_id": 2, "row_count": 140},
    ]
    cursor = make_cursor(fetchall_result=rows)

    result = queries.check_data_skew(cursor, "sales")

    expected_sql = queries.DATA_SKEW_SQL_TEMPLATE.format(table='"sales"')
    cursor.execute.assert_called_once_with(expected_sql)
    assert result["segments"] == rows
    assert result["skewed"] is True
    assert [s["gp_segment_id"] for s in result["skewed_segments"]] == [2]


def test_data_skew_rejects_unsafe_table_name():
    cursor = make_cursor()

    with pytest.raises(ValueError, match="invalid table name"):
        queries.check_data_skew(cursor, "sales; DROP TABLE users;--")

    cursor.execute.assert_not_called()


def test_explain_segment_aware_extracts_motion_lines():
    plan_rows = [
        {"QUERY PLAN": "Gather Motion 3:1  (slice1; segments: 3)"},
        {"QUERY PLAN": "  ->  Redistribute Motion 3:3  (slice2; segments: 3)"},
        {"QUERY PLAN": "        ->  Seq Scan on orders  (cost=0.00..431.00 rows=1 width=8)"},
    ]
    cursor = make_cursor(fetchall_result=plan_rows)

    result = queries.explain_segment_aware(cursor, "SELECT * FROM orders")

    cursor.execute.assert_called_once_with("EXPLAIN SELECT * FROM orders")
    assert result["motion_lines"] == [
        "Gather Motion 3:1  (slice1; segments: 3)",
        "  ->  Redistribute Motion 3:3  (slice2; segments: 3)",
    ]
    assert "Seq Scan on orders" in result["plan"]
