# AGENTS.md — Music Assistant Alexa API add-on

## Architecture

- The add-on image builds `FROM ghcr.io/timlaing/music-assistant-skill:<tag>@<digest>`
  — the cosign-signed skill release image (patched Python 3.12 venv at
  `/app/venv`, ASK CLI, skill code at `/app/src`, assets) — plus a thin
  add-on layer: `gunicorn`, `gunicorn.conf.py`, the `rootfs/` entrypoint and
  the healthcheck. The entrypoint replaces the Home Assistant base
  s6-overlay/bashio service definition (the skill image is Ubuntu-based).
- The skill source is no longer vendored via a git submodule; skill code
  arrives through the image.

## Bumping the skill image (do this whenever a skill release should reach users)

1. The skill repo publishes `ghcr.io/timlaing/music-assistant-skill:vX.Y.Z`
   (plus `X.Y.Z`/`latest`) automatically when a GitHub release is published,
   and signs it. Check it exists:
   `docker buildx imagetools inspect ghcr.io/timlaing/music-assistant-skill:vX.Y.Z`.
2. Update `music-assistant-alexa-api/build.yaml` `build_from` (both arches
   share the same multi-arch tag) **and** the Dockerfile
   `ARG BUILD_FROM=` default — they must stay identical (tests enforce this).
   Keep the `@sha256:` digest (shown by the inspect command above) after the tag.
3. Bump `config.yaml` `version`, add a `CHANGELOG.md` entry, open the release PR.

## Tests

- Host: `pytest tests/ -q` (deps in `requirements-test.txt`), `ruff check .`.
- Container (mirrors CI): `scripts/test_container.sh <image> <platform>` runs
  the add-on contract tests **and the skill repo's test suite** inside the
  image. The skill tests are not vendored: CI checks out the skill repo at the
  pinned release tag into `music-assistant-alexa-api/skill-api/` (gitignored).
  Locally:
  `git clone --depth 1 --branch vX.Y.Z git@github.com:timlaing/music-assistant-alexa-skill.git music-assistant-alexa-api/skill-api`
  then `bash scripts/test_container.sh <image> <platform>`.

## Release flow

- PRs only, squash-merge, never push to `main`. If `gh pr merge` reports
  `BLOCKED` with checks green:
  `gh api -X PUT repos/timlaing/music-assistant-alexa-api/pulls/N/merge -f merge_method=squash`.
- CI: add-on linter, runtime container tests on amd64 + aarch64 (which
  cosign-verify the base image signature), then the image build; merges to
  `main` publish and sign `ghcr.io/timlaing/{arch}-addon-ma-alexa-api:<version>`.
- Publishing the GitHub release (release-drafter draft →
  `gh release edit <draft> --tag vX.Y.Z --title 'Music Assistant Alexa API add-on X.Y.Z' --target main`
  → `--draft=false`) is a separate, user-approved step.
