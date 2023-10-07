#! /usr/bin/env bash

SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

cd "$PROJECT_ROOT" || exit

docker build . --file="./Dockerfile_precommit" --tag="code_checks:latest"
docker run --rm -v "$PWD":/project code_checks:latest bash -c "pre-commit run --a $*"
