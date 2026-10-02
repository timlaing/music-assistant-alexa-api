#!/usr/bin/env bash
set -euo pipefail
image="${1:?image required}"
platform="${2:?platform required}"
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
docker run --rm --platform "$platform" --entrypoint /bin/sh \
  -e AWS_EC2_METADATA_DISABLED=true -e SKILL_APP_PATH=/app/src \
  -v "$repo_root:/tests:ro" "$image" -c \
  '/app/venv/bin/pip install --quiet pytest==9.1.1 PyYAML==6.0.3 && /app/venv/bin/python -m pytest -p no:cacheprovider -q /tests/tests/test_addon.py /tests/music-assistant-alexa-api/skill-api/tests && /app/venv/bin/python -c "from certvalidator import ValidationContext; ValidationContext(); print(\"certificate registry ready\")"'
docker run --rm --platform "$platform" --entrypoint /app/venv/bin/python \
  -v "$repo_root/tests/container_smoke.py:/tmp/container_smoke.py:ro" \
  "$image" /tmp/container_smoke.py
