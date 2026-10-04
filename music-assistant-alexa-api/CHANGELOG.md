<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

## Unreleased

- Show Amazon connection progress and errors beside Connect, validate settings before sign-in and provide a direct sign-in link when pop-ups are blocked.
- Share responsive page styling between Status and Setup.

## 1.3.0-beta.2

- Fix Home Assistant Open Web UI opening the status page with a doubled slash; accept cached status entry links only through the trusted ingress gateway.

## 1.3.0-beta.1 (candidate)

- Move application settings into the ingress setup page, migrate available legacy values and persist web edits.
- Generate the callback URL and initial API password; mask secrets and provide deliberate provider-password reveal.
- Remove the unused AWS region configuration.

- Provide status/setup through Home Assistant ingress without a separate app login, preserving API authentication.
- Keep the Amazon callback under `/ma-alexa-skill/`, completing sign-in in the original ingress browser.
- Verify configured URL reachability on status with background HTTPS/health/audio checks.

- Replace interactive web ASK CLI setup with self-hosted Amazon browser sign-in and direct management APIs.
- Add explicit existing-skill selection, configuration review and supported package import/build verification.
- Preserve skill identity, other locales and unrelated resources; prevent automatic deletion and duplicate creation retries.
- Persist private credentials/progress and resume accepted imports after restart.
- Add Login with Amazon and certificate options, callback proxy guidance and automated protocol/security tests.
- Live Amazon deployment and Echo acceptance are still required before promotion.

## 1.2.0

- Promote the tested beta after maintainer confirmation of real-device playback through NPM.
- Verify signed base image indexes before publication and in PR builds.
- Document shared-host `/alexa/` and `/ma/` API proxy routing.

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
