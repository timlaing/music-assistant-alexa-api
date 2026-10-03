# Alexa add-on 1.2.0 update plan

## Verified baseline and upstream findings (2 October 2026)

The local checkout started at 1dc34a2 (add-on 1.0.3, skill 82ad59c).
Implementation starts from GitHub main a1715dd (1.1.0, skill cd07e77).
Latest upstream is 8c1650577b2ebd81a34da58e180506643decc9e2 (0.0.39-beta).
It adds shared storage, device mapping, voice controls, resume offsets and optional APL.
Use the existing fork https://github.com/timlaing/music-assistant-alexa-skill,
maintenance branch addon-stability-1.2.0; pin the tested fork commit in the submodule.

Upstream's merged Home Assistant wrapper remains labelled NOT WORKING. PRs 69 and
78 remain open; the latter proposes a Nabu Casa webhook but still needs public
stream URLs. Neither is an accepted replacement for this maintained wrapper.
Nginx Proxy Manager is already supported: public HTTPS on 443 reaches NPM;
NPM forwards internally to this add-on on 5000 and MA streams on 8097. Direct
internet forwarding of 5000 or 8097 is unnecessary. Both skill requests and
streams must remain reachable through public HTTPS. Use separate proxy hosts;
also test existing custom-location/path-prefix configurations.

## Approved implementation

- Preserve add-on slug, credentials, existing options, image names and both architectures.
- Use latest upstream plus fixes in the fork, rather than build-time application patches.
- One Gunicorn gthread process with eight threads; direct internal status/store reads.
- Request-local APL capability and metadata; locked independent MA/Alexa stores.
- Shared URL parser supporting HTTPS, bare hosts, ports, IPv6 and path prefixes.
- Never enqueue/restart the current stream on completion/failure: MA owns flow sequencing.
- Optional MA API URL/token and APL options; map devices persistently under /data.
- Preserve ASK credentials under /data/.ask. Add a secret-free /health endpoint.
- Bind internal port 5000 independently of external Supervisor port mappings.
- Redact all option passwords/tokens; preserve Gunicorn signal handlers and Alexa verification.
- Pin base-image digests and runtime requirements, upgrade Gunicorn to 26.2.0.
- Keep Lint and Builder separate; require runtime tests before publication.
- Release candidate 1.2.0-beta.1; stable 1.2.0 only after live HA/Echo acceptance.

## Issues and acceptance criteria

Local issues 22/27: loopback deadlock; 23: unexplained process crash; 11: old missing
/alexa/intents route; 9: independently verify port/status/certificate symptoms.
Missing OAuth endpoints alone do not imply this skill requires account linking.
Upstream issues 79/80: stale URL enqueue causes announcements/queues to repeat.
Do not claim the crash fixed without evidence. Capture Python faults, process
exits/signals and dependency versions. Compare baseline and updated containers.

