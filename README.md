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
x-ray hc  # alias
x-ray healthcheck -u mongodb://localhost:27017 -f html -o /path/to/output/
```

## Development

Requires Python 3.10+ and the [mongo-x-ray](https://github.com/mongodb-ps/ce-mongo-x-ray) core package.

```bash
make unit-test   # run the unit tests
make lint        # ruff check + ruff format --check
make minify      # minify templates
```
