<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

## 1.2.0-beta.1

- Update to latest upstream via the maintained Alexa skill fork.
- Fix single-worker playback deadlocks with one threaded worker and direct store access.
- Correct HTTPS stream/artwork rewriting for NPM hostnames and path prefixes.
- Stop stale flow streams and announcements from being enqueued repeatedly.
- Add optional MA voice-control credentials, persistent device mapping and APL settings.
- Add idle-aware status, unauthenticated health checks and fault diagnostics.
- Pin base images and Python dependencies; validate both architecture images in CI.

## 1.1.0

- Update the Alexa skill submodule and support its refactored application layout.
- Add the upstream skill setup UI, locale selection, and optional stream URL validation bypass.
- Run a single application worker so pushed stream state remains consistent.

## 1.0.3

Fix gunicorn worker issues

## 1.0.2

Bugfix environment variable

## 1.0.1

Refactor docker / repo dependencies

## 1.0.0

- Initial release
