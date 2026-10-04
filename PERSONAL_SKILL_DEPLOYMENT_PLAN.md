# Automate personal Alexa skill setup

Status: Beta.3 is merged and published in both repositories. Beta.4 onboarding, certificate and deployment-verification refinements are in skill PR #7 and add-on PR #33; publication awaits their reviews and CI. Live Amazon/Echo acceptance remains required before stable promotion.

## Summary

Extend the existing web app to create or update your personal Music Assistant skill, fill in its Amazon configuration, build its voice model, and enable development testing.

Use the chosen self-hosted sign-in approach. One initial Amazon login application registration is required; subsequent setup uses browser sign-in with automatic return. See [Amazon authorization requirements](https://developer.amazon.com/en-US/docs/alexa/smapi/get-access-token-smapi.html) and [registered callback requirements](https://www.developer.amazon.com/docs/login-with-amazon/dynamically-redirect-users.html).

## Implementation

- Add a guided setup: connect Amazon → select your existing skill or create one → review settings → deploy → verify completion.
- Use Amazon’s management APIs directly for deployment, replacing the web flow’s interactive command-line process.
- Update the selected skill by its saved ID. Never delete skills automatically or select one solely by name.
- Generate the endpoint, locale, voice model, AudioPlayer interface, optional APL interface, and certificate setting from the configured installation.
- Persist credentials, selected skill ID, and deployment progress under `/data`. Allow safe retries and report interrupted deployments after restart.
- Report success only after Amazon confirms the configuration, model build, and development enablement.

## Sign-in and interfaces

- Add settings for the Amazon login client ID, secret, and explicit public HTTPS callback URL.
- Add authorization start and callback routes, plus deployment start and status routes under `/setup`.
- Provide status/setup through Home Assistant ingress without a second app login; retain app authentication for the APIs and standalone deployments. Protect deployment controls with browser CSRF validation. Validate short-lived, single-use authorization state; keep credentials and codes out of logs.
- Use the configured callback address behind Nginx Proxy Manager. Keep tokens on your installation and support refresh and reconnection.
- Preserve the existing personal skill’s identity and unrelated configuration when updating it.

## Testing and documentation

- Test creating a skill, updating an existing skill, repeated deployment, duplicate names, failed builds, expired credentials, rejected callbacks, and restart recovery.
- Verify locale, APL, certificate settings, and HTTPS proxy compatibility.
- Run the existing regression suite and both supported container architectures.
- Complete a live Amazon deployment and Echo playback check before claiming full acceptance.
- Update both repositories’ setup instructions and this plan document, distinguishing one-time login registration from automated skill configuration.

## Defaults

- Development-stage personal skill; no publication or certification.
- Keep the configured locale and APL preference.
- Existing skills require explicit selection before the first update.
- Public HTTPS skill and audio endpoints remain required; Nginx Proxy Manager can provide them.
- Sign implementation commits with GitHub GPG key `C1E29FB983ECFB1A541B19BE152E7550E4916458`.

## Implementation findings and progress (3 October 2026)

- The old web setup spawned ASK CLI authorization, accepted pasted codes and could select/delete skills by name. The new web routes replace that flow entirely; manual CLI scripts are no longer called by the wizard.
- Amazon now marks direct interaction-model update APIs as unsupported and recommends [Skill Package Management](https://www.developer.amazon.com/en-US/docs/alexa/smapi/skill-package-api-reference.html). The implementation exports existing packages, preserves unrelated members/locales, and imports the reviewed package using Amazon's presigned storage URL. Creation uses the manifest API first so the skill ID can be persisted before import.
- Existing invocation names are preserved. The chosen locale's bundled intents/slots are deliberately replaced and clearly disclosed during review. Default and existing regional endpoints are updated together.
- Configuration includes explicit HTTPS callback and certificate type; status/setup use Home Assistant ingress on private port 8099. The public callback is `/ma-alexa-skill/setup/oauth/callback` and uses the existing core skill proxy route. No public status/setup proxy locations are required. Proxy access logs must omit callback query strings too.
- Tokens and package/job state are persisted privately under `/data`; the app supports refresh, single-use browser-bound OAuth state, CSRF-protected controls, interrupted imports and uncertain-create duplicate prevention.
- Changes made in Amazon between review and deployment are detected by a canonical exported-package comparison. Amazon confirmation requires successful package import, manifest/model builds, matching exported package and development enablement.
- The existing playback/status regression suite remains green. Additional API fixtures cover creation/redeployment, duplicate names, retained resources, failures, expired credentials, callback rejection, restart recovery and settings validation. All **80 combined tests** passed locally and in both ARM64 and AMD64 candidate images. HTTP/proxy, playback, concurrency, certificate-registry and graceful shutdown checks passed in both images. The add-on linter and new module/test static checks passed. A browser check completed review and deployment with simulated Amazon responses and no JavaScript errors; live acceptance remains pending.

## Remaining acceptance gate

A real Amazon account must complete the one-time security-profile registration and sign-in, deploy an existing personal skill, repeat the update without changing its ID, exercise restart/resume and verify Echo playback. Existing stable-1.2.0 device confirmation does not validate these new APIs. The owner has authorized merging and publishing beta candidates for live testing. Do not promote to a stable release until live acceptance passes.

## Ingress and status revision

- User requested `/status` and `/setup` without app authentication and through Home Assistant ingress. Added a private 8099 listener restricted to the raw Supervisor peer; forwarded headers cannot bypass this boundary. Ingress prefixes are retained in links, polling and browser cookies. API traffic remains on 5000 with its existing credentials.
- User requested the callback under the existing `/ma-alexa-skill/` route. The callback now accepts the OAuth return there, while connection completion requires the original ingress browser's cookie and CSRF token. Home Assistant itself need not be externally accessible.
- Status now checks public skill health, HTTPS stream-host connectivity and the current rewritten audio URL in a background cache, reporting TLS/DNS/timeouts/HTTP errors. Results describe add-on-side reachability; Echo acceptance remains necessary.

Ingress/diagnostics revision validation: **91 combined tests** passed locally and in both ARM64/AMD64 candidate images, including gateway spoofing rejection, ingress cookie paths, callback replay/original-browser completion, HTTPS failure diagnostics and caching. Add-on lint passed. Browser status→setup navigation and simulated deployment worked through the ingress prefix. Actual Home Assistant, Amazon and Echo acceptance remain pending.

## Web settings follow-up (3 October 2026)

- Move all 13 useful settings into the ingress setup page; generate the callback URL from the public skill origin instead of maintaining a separate editable value. Put API credentials, certificate selection and troubleshooting controls under Advanced.
- Remove the unused AWS region setting from the maintained add-on and application deployment examples.
- Store settings atomically with owner-only permissions in `/data/app-settings.json`. Import available legacy add-on options/environment values once, preserve web edits across restarts, and retain standalone environment bootstrap support.
- Keep secrets masked, retain them for blank inputs, provide explicit optional-secret removal and deliberate API-password reveal. Generate the initial add-on API password once.
- Apply playback/control settings on subsequent requests; never deploy merely because settings were saved. Block edits during a deployment, invalidate old reviews and pending sign-in, and reject stale browser saves.
- Validate persistence, migration, request authentication, callback derivation, secret handling and playback regressions; live Supervisor upgrade and Amazon acceptance remain pending.

- Container startup revealed that Flask ASK SDK imports a DynamoDB client even though this service does not use it. Keep an internal `us-east-1` compatibility default before importing that SDK; the unused user-facing AWS region option remains removed.

Web-settings validation: **108 combined tests** passed locally and in both ARM64/AMD64 candidate images. Both images passed real HTTP/proxy/playback/concurrency and shutdown checks. A simulated ingress browser saved settings and retained them on reload. Secret masking/retention/removal, stale saves, migration, file permissions, credential updates and deployment edit locking are covered. Real Supervisor upgrade/ingress and Amazon/Echo acceptance remain pending.

## PR review findings (3 October 2026)

- Document all three required Compose secret files; an empty Amazon secret file permits setup later through the wizard.
- Turn invalid stream rewrite inputs into failed URL diagnostics rather than a polling error, and preserve connected deployment status when current deployment settings are invalid.
- Keep pending Amazon sign-in when unrelated settings change; invalidate pending sign-in only when the Amazon client/callback configuration changes. Settings edits still invalidate the reviewed deployment.
- Persist an uncertain-import transition before submitting to Amazon, retaining it after timeouts, interruption and invalid operation responses. Block later deployments until manual reconciliation when the operation ID is unavailable; a valid saved operation ID still supports normal resume.
- Resume revalidates the saved vendor and development custom skill against the current Amazon connection before polling or enabling testing. An unrelated developer account cannot resume the saved operation. This binds recovery to a verified ownership context, not a newly introduced Amazon identity API.

Review-fix validation: **125 combined tests** passed locally and in ARM64/AMD64 candidate images, together with HTTP/proxy/playback/concurrency, certificate-registry and shutdown checks. New regressions cover invalid URL polling, connected status with invalid settings, OAuth-preserving edits, durable lost/invalid/interrupted import responses, definite rejection and recovery ownership. Review changes remain on the existing paired draft PRs; real Supervisor/Amazon/Echo acceptance remains pending.

## Follow-up review findings (4 October 2026)

- Add a protected owner action for uncertain imports: require the exact saved skill/attempt, explicit Amazon-confirmed terminal result and confirmation reference, revalidate the saved ownership context, and atomically persist an audit record before clearing uncertainty. Never equate owner confirmation with API-verified deployment or permit clearing merely because no local job is busy.
- Retain a temporary legacy Supervisor schema with migration-only labels for the first migration release so upgrade values survive until startup import. Web settings remain authoritative after migration; the obsolete AWS region option stays removed. Plan schema removal for a later release after verified migrations.
- The add-on plaintext-management comment targets an old pin: current ingress mode denies setup/status on 5000 even with Basic Auth and spoofed forwarded headers; private 8099 trusts only the raw Supervisor peer. Existing regression checks cover this boundary.

Follow-up validation: **140 combined tests** passed locally and in ARM64/AMD64 images with real HTTP/proxy/playback/concurrency, certificate and shutdown checks. Add-on metadata lint passed. A simulated ingress browser recorded a confirmed non-acceptance and required a fresh review. Tests cover terminal result validation, CSRF/authentication, stale attempts, ownership, active jobs, legacy state migration and failed persistence retaining both retry blocks. Live Supervisor migration and Amazon/Echo acceptance remain pending.

### Reconciliation concurrency review (4 October 2026)

- Snapshot the uncertain attempt and Amazon connection under the manager lock, then release it while checking ownership. Reacquire it and reject changes to attempt, skill, vendor, credentials, job state or shutdown before recording confirmation. Slow Amazon listing no longer holds status/settings behind that manager lock.
- Add deterministic concurrent status/settings tests and stale-attempt/ownership/connection checks. Add-on PR #30 was approved on its prior head; the synchronized pointer requires review of this follow-up.

Concurrency follow-up validation: **150 combined tests** passed locally and in ARM64/AMD64 images, including real HTTP/proxy/playback/concurrency, certificate and shutdown checks. Ruff and whitespace checks passed. Live Supervisor migration and Amazon/Echo acceptance remain pending.

### Home Assistant entry-path correction (4 October 2026)

- Owner reported Open Web UI showing the playback-listener denial instead of status. Supervisor appends `ingress_entry` to an ingress URL ending in `/`; the former `/status` entry therefore generates `//status`.
- Set the entry to relative `status`. Normalize leading slashes only after validating the raw Supervisor peer and ingress prefix so cached entry links open status while private playback APIs remain blocked.
- Regression coverage includes the actual doubled-slash WSGI path, status-page links, blocked playback paths and spoofed gateway headers. This report confirms the entry failure on a real installation; it does not establish Amazon/Echo deployment acceptance.

Entry-path validation: **151 combined tests** passed locally and in ARM64/AMD64 images, with HTTP/proxy/playback/concurrency, certificate and shutdown checks. Ruff and whitespace checks passed. The corrected entry still needs confirmation through the owner's Home Assistant Open Web UI button.

### Amazon connection feedback and consistent pages (4 October 2026)

- Owner reported Connect Amazon opening nothing. The existing handler closes its blank window when preparation fails and reports the failure above the settings, away from the button. First-use status also skipped OAuth prerequisite validation when no tokens existed. The exact installation error is not available locally.
- Validate prerequisites before first sign-in, display concrete configuration errors and connection progress beside Connect, and keep a direct Amazon sign-in link available when a popup is blocked or unavailable. Preserve the CSRF, callback-state and original-browser checks.
- Use one shared responsive style template for Status and Setup, preserving status polling and ingress-prefixed links. Browser preview uses fixtures; no live Amazon authorization is claimed.

Connection/style validation: **153 combined tests** passed locally and in ARM64/AMD64 images, including runtime HTTP/proxy/playback/concurrency, certificate and shutdown checks. JavaScript checks covered normal popup navigation, blocked-popup fallback, visible preparation errors and missing-settings feedback. A simulated ingress browser verified matching page layouts and prefixed links. Live owner sign-in remains to be tested.

- Beta.3 UI refinement: Status places the arrow-style Setup link above its title and groups checks into Public URL reachability, Alexa skill, Playback APIs, Echo Show display and Recent activity sections. Setup places API username/password and reveal in Credentials; public skill endpoint, callback, MA control URL/token move into Advanced. The public skill endpoint remains required for Amazon deployment. All 153 tests and connection JavaScript checks still pass.

- Beta.3 endpoint default: blank skill endpoint now derives from the public audio URL origin plus `/ma-alexa-skill/`; existing explicit endpoints remain overrides. Backend deployment, reachability and callback use the effective endpoint. The Setup placeholder and callback preview follow unsaved audio/override edits; saving persists a blank override so subsequent audio changes update the default.

Endpoint-default validation: **155 combined tests** passed locally and in ARM64/AMD64 images, with runtime HTTP/proxy/playback/concurrency, certificate and shutdown checks. Regressions cover default path construction, explicit overrides, derived callback origins and persistence across audio-URL changes. Ruff, whitespace and connection JavaScript checks pass.

- Move Amazon client ID, secret and optional removal into **Connect to Amazon**, with a local save control and **Connect** button. Keep the controls associated with the existing settings form so validation, secret retention, revision and CSRF protections stay consistent.


## Beta.4 follow-up (skill PR #7; add-on PR #33)

- Add LWA developer-console registration steps and the generated public callback to Connect to Amazon.
- Support Trusted, Trusted sub-domain and File certificate choices. Validate the public PEM file and upload/verify it through Amazon before enabling testing; preserve callback TLS validation.
- Deploy the maintained add-on artwork as both Alexa icon sizes across retained locales.
- Put feedback in the relevant settings, connection, selection or deployment section; show the connected account with a green tick.
- Wait for explicitly running builds and verify successful imports against the exported approved package when legacy build status fields are missing. Preserve failure and mismatch gates and resumable imports.
- Validation: 168 combined tests pass locally; live Amazon certificate deployment and owner-reported build scenario require retesting with the updated add-on.
