"""
Build the combined app into app/build/: the platform view plus every product's dashboard.

Reads the ops log (PLATFORM.OPS in Snowflake or warehouse/platform.duckdb) and copies each
project's dashboard with its data inlined, so the whole app is static files.

    python -m app.build_app                      # ops data from local DuckDB
    python -m app.build_app --target snowflake   # ops data from Snowflake
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date, datetime
from pathlib import Path

import yaml

from switchyard import ops

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "app" / "build"
# the global each dashboard reads its data from when it's inlined
DATA_VAR = {"bellwether": "MP_DATA", "throughline": "CP_DATA", "clip-curator": "CC_DATA"}


def rows(sql: str) -> list[dict]:
    if ops._target == "snowflake":
        cur = ops._conn.cursor()
        cur.execute(sql)
        cols = [c[0].lower() for c in cur.description]
        data = cur.fetchall()
    else:
        cur = ops._conn.execute(sql)
        cols = [c[0].lower() for c in cur.description]
        data = cur.fetchall()
    out = []
    for r in data:
        d = {}
        for c, v in zip(cols, r):
            if isinstance(v, (datetime, date)):
                v = v.isoformat()
            elif hasattr(v, "as_tuple"):
                v = float(v)
            d[c] = v
        out.append(d)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=["duckdb", "snowflake"], default="duckdb")
    ap.add_argument("--save-ops", help="also write the ops payload to this JSON file (no credentials needed to rebuild)")
    ap.add_argument("--from-ops", help="build from a saved ops payload instead of querying the ops log")
    args = ap.parse_args()
    projects = yaml.safe_load((ROOT / "projects.yml").read_text())["projects"]
    if args.from_ops:
        payload = json.loads(Path(args.from_ops).read_text(encoding="utf-8"))
        write_app(projects, payload)
        return
    ops.connect(args.target)

    runs = rows("""select run_id, started_at, finished_at, target, trigger_type, status
                   from pipeline_runs where finished_at is not null order by started_at desc limit 25""")
    latest = {}
    for p in projects:
        r = rows(f"""select s.run_id from step_runs s join pipeline_runs r on r.run_id = s.run_id
                     where s.project = '{p['name']}' and r.finished_at is not null
                     order by r.started_at desc limit 1""")
        if not r:
            continue
        rid = r[0]["run_id"]
        latest[p["name"]] = {
            "run_id": rid,
            "steps": rows(f"select step, started_at, seconds, status, detail from step_runs "
                          f"where run_id = '{rid}' and project = '{p['name']}' order by started_at"),
            "dbt": rows(f"select resource_type, status, count(*) as n, sum(execution_seconds) as seconds "
                        f"from dbt_results where run_id = '{rid}' and project = '{p['name']}' group by 1, 2"),
            "tables": rows(f"select schema_name, count(*) as tables, sum(row_count) as row_count from table_stats "
                           f"where run_id = '{rid}' and project = '{p['name']}' group by 1 order by 1"),
        }
    run_steps = rows("""select run_id, project, sum(seconds) as seconds,
                               max(case when status = 'error' then 1 else 0 end) as failed
                        from step_runs group by 1, 2""")

    payload = {"generated": datetime.now().isoformat(timespec="seconds"), "target": args.target,
               "projects": [{k: p[k] for k in ("name", "title", "kind", "repo", "snowflake_database")} for p in projects],
               "latest": latest, "runs": runs, "run_steps": run_steps}
    if args.save_ops:
        Path(args.save_ops).write_text(json.dumps(payload, indent=1, default=str), encoding="utf-8")
    write_app(projects, payload)


def write_app(projects: list[dict], payload: dict) -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    for p in projects:
        dash = ROOT / "projects" / p["name"] / "dashboard"
        if not (dash / "index.html").exists():
            continue
        html = (dash / "index.html").read_text(encoding="utf-8")
        data = (dash / "data.json").read_text(encoding="utf-8")
        html = html.replace("<script>\n(async", f"<script>window.{DATA_VAR[p['name']]}={data};</script>\n<script>\n(async", 1)
        (BUILD / p["name"]).mkdir()
        (BUILD / p["name"] / "index.html").write_text(html, encoding="utf-8")

    page = (ROOT / "app" / "index.html").read_text(encoding="utf-8")
    page = page.replace("/*__OPS__*/", "window.OPS=" + json.dumps(payload, separators=(",", ":"), default=str) + ";")
    (BUILD / "index.html").write_text(page, encoding="utf-8")
    print(f"Built app/build with {len(payload['latest'])} products and {len(payload['runs'])} runs of history")


if __name__ == "__main__":
    main()
