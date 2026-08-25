# mongo-x-ray-hc

[![CI](https://github.com/zhangyaoxing/mongo-x-ray-hc/actions/workflows/ci.yml/badge.svg)](https://github.com/zhangyaoxing/mongo-x-ray-hc/actions/workflows/ci.yml)

Health check analysis plugin for [x-ray](https://github.com/mongodb-ps/ce-mongo-x-ray).

## Install

```bash
pip install mongo-x-ray mongo-x-ray-hc
```

## Usage

```bash
x-ray healthcheck
x-ray hc  # alias for healthcheck
x-ray healthcheck -u mongodb://localhost:27017 -f html -o /path/to/output/
```

## Parameters

```bash
x-ray healthcheck [-h] [-u URI] [-s CHECKSET] [-o OUTPUT]
                  [-f {markdown,html,pdf}] [--no-browser]
```

| Argument | Description | Default |
| --- | --- | --- |
| `-u, --uri` | MongoDB connection URI. | `HC_URI` env var, else `mongodb://localhost:47017` |
| `-s, --checkset` | Checkset to run. | `default` |
| `-o, --output` | Output folder path. | `output/` |
| `-f, --format` | Output format: `markdown`, `html` or `pdf` (PDF also keeps Markdown and HTML). | `html` |
| `--no-browser` | Do not open the generated report in the browser. | `false` |

## Check Items

| Item | Purpose |
| --- | --- |
| `BuildInfoItem` | MongoDB server build information, including a version end-of-life check. |
| `ClusterItem` | Cluster topology: replica set config/status, sharding overview and oplog window. |
| `CollInfoItem` | Collection information: sizes, fragmentation and operation latency. |
| `HostInfoItem` | Host information: filesystem type, NUMA settings and host properties. |
| `IndexInfoItem` | Index coverage and health. |
| `SecurityItem` | Security posture (authentication and authorization). |
| `ServerStatusItem` | Server status: cache, connections, opcounters and query targeting. |
| `ShardKeyItem` | Shard key selection and data balance. |

## Development

Requires Python 3.10+ and the [mongo-x-ray](https://github.com/mongodb-ps/ce-mongo-x-ray) core package.

```bash
make unit-test   # run the unit tests
make lint        # ruff check + ruff format --check
make minify      # minify templates
```
