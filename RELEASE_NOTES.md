# Release Notes — mongo-x-ray-hc

> Generated from the full Git commit history (2026-08-23 → 2026-08-31, 45 commits).

## Initial Release (v2.0.0)
- Extracted the health check into a standalone `mongo-x-ray-healthcheck` plugin; renamed the distribution to **mongo-x-ray-hc** (package `mongo_x_ray_hc`) and switched imports to the shared `mongo_x_ray` core.
- Added an `hc` alias for the `healthcheck` command.
- Added a Makefile (`minify`, `unit-test`, `lint` targets) and unit-test launch configuration.

## New Features
- **Replication rules:**
  - `JournalingRule` — alerts on `writeConcernMajorityJournalDefault` not enabled.
  - `ChainedReplicationRule` — alerts on `chainingAllowed` (with proper unwrapped rs-config handling).
  - `WriteConcernRule` — alerts on non-default write concern, including `wtimeout = 0`.
- **Server parameter checks:**
  - Collects `server_parameters` in a dedicated check item; parameter issues grouped under ID range 1700.
  - Alerts on high `minSnapshotHistoryWindowInSeconds`, enabled SBE on MongoDB 6.0/7.0, FTDC configuration issues, insecure/unrecognized TLS protocols, and improper member priority settings.
- **Risk register as an optional plugin** (`mongo_x_ray_risk`): Known Risks summary column is hidden when no risk register is detected; plugin distribution declared so `x-ray <name> --version` works.

## Fixes
- Fixed risk tooltips wrapping in Markdown tables.
- Use bundled test fixtures instead of core `misc/` data.
- Fixed an uninitialized browser fixture variable in CI.
- Style: widened the Category column in the summary table.

## Tooling & Quality
- Migrated to ruff (lint + format) with matching `.vscode` config; dropped pylint/Black; pinned pyright config and fixed type errors.
- Declared direct dependencies after an import audit; deterministic isort via explicit known-first-party.
- Unified copyright headers to 2026 and normalized formatting.

## CI/CD
- Added GitHub Actions CI with a lint target.
- Enabled CodeQL analysis.
- Publish to (Test)PyPI on tagged releases via trusted publishing.

## Documentation
- Rewrote the README: badges (CI, PyPI), usage and parameters, analysis items, and compatibility matrix.
- Documented MongoDB 5.0+ requirement and topology compatibility (replica sets and sharded clusters supported; **standalone not supported**).
