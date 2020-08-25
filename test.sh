#!/bin/bash
# Run all codex tests
set -euxo pipefail
mkdir -p test-results
poetry run pytest
# pytest-cov leaves .coverage.$HOST.$PID.$RAND files around while coverage itself doesn't
bash -c "cd frontend && npm run test:unit"
poetry run coverage erase || true
poetry run vulture --exclude frontend . || true
poetry run radon mi -nc . || true
