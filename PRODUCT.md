# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Hiring managers first, arriving from Evan Wilson's resume or LinkedIn and giving the page about a minute; they need to see one platform running three different data products end to end, and that its health view is measured from a real run log. Data and platform engineers second, who check the run steps, the dbt results and the Snowflake load. Desktop and phone viewing are about equal. (Confirmed for the whole portfolio on 2026-10-09.)

## Product Purpose

Switchyard is one small data platform that runs three separate data products (Bellwether markets pipeline, Throughline executive KPI dashboard, Clip Curator AI video curation) through the same five steps (extract, load, warehouse load to Snowflake, dbt transform, export), records every run, step, dbt result and table row count to an ops schema (PLATFORM.OPS), and serves one app: a platform view built only from that log, plus each product's own dashboard. Success: a reader understands in seconds that three unlike workloads go through one shared, logged process, sees the latest run's outcome per product, and can open any product.

## Positioning

Platform engineering shown at portfolio scale: the products keep their own repos and dbt projects; Switchyard owns the operational layer (orchestration order, failure stop, warehouse load with row-count checks, Snowflake mirror back, ops log) and is honest about history, including the failed runs that came before the first clean Snowflake run.

## Operating Context

Static app: app/index.html receives the ops payload inlined at build (window.OPS), and links to each product's dashboard under app/build/<product>/. Also published as a Claude artifact.

## Capabilities and Constraints

- Payload: projects (name, title, kind, repo, Snowflake database), latest run per product (steps with seconds, status, detail; dbt results by type and status; table counts by schema), up to 25 runs with status, per-run per-product seconds and failure flags.
- Clip Curator's extract step loads saved AI results (YOLOv8 + CLIP output) rather than re-running the models; the page must say so.
- "Cleaned records" counts core-schema rows only.
- Run history is short: 6 runs, 4 of the first 5 Snowflake attempts failed (the one that passed ran Bellwether alone) before the export was fixed. Show them.
- Every number comes from the payload.

## Brand Commitments

Each portfolio project has its own visual world and its own new colour palette, distinct from Reprise (cool white, ink, blue ramp, amber), Cloverfield (control-room black, Caltrans orange, green/amber/red), Cloverleaf (concrete grey, plum, lime) and the earlier IBM Plex blue and sign-green looks.

## Evidence on Hand

app/ops_snapshot.json (the saved ops payload from the Snowflake run log). Product dashboards in app/build/.

## Product Principles

1. One process, three products: the shared steps are the spine of the page.
2. The log is the source: every status traces to a recorded step.
3. Failures stay in the history.
4. Every product is one click away.

## Accessibility & Inclusion

WCAG AA contrast in light and dark; status never carried by colour alone; works at phone width.
