#!/usr/bin/env bash
set -e

ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH

isort .
black .
npx pyright
pytest
flake8 logchange

./scripts/docs.sh
