"""
Pull a product's modeled layers (staging, core, reporting, reference) from Snowflake into its
local DuckDB file, so the dashboard export reads exactly what Snowflake built.

Each table or view is unloaded to Parquet with COPY INTO a stage, fetched with GET and
loaded into DuckDB under the same schema and name.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import duckdb
import snowflake.connector

SCHEMAS = ("STAGING", "CORE", "REPORTING", "REFERENCE")


def mirror(database: str, duckdb_path: Path) -> int:
    sf = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"], user=os.environ["SNOWFLAKE_USER"],
        private_key_file=os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"],
        role=os.environ.get("SNOWFLAKE_ROLE", "SYSADMIN"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "PORTFOLIO_WH"), database=database)
    cur = sf.cursor()
    cur.execute("create schema if not exists _MIRROR")
    cur.execute("create stage if not exists _MIRROR._UNLOAD")
    cur.execute(f"select table_schema, table_name from {database}.information_schema.tables "
                f"where table_schema in ({', '.join(repr(s) for s in SCHEMAS)})")
    objects = cur.fetchall()
    tmp = Path(tempfile.mkdtemp())
    duck = duckdb.connect(str(duckdb_path))
    for schema, table in objects:
        key = f"{schema}/{table}/"
        cur.execute(f"select column_name, data_type from {database}.information_schema.columns "
                    "where table_schema = %s and table_name = %s order by ordinal_position", (schema, table))
        cols = cur.fetchall()
        # timestamps travel as ISO text: DuckDB can't always read Snowflake's millisecond Parquet timestamps
        ts = {c for c, t in cols if t.startswith("TIMESTAMP")}
        fmt = "'YYYY-MM-DD HH24:MI:SS.FF6'"
        select = ", ".join((f'to_varchar("{c}", {fmt}) as "{c}"' if c in ts else f'"{c}"') for c, _ in cols)
        cur.execute(f'copy into @_MIRROR._UNLOAD/{key} from (select {select} from {database}.{schema}."{table}") '
                    "file_format = (type = parquet) header = true overwrite = true")
        dest = tmp / schema / table
        dest.mkdir(parents=True, exist_ok=True)
        cur.execute(f"get @_MIRROR._UNLOAD/{key} 'file://{dest.as_posix()}/'")
        files = sorted(dest.glob("*.parquet"))
        s, t = schema.lower(), table.lower()
        duck.execute(f"create schema if not exists {s}")
        kind = duck.execute("select table_type from information_schema.tables where table_schema = ? and table_name = ?",
                            [s, t]).fetchone()
        if kind and kind[0] == "VIEW":
            duck.execute(f"drop view {s}.{t}")
        if files:
            paths = [f.as_posix() for f in files]
            cols = [r[0] for r in duck.execute(f"describe select * from read_parquet({paths})").fetchall()]
            # Snowflake upper-cases unquoted names; give them back their dbt (lower-case) spelling
            name = lambda c: c.lower() if c == c.upper() else c
            sel = ", ".join((f'try_cast("{c}" as timestamp)' if c in ts else f'"{c}"') + f' as "{name(c)}"' for c in cols)
            duck.execute(f"create or replace table {s}.{t} as select {sel} from read_parquet({paths})")
        else:  # an empty table unloads no files
            duck.execute(f"drop table if exists {s}.{t}")
    duck.close()
    sf.close()
    return len(objects)
