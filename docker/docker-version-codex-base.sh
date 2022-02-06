#!/bin/bash
# Compute the version tag for ajslater/codex-base
set -euo pipefail
# shellcheck disable=SC1091
source .env.build
EXTRA_MD5S=("$PYTHON_ALPINE_VERSION  python-alpine-version")

DEPS=(
    "$0"
    .dockerignore
    base.Dockerfile
    docker/docker-arch.sh
    docker/docker-build-image.sh
    docker/docker-env.sh
    docker/docker-env-filename.sh
    docker/docker-init.sh
    docker/docker-version-checksum.sh
    docker/docker-version-codex.sh
    docker-compose.yaml
)

source ./docker/docker-version-checksum.sh