Test authenticated APIs, idle state, invalid JSON, concurrent requests and APL
isolation; push-to-play metadata integrity; URL prefix/encoding/artwork behavior;
queue completion, announcements, live radio, pause/resume, next/previous/start-over
and echo suppression; mapping persistence and absent/invalid MA credentials.
Build/run amd64 and aarch64 and explicitly test NPM-style forwarded requests.
Target MA stable [2.10.5](https://github.com/music-assistant/server/releases/tag/2.10.5),
released 2 October 2026 at 11:48 UTC (reverified 3 October against the official
release metadata). Live device tests remain a release gate.
Independent simultaneous streams remain an upstream limitation outside this release.

## Execution evidence

- Reused the existing fork `timlaing/music-assistant-alexa-skill` (the originally
  proposed `-prototype` name was not its actual name).
- Baseline ARM image 1.1.0: Python 3.14.5/Gunicorn 26.0.0; registry initialization
  and repeated ordinary HTTP requests succeeded. Issue 23 remains unreproduced.
- Baseline failed the 10-second SIGTERM shutdown check. Removing import-time
  signal replacement makes the updated Gunicorn worker terminate cleanly.
- Added a worker-exit hook to reap ASK subprocesses in separate process groups.
- Discovered upstream's simulator headers could disable signature verification
  on the public root without authentication. Restricted simulation to valid API
  credentials; unsigned Alexa requests and unauthenticated bypasses are rejected.
- Updated runtime: Python 3.14.8, Gunicorn 26.2.0, ASK CLI 2.30.7; base digests
  are pinned in build.yaml and Python packages in requirements.lock.
- Implementation commits signed with GitHub GPG key
  `C1E29FB983ECFB1A541B19BE152E7550E4916458`.
- Application fork revision: `a88b7e9`, based on upstream `8c16505`.
  The add-on gitlink pins this tested commit on `addon-stability-1.2.0`.
- Fixed APL rendering/refresh to preserve external provider artwork as well as
  local artwork normalized at the MA push endpoint.
- Final local validation: 46 tests passed natively and in both aarch64 and amd64
  containers built from the pinned bases and lock. Certificate registry startup,
  real HTTP launch/play, authentication, idle state, intents, NPM-style forwarded
  headers, 40 concurrent reads and unsigned-request rejection passed. Both
  Gunicorn containers exited with status 0 within the 10-second SIGTERM limit.
- Actionlint 1.7.12, Python import checks, shell syntax and git whitespace checks
  passed. Separate Runtime Tests now gate the Builder before image publication.

- CI exposed a linter schema that rejects OCI digests even in v2.21.1. The Lint
  workflow now runs that pinned upstream source with only the image-reference
  regex extended for strict SHA256 digests; all other checks remain intact.
- Builder 2026.09.0 deprecates the old action and no longer publishes its builder
  image. Migrated to its supported build-image action on native ARM64/AMD64
  runners; retained separate Lint/Builder workflows and runtime gates.

## PR review findings (3 October 2026)

- Added root requirements_all.txt and the add-on .dockerignore to build-change
  detection; changes to either now trigger runtime tests and builds.
- Disabled checkout credential persistence in Builder, Runtime Tests and Lint;
  initialization and lint default to contents: read.
- Split read-only PR image builds from main-branch publication. Only the publisher
  grants packages: write/OIDC and supplies the registry token to the builder.
- Kept MA 2.10.5 as the hardware acceptance target: the review's 2.10.4 claim was
  stale, as the official stable release was published before the original plan.
- Dependency PRs 25/26 contain no actionable inline review comments. Their version
  updates are incorporated in PR 28; they remain open pending the beta update.

## Remaining release acceptance

Automated tests use simulated events and mocked MA commands; no live HA, Echo,
Amazon certificate fetch or deployed NPM/router test was available in this run.
Before stable release, install the beta on HA with MA 2.10.5 and check:

- Existing options and ASK credentials survive restart/update; device mappings persist.
- Separate NPM HTTPS hosts reach the skill and streams; verify a real signed Alexa
  invocation and playable audio externally, including artwork and path prefixes.
- Finite queues, announcements and radio do not repeat at completion/failure.
- Mapped devices handle pause/resume offsets and next/previous/start-over with
  optional MA credentials; verify echo suppression on real Alexa/MA round trips.
- APL opt-in behaves correctly on a supported Echo and concurrent screenless device.
- Observe logs/fault diagnostics for issue 23, whose original crash was not reproduced.

This is an experimental `1.2.0-beta.1` candidate. Stable publication remains gated
on the above hardware acceptance.

## Documentation consistency follow-up (3 October 2026)

[Skill documentation PR #2](https://github.com/timlaing/music-assistant-alexa-skill/pull/2)
on `docs/home-assistant-addon` updates README, manual setup, compatibility,
limitations and the bundled wrapper's README to direct Supervisor users to the
maintained add-on repository. The add-on README/DOCS use matching public HTTPS
routing, lowercase Supervisor options, optional MA control credentials, player-ID
mapping, persistence paths and APL defaults. The 1.2.0-beta.1 features are explicitly
candidate-only, with automated validation distinguished from live acceptance.
The historical upstream-wrapper finding above does not describe the maintained
Home Assistant add-on's current packaging or test results.
