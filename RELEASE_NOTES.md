# Release Notes — mongo-x-ray-hc

## 2.1.2

### Fixed
- **Report headings are no longer swallowed by the preceding table**: the report markdown is converted with python-markdown's table extension, which keeps a line that follows a table row inside the table, so `### 2.5 Review Shard Key Information` — and its outline entry — disappeared into the server parameters table of `2.4`. Every check item's markdown now ends on a blank line before the next heading is written.
- **Cluster checks survive a missing server parameter**: the chained replication rule asks for `enableOverrideClusterChainingSetting` through `getParameter`, and newer servers answer `InvalidOptions: no option found to get` (code 72). The exception escaped the replica set level check and discarded the status, config and journaling findings with it. A server that does not expose the option now counts as "override not set", while any other `OperationFailure` still propagates.

### Changed
- **Snapshot history window threshold is configurable**: read `min_snapshot_history_window_seconds` from the item configuration (default `5`) instead of a module constant, and quote the configured value in the finding.

## 2.1.1

Dependency and automation release — the plugin's own behaviour is unchanged.

### Dependencies
- Build: `setuptools` 84.0.0 → 84.2.1 ([`GHSA-xmj3-9gf7-h52w`](https://github.com/advisories/GHSA-xmj3-9gf7-h52w), low — Windows path escape via `namespace_packages.txt` during a legacy wheel install).

### Automation
- **Dependabot auto-merge repaired**: the workflow counted its own in-progress `auto-merge` check when waiting for "every check to pass", so it always timed out and updates stayed open. It now ignores its own check, retries a merge that lost a race with a sibling update, requests a rebase when the branch conflicts, and tolerates branches modified by hand.
- Repository labels `dependencies`, `python` and `github-actions` added, so Dependabot can tag its pull requests.

## 2.1.0

### Changed
- **Issue catalog is owned by this plugin again**: `mongo_x_ray_hc.issues` holds the `ISSUE` enum, the message templates and `create_issue()`. Plugins that reuse health-check rules (log, gmd) reference it through those rules, and the catalog is no longer shipped by the core.
- **Copyable values**: important table contents are wrapped in backticks, so the new report copy icons can copy them with one click.
- **Ships in the prebuilt binary**: the `log` and `gmd` plugins build on the health-check rules, so the frozen `x-ray` binary bundles this plugin too and `x-ray healthcheck` works out of the box.

### Fixed
- **Encryption at rest on mongos**: the encryption-at-rest alert is now skipped for `mongos` (it has no storage engine configuration to check).
- **NUMA**: NUMA is reported on all MongoDB versions again (the alert had become version-dependent).

### Development
- **CI now runs on pull requests** as well as on pushes to `main`, so a dependency bump is linted and tested before it can land.
- **Dependabot** is enabled for `pip` and GitHub Actions (weekly). Patch and minor updates merge automatically once every check is green, as do major updates of the CI actions and the build/lint/test tooling; a major update of a runtime dependency (`mongo-x-ray`) is left for review, and a failing or missing check leaves the pull request open instead of merging.
- **Tooling bumped**: `setuptools` 83.0.0 → 84.0.0, `actions/checkout` v4 → v7, `actions/setup-python` v5 → v7.

### Inherited from core (applies to every health check report)
- **Copy icons** for inline code, code blocks (top-right icon instead of the "Copy" text) and table `<pre>` blocks, preserving line breaks and indentation when copied.
- **Output folder naming**: report folders are prefixed with the plugin name (`healthcheck-default-<timestamp>`, `healthcheck-<hostname>-default-<timestamp>`), including with `--discover`.

## 2.0.0

The health check was extracted into a standalone plugin (`mongo-x-ray-hc`, package `mongo_x_ray_hc`, command `healthcheck` with the `hc` alias), using the shared `mongo_x_ray` core. It added replication rules (journaling, chained replication, write concern, member priority), server parameter checks (snapshot window, SBE, FTDC, TLS protocols), an optional risk-register integration (Known Risks column hidden when no register is detected), plus a Makefile, CI, CodeQL and (Test)PyPI publishing. MongoDB 5.0+ is required; standalone deployments are not supported.
