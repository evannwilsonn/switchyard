"""
Switchyard: run every data product end to end and record what happened.

For each project in projects.yml it runs, in order:
  extract         pull source data (or, for Clip Curator, unpack the published AI extraction)
  load            land the raw files in the project's local DuckDB warehouse
  warehouse_load  copy the raw layer into the project's Snowflake database (--target snowflake only)
  transform       dbt build: every model and test
  export          write the dashboard's data file

Every run, step, dbt result and table row count is written to an ops schema
(PLATFORM.OPS in Snowflake, warehouse/platform.duckdb locally). That's what the
platform-health view in the app reads.

    python -m switchyard.run                      # all projects, DuckDB
    python -m switchyard.run --target snowflake   # all projects, Snowflake
    python -m switchyard.run --only throughline   # one project
    python -m switchyard.run --full-ai            # re-run YOLOv8 + CLIP instead of the snapshot
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tarfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

from switchyard import ops

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
PY = sys.executable


def now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)


def sh(args: list[str], cwd: Path) -> tuple[int, str]:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return p.returncode, (p.stdout + p.stderr)[-4000:]


def ensure_repo(p: dict) -> Path:
    path = PROJECTS / p["name"]
    if not (path / ".git").exists():
        PROJECTS.mkdir(exist_ok=True)
        code, out = sh(["git", "clone", "--quiet", p["repo"], str(path)], ROOT)
        if code:
            raise RuntimeError(f"clone failed: {out}")
    else:
        sh(["git", "pull", "--quiet", "--ff-only"], path)
    return path


def step_extract(p: dict, path: Path, args) -> str:
    scripts = p.get("extract_full") if args.full_ai and p.get("extract_full") else p["extract"]
    if scripts == ["snapshot"]:
        (path / "data").mkdir(exist_ok=True)
        with tarfile.open(path / "snapshots" / "extracted.tar.gz") as t:
            t.extractall(path / "data", filter="data")
        return "loaded saved AI results from the published snapshot (YOLOv8 + CLIP not re-run; pass --full-ai to re-run)"
    for s in scripts:
        code, out = sh([PY, s], path)
        if code:
            raise RuntimeError(out)
    return f"ran {', '.join(scripts)}"


def step_load(p: dict, path: Path, args) -> str:
    code, out = sh([PY, "ingest/load_raw.py"], path)
    if code:
        raise RuntimeError(out)
    return out.strip().splitlines()[-1] if out.strip() else "loaded"


def step_warehouse_load(p: dict, path: Path, args) -> str:
    if args.target != "snowflake":
        return "skipped (local target)"
    code, out = sh([PY, "ingest/load_snowflake.py", "--duckdb", p["duckdb"], "--database", p["snowflake_database"],
                    "--schemas", ",".join(p["raw_schemas"])], path)
    if code:
        raise RuntimeError(out)
    return f"{len(out.strip().splitlines())} raw tables copied"


def step_transform(p: dict, path: Path, args) -> str:
    target = ["--target", "snowflake"] if args.target == "snowflake" else []
    code, out = sh([PY, "-m", "dbt.cli.main", "build", "--profiles-dir", ".", *target], path)
    results = path / "target" / "run_results.json"
    if results.exists():
        ops.record_dbt_results(args.run_id, p["name"], json.loads(results.read_text()))
    summary = next((l for l in reversed(out.splitlines()) if "Done. PASS=" in l), "")
    if code:
        raise RuntimeError(summary or out)
    return summary.split("Done. ")[-1].strip()


def step_export(p: dict, path: Path, args) -> str:
    note = ""
    if args.target == "snowflake":
        from switchyard.mirror import mirror
        n = mirror(p["snowflake_database"], path / p["duckdb"])
        note = f" from Snowflake ({n} modeled tables pulled)"
    code, out = sh([PY, "dashboard/export_data.py"], path)
    if code:
        raise RuntimeError(out)
    wrote = [l for l in out.splitlines() if l.startswith("Wrote")]
    return (wrote[-1] if wrote else "exported") + note


STEPS = {"extract": step_extract, "load": step_load, "warehouse_load": step_warehouse_load,
         "transform": step_transform, "export": step_export}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=["duckdb", "snowflake"], default="duckdb")
    ap.add_argument("--only", help="run a single project by name")
    ap.add_argument("--full-ai", action="store_true")
    ap.add_argument("--trigger", default="manual")
    args = ap.parse_args()
    args.run_id = uuid.uuid4().hex[:12]

    cfg = yaml.safe_load((ROOT / "projects.yml").read_text())["projects"]
    if args.only:
        cfg = [p for p in cfg if p["name"] == args.only]
    ops.connect(args.target)
    started = now()
    ops.start_run(args.run_id, started, args.target, args.trigger)
    print(f"Switchyard run {args.run_id} · target {args.target}")
    ok = True
    for p in cfg:
        print(f"\n{p['title']} ({p['kind']})")
        try:
            path = ensure_repo(p)
        except Exception as exc:
            ops.record_step(args.run_id, p["name"], "checkout", now(), 0, "error", str(exc)[:2000])
            ok = False
            continue
        for name in p["steps"]:
            t0, st = time.time(), now()
            try:
                detail, status = STEPS[name](p, path, args), "success"
            except Exception as exc:
                detail, status = str(exc)[-2000:], "error"
            secs = round(time.time() - t0, 2)
            ops.record_step(args.run_id, p["name"], name, st, secs, status, detail)
            print(f"  {name:<15} {status:<8} {secs:>7.1f}s  {detail.splitlines()[-1][:80] if detail else ''}")
            if status == "error":
                ok = False
                break
        ops.record_table_stats(args.run_id, p, path, args.target)
    ops.finish_run(args.run_id, now(), "success" if ok else "error")
    print(f"\nRun {'succeeded' if ok else 'FAILED'} in {(now() - started).total_seconds():.0f}s")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
