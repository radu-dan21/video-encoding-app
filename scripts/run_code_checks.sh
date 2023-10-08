#! /usr/bin/env bash

SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

cd "$PROJECT_ROOT" || exit

if [[ -z ${CODE_CHECKS_IMAGE_TAG} ]]; then
  # local run, code checks image must be built
  CODE_CHECKS_IMAGE_TAG='code_checks:latest'
  docker build . --file="./Dockerfile_precommit" --tag=$CODE_CHECKS_IMAGE_TAG
fi

docker run --rm -v "$PWD":/project $CODE_CHECKS_IMAGE_TAG bash -c "pre-commit run --a $*"
