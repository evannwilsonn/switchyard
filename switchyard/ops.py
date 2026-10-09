"""
The platform's own operational data: runs, steps, dbt results and table sizes.

Written to PLATFORM.OPS in Snowflake (--target snowflake) or to warehouse/platform.duckdb
locally. Snowflake sign-in is key-pair (SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER,
SNOWFLAKE_PRIVATE_KEY_PATH); no password is read or stored.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_conn = None
_target = None

DDL = [
    """create table if not exists pipeline_runs (run_id varchar, started_at timestamp, finished_at timestamp,
       target varchar, trigger_type varchar, status varchar)""",
    """create table if not exists step_runs (run_id varchar, project varchar, step varchar, started_at timestamp,
       seconds double, status varchar, detail varchar)""",
    """create table if not exists dbt_results (run_id varchar, project varchar, unique_id varchar, resource_type varchar,
       status varchar, execution_seconds double, failures integer)""",
    """create table if not exists table_stats (run_id varchar, project varchar, schema_name varchar, table_name varchar,
       row_count bigint)""",
]


def connect(target: str) -> None:
    global _conn, _target
    _target = target
    if target == "snowflake":
        import snowflake.connector
        _conn = snowflake.connector.connect(
            account=os.environ["SNOWFLAKE_ACCOUNT"], user=os.environ["SNOWFLAKE_USER"],
            private_key_file=os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"],
            role=os.environ.get("SNOWFLAKE_ROLE", "SYSADMIN"))
        cur = _conn.cursor()
        wh = os.environ.get("SNOWFLAKE_WAREHOUSE", "PORTFOLIO_WH")
        cur.execute(f"create warehouse if not exists {wh} warehouse_size = xsmall auto_suspend = 60 auto_resume = true")
        cur.execute(f"use warehouse {wh}")
        cur.execute("create database if not exists PLATFORM")
        cur.execute("create schema if not exists PLATFORM.OPS")
        cur.execute("use schema PLATFORM.OPS")
    else:
        import duckdb
        (ROOT / "warehouse").mkdir(exist_ok=True)
        _conn = duckdb.connect(str(ROOT / "warehouse" / "platform.duckdb"))
        _conn.execute("create schema if not exists ops")
        _conn.execute("set schema = 'ops'")
    for ddl in DDL:
        _exec(ddl)


def _exec(sql: str, params=None) -> None:
    if _target == "snowflake":
        _conn.cursor().execute(sql, params)
    else:
        _conn.execute(sql.replace("%s", "?"), params or [])


def _many(sql: str, rows: list) -> None:
    if not rows:
        return
    if _target == "snowflake":
        _conn.cursor().executemany(sql, rows)
    else:
        _conn.executemany(sql.replace("%s", "?"), rows)


def start_run(run_id, started, target, trigger) -> None:
    _exec("insert into pipeline_runs values (%s, %s, null, %s, %s, 'running')", [run_id, started, target, trigger])


def finish_run(run_id, finished, status) -> None:
    _exec("update pipeline_runs set finished_at = %s, status = %s where run_id = %s", [finished, status, run_id])


def record_step(run_id, project, step, started, seconds, status, detail) -> None:
    _exec("insert into step_runs values (%s, %s, %s, %s, %s, %s, %s)",
          [run_id, project, step, started, seconds, status, (detail or "")[:4000]])


def record_dbt_results(run_id, project, results: dict) -> None:
    rows = []
    for r in results.get("results", []):
        uid = r["unique_id"]
        rows.append([run_id, project, uid, uid.split(".")[0], r["status"],
                     round(r.get("execution_time") or 0, 3), r.get("failures") or 0])
    _many("insert into dbt_results values (%s, %s, %s, %s, %s, %s, %s)", rows)


def record_table_stats(run_id, p: dict, path: Path, target: str) -> None:
    rows = []
    try:
        if target == "snowflake":
            cur = _conn.cursor()
            cur.execute(f"select table_schema, table_name, row_count from {p['snowflake_database']}.information_schema.tables "
                        "where table_type = 'BASE TABLE' and table_schema <> 'INFORMATION_SCHEMA'")
            rows = [[run_id, p["name"], s.lower(), t.lower(), n or 0] for s, t, n in cur.fetchall()]
        else:
            import duckdb
            con = duckdb.connect(str(path / p["duckdb"]), read_only=True)
            for s, t in con.execute("select table_schema, table_name from information_schema.tables "
                                    "where table_type = 'BASE TABLE'").fetchall():
                n = con.execute(f'select count(*) from "{s}"."{t}"').fetchone()[0]
                rows.append([run_id, p["name"], s, t, n])
            con.close()
    except Exception:
        return
    _many("insert into table_stats values (%s, %s, %s, %s, %s)", rows)
