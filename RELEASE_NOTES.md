# Release Notes — mongo-x-ray-hc

## 2.1.0

### Changed
- **Issue catalog is owned by this plugin again**: `mongo_x_ray_hc.issues` holds the `ISSUE` enum, the message templates and `create_issue()`. Plugins that reuse health-check rules (log, gmd) reference it through those rules, and the catalog is no longer shipped by the core.
- **Copyable values**: important table contents are wrapped in backticks, so the new report copy icons can copy them with one click.

### Fixed
- **Encryption at rest on mongos**: the encryption-at-rest alert is now skipped for `mongos` (it has no storage engine configuration to check).
- **NUMA**: NUMA is reported on all MongoDB versions again (the alert had become version-dependent).

### Inherited from core (applies to every health check report)
- **Copy icons** for inline code, code blocks (top-right icon instead of the "Copy" text) and table `<pre>` blocks, preserving line breaks and indentation when copied.
- **Output folder naming**: report folders are prefixed with the plugin name (`healthcheck-default-<timestamp>`, `healthcheck-<hostname>-default-<timestamp>`), including with `--discover`.

## 2.0.0

The health check was extracted into a standalone plugin (`mongo-x-ray-hc`, package `mongo_x_ray_hc`, command `healthcheck` with the `hc` alias), using the shared `mongo_x_ray` core. It added replication rules (journaling, chained replication, write concern, member priority), server parameter checks (snapshot window, SBE, FTDC, TLS protocols), an optional risk-register integration (Known Risks column hidden when no register is detected), plus a Makefile, CI, CodeQL and (Test)PyPI publishing. MongoDB 5.0+ is required; standalone deployments are not supported.
