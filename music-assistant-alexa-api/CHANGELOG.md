<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

## 1.3.8

- The bundled skill moves to `ghcr.io/timlaing/music-assistant-skill:v1.6.0` (cosign-signed). The status page gains an **MA to Amazon channel** check (V13) that catches a dead Music Assistant → Amazon session: MA pushes the stream to the skill but its Alexa provider can no longer ask Amazon to start playback, so MA-initiated play and volume control silently fail while every other check stays green (#86). V13 correlates the pushed stream with the Echo's own playback reports — a fresh push that its player never reports as current becomes a warning pointing at re-authenticating Music Assistant's Alexa provider with Amazon, which is separate from this add-on's **Connect to Amazon** step. An idle Echo does not warn: a stale or absent push reports Unknown instead.
- The **Music Assistant API URL** and **access token** now have their own **Music Assistant control API** section on **Application settings** instead of sitting behind **Advanced connection settings**, with helper text naming what they unlock: the Alexa provider, Now playing and Alexa players status checks, the player picker on Devices, voice pause/resume/stop routed to Music Assistant, and stale one-shot stream recovery (skill PR #55, fixes #87).
- The V1–V12 Music Assistant channel checks probe the configured skill endpoint with its path prefix, so a prefixed deployment is no longer judged by the bare host where another service (for example the Music Assistant stream server) answers (skill PRs #51, #52, fixes skill issues #47 and #49).
- The Current audio check verifies real bytes and HTTP 405 counts as reachable for the Stream host check on Home Assistant roots that only accept GET (skill PR #50, fixes skill issue #48).
- Localized responses keep empty messages empty instead of substituting a fallback (skill PR #57).

## 1.3.7

- The bundled skill moves to `ghcr.io/timlaing/music-assistant-skill:v1.5.0` (cosign-signed). **Upgrading changes the invocation name in every locale to `music assistant`** — relearn the launch phrase after deploying, and redeploy from **Skill setup → Review settings → Deploy approved settings** if the deployed model still uses an older name (skill issue #71). The status page gains an **Invocation name** check (V12) that compares the deployed name against Music Assistant's start command for the configured locale.
- Spoken music selection and queue commands: ask for a song, artist, album, playlist, radio station or favourites; queue, shuffle, insert next and favourite the current track; and hear what is playing, next and previous (skill PR #38). Requires the Music Assistant control API URL and token; `en-US` only, other locales unchanged.
- Playback position: the add-on serves `GET /alexa/playback-state?player_id=…` behind the API credentials, reporting where each Echo really is so Music Assistant's Alexa player no longer drifts ahead of the device with every voice command (skill PR #38). Pairs with Music Assistant server change music-assistant/server#7143.
- Only requests from the deployed skill are accepted: the endpoint rejects correctly-signed requests from any other Alexa skill with the same endpoint, and fails closed until a deployment has been verified (skill PR #36).
- Package verification accepts Amazon skill exports that omit the optional `skill-package/` wrapper (skill PR #37).
- Give each Echo the stream pushed for its own player: with several Echos on separate queues, stale-stream recovery and the APL metadata refresh no longer pick up another player's stream (skill PR #41, fixes skill issue #33).
- Choose the Music Assistant player from a list on the Devices page: a dropdown of Music Assistant's own players labelled by display name, with validation of saved ids and free text as a fallback when Music Assistant is unreachable (skill PR #42).
- A diagnostics download and read-only Music Assistant channel verification (checks V1–V11) are available from the status page for the "skill answers but the Echo stays silent" reports (#40, #71).
- Redesigned setup UI: a four-step wizard with global navigation and eight views on a shared page shell (skill PRs #32, #34). The public skill endpoint is now collected on **Application settings**, before the step that displays the Amazon callback URL derived from it (skill PR #39).
- Consistent field styling across setup and simulator pages, HTTP response statuses in the Invocations tables, and Echo playback state updated from accepted device callbacks (skill PR #40).
- The Stream host HEAD check treats HTTP 405 as reachable for Home Assistant roots that only accept GET.
- Troubleshooting documentation: the Alexa locale must match the locale registered to the Echo devices, the Amazon callback URL follows the public skill endpoint, the reverse-proxy `trusted_proxies` ranges one setup needed, and an ordered "skill answers but the Echo stays silent" sequence including the invocation-name failure class (#72, #76).

## 1.3.7-beta.5

- **Beta — for testing only.** Update the bundled skill to the cosign-signed `v1.5.0-beta.3` image.
- Give each Echo the stream pushed for its own player: with several Echos on separate queues, stale-stream recovery and the APL metadata refresh no longer pick up another player's stream, so the wrong queue no longer starts playing and another Echo's track no longer appears on this one's card (skill PR #41, fixes skill issue #33).
- Choose the Music Assistant player from a list on the Devices page: the player field becomes a dropdown of Music Assistant's own players labelled by display name, a saved id Music Assistant no longer reports is kept, an id that is not a listed player is rejected with the previous mapping untouched, and the free-text field remains as a fallback when Music Assistant is unreachable (skill PR #42). The long Alexa device id now truncates instead of stretching the card grid.

## 1.3.7-beta.4

- **Beta — for testing only.** Update the bundled skill to the cosign-signed `v1.5.0-beta.2` image.
- Use consistent field styling across setup and simulator pages.
- Show recorded HTTP response statuses in the Invocations desktop table and mobile cards; malformed log entries remain readable.
- Update Echo playback from accepted device callbacks, showing the last reported state, device and time. Simulator requests are excluded, and callback timestamps prevent delayed events from replacing newer playback states.
- Treat HTTP 405 as reachable for the Stream host HEAD check, supporting Home Assistant roots that only accept GET. Skill and audio checks retain their stricter response checks.
- Clarify that Echo Show track metadata appears in Metadata diagnostics.

## 1.3.7-beta.3

- **Beta — for testing only.** The bundled skill moves to `ghcr.io/timlaing/music-assistant-skill:v1.5.0-beta.1` (cosign-signed).
- Spoken music selection and queue commands: ask for a song, artist, album, playlist, radio station or favourites; queue, shuffle, insert next and favourite the current track; and hear what is playing, next and previous (skill PR #38). Requires the Music Assistant control API URL and token for library and favourites changes. `en-US` only; other locales are unchanged.
- Playback position: the add-on now serves `GET /alexa/playback-state?player_id=…` behind the API credentials, reporting where each Echo really is so Music Assistant's Alexa player no longer drifts ahead of the device with every voice command (skill PR #38). Pairs with Music Assistant server change music-assistant/server#7143.
- Package verification accepts Amazon exports that omit the optional `skill-package/` wrapper, fixing the deployment failure reported against 1.3.7-beta.2 where every member path differed and the whole package was rejected as a mismatch (skill PR #37).
- Only requests from the deployed skill are accepted: the endpoint rejects correctly-signed requests from any other Alexa skill with the same endpoint, and fails closed until a deployment has been verified (skill PR #36).
- A diagnostics download and read-only Music Assistant channel verification (checks V1–V11) are available from the status page, for the "skill answers but the Echo stays silent" reports in #40 and #71 (skill PR #35).
- Setup now collects the public skill endpoint on **Application settings**, before the step that displays the Amazon callback URL derived from it. The callback URL is derived from the skill endpoint rather than the audio URL, and step 3 no longer collects a value that could silently override an endpoint already registered with Amazon (skill PR #39, addressing points 3 and 4 of @Rob-SBT's report in #40).
- Document the #40 setup findings: the Alexa locale must match the locale registered to the Echo devices, the Amazon callback URL follows the public skill endpoint, the reverse-proxy `trusted_proxies` ranges one setup needed, and a troubleshooting sequence for "the skill answers but the Echo stays silent" (#72).

## 1.3.7-beta.2

- **Beta — for testing only.** The bundled skill moves to `ghcr.io/timlaing/music-assistant-skill:v1.4.2-beta.2` (cosign-signed), which lands the redesigned web UI: eight views on a shared page shell, static assets served from `/assets` with per-use revalidation, and an error fallback on the Devices page that keeps device mapping available (skill PR #34).

## 1.3.7-beta.1

- **Beta — for testing only.** The bundled skill moves to `ghcr.io/timlaing/music-assistant-skill:v1.4.2-beta.1` (cosign-signed), which restructures the skill's setup UI into a four-step wizard with global navigation and adds a test-audio player on the reachability page (skill PR #32).
- Maintenance: CI cosign-verifies the pinned skill image signature before checking out the skill repository to run its test suite (#68).

## 1.3.6

- The bundled skill moves to `ghcr.io/timlaing/music-assistant-skill:v1.4.1` (cosign-signed), which carries the runtime modernization (Ubuntu 26.04, Python 3.14, Node 26) and the skill fix for stale one-shot flow-stream URLs: after an idle period the skill now validates the stored stream URL, asks Music Assistant to resume the player and plays the pushed replacement URL instead of serving a 404 to Alexa (skill PR #31, addressing the playback failures reported in #40).
- Raise the gunicorn keepalive so it outlives client connection pools, fixing the first-attempt `Server disconnected` playback failures on the add-on-facing half of #55 (the `players/cmd/play_pause` path is MA-side via alexapy and is not addressed here).
- Document an NGINX Home Assistant SSL proxy example configuration (#60).
- Maintenance: CI and Sonar analysis run on Python 3.14 (#63); gunicorn.conf.py is excluded from Sonar coverage and remaining coverage exclusions passed as inline scanner args (#64, #65).

Validated as 1.3.6-beta.1 before this release.

## 1.3.5

- Update the bundled skill to 1.3.5: package verification now **validates** icon URIs instead of excluding them — a locale's `smallIconUri`/`largeIconUri` equal to the configured artwork or to Amazon's own materialized `file://assets/images/…` form passes, while a foreign URL, a cross-locale path or a missing key still fails — and stores Amazon's one-time re-encoded icon artwork (`assets/images/*IconUri.png`) into the approved package so the byte comparison never fails on it again. Verified with a full deployment against the live Amazon service; every non-artwork file keeps byte-for-byte verification. Fixes the remaining "Amazon's exported package differs from the approved deployment" failures of #40.
- The add-on image now builds `FROM ghcr.io/timlaing/music-assistant-skill:v1.3.5` (the cosign-signed release image published by the skill repository) instead of compiling the skill from the `skill-api` git submodule. The image already ships the patched Python environment, ASK CLI and assets; the add-on layer contributes gunicorn, the ingress service entrypoint and the healthcheck. Identical application code — faster, reproducible builds and a one-line bump for future skill releases.

## 1.3.4

- Update the bundled skill to 1.3.4: package verification no longer fails on `smallIconUri`/`largeIconUri`, which Amazon rewrites during import and export — this was the remaining cause of "Amazon's exported package differs from the approved deployment" reported for es-ES and en-GB; every other field stays fully verified. No add-on changes.

## 1.3.3

- Update the bundled skill to 1.3.3: a failed package verification now names the differing files and JSON paths, the fr-CA and nl-NL interaction models are converted to the current schema with invocation names and a PlayAudio intent, nl-NL gains a manifest entry, and every bundled locale round-trips a full deployment in the test suite; no add-on changes.

## 1.3.2

- Replace the add-on store README with an overview, installation steps, a quick start and support links.
- Update the bundled skill to 1.3.2, which fixes the standalone image build workflow and refreshes documentation wording; no application changes.

## 1.3.1

- Fix personal-skill deployment for the es-ES, es-MX, fr-FR and it-IT locales, which failed final package verification with "Amazon's exported package differs from the approved deployment" (#40).

- Update the bundled skill to 1.3.1, which includes the custom slot type list in every bundled interaction model so Amazon's export matches the approved package.

## 1.3.0

- Promote the personal-skill deployment wizard to stable following maintainer confirmation that it is tested and working.

- Put LWA registration instructions, the developer-console link and generated callback URL in Connect to Amazon.
- Show connection success with a green tick and place setup feedback in its relevant section.
- Offer Trusted, Trusted sub-domain and File certificate choices; validate and deploy public PEM certificates for development testing.
- Use the maintained add-on artwork for the skill icons.
- Wait for running builds and verify the imported package when Amazon omits legacy build-status fields, preserving failure/mismatch checks and accepted-import resume.

## 1.3.0-beta.3

- Show Amazon connection progress and errors beside Connect, validate settings before sign-in and provide a direct sign-in link when pop-ups are blocked.
- Share responsive page styling between Status and Setup; place Setup navigation above the status title and group checks under section headings.
- Put required API username/password in Credentials and additional connection fields in Advanced settings.
- Default the skill endpoint to the public audio URL origin plus `/ma-alexa-skill/`, with an optional override.

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
