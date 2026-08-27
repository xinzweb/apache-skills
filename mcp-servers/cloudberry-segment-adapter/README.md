# cloudberry-segment-adapter

A thin [MCP](https://modelcontextprotocol.io/) server exposing Apache
Cloudberry (Incubating)-specific SQL/DB visibility that no generic
Postgres-family MCP server provides: segment health, distribution-key
correctness, data skew, and segment-aware `EXPLAIN` output.

See `dev/TODO/T20260827-107079-cloudberry-mcp-segment-adapter.md` for the
design and `dev/TODO/T20260827-203753-mcp-server-survey.md` for the survey
that motivated it.

## Pair with a generic MCP server

This adapter is deliberately narrow — it does **not** provide schema
browsing or general SQL execution. Run it alongside a generic
wire-protocol MCP server (e.g.
[`mcp-alchemy`](https://github.com/runekaagaard/mcp-alchemy)) for baseline
access; that tier already works against Cloudberry unmodified.

## Tools

- `list_segments()` — segment configuration from `gp_segment_configuration`,
  flagging down (`status='d'`) or out-of-sync (`mode='n'`) segments.
- `get_distribution_policy(table_name)` — a table's distribution policy
  from `gp_distribution_policy`, labeled `REPLICATED` / `RANDOM` /
  `HASH(col1, col2, ...)`.
- `check_data_skew(table_name)` — per-segment row counts, flagging segments
  more than 10% above the mean (a tool-chosen heuristic, not an official
  Cloudberry number).
- `explain_segment_aware(query)` — runs `EXPLAIN` on `query` and pulls out
  the `Motion` (redistribution-cost) plan lines. `query` is caller-supplied
  and executed as-is, the same trust model as any `execute_sql`/
  `explain_query` MCP tool.

## Setup

```bash
cd mcp-servers/cloudberry-segment-adapter
pip install -e .
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
cloudberry-segment-adapter   # runs over stdio
```

## Testing

No live Cloudberry cluster is required (or used) — the test suite mocks
the DB cursor:

```bash
pip install -e ".[dev]"
pytest tests/
```

**Not yet verified**: running against a live Cloudberry cluster. No
cluster was reachable from the environment this was built in — see the
task file's Test plan for the explicit unverified item.
