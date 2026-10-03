# Automate personal Alexa skill setup

Status: Implementation in progress on `codex/personal-skill-deployment` in both repositories. Candidate 1.3.0-beta.1; live Amazon/Echo acceptance remains pending.

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
- Protect setup controls with the app’s configured authentication. Validate short-lived, single-use authorization state; keep credentials and codes out of logs.
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
- Configuration includes explicit HTTPS callback and certificate type; setup requires authentication and the public callback hostname. `/setup` and `/setup/` need port-5000 routing on shared NPM hosts. Proxy access logs must omit callback query strings too.
- Tokens and package/job state are persisted privately under `/data`; the app supports refresh, single-use browser-bound OAuth state, CSRF-protected controls, interrupted imports and uncertain-create duplicate prevention.
- Changes made in Amazon between review and deployment are detected by a canonical exported-package comparison. Amazon confirmation requires successful package import, manifest/model builds, matching exported package and development enablement.
- The existing playback/status regression suite remains green. Additional API fixtures cover creation/redeployment, duplicate names, retained resources, failures, expired credentials, callback rejection, restart recovery and settings validation. All **80 combined tests** passed locally and in both ARM64 and AMD64 candidate images. HTTP/proxy, playback, concurrency, certificate-registry and graceful shutdown checks passed in both images. The add-on linter and new module/test static checks passed. A browser check completed review and deployment with simulated Amazon responses and no JavaScript errors; live acceptance remains pending.

## Remaining acceptance gate

A real Amazon account must complete the one-time security-profile registration and sign-in, deploy an existing personal skill, repeat the update without changing its ID, exercise restart/resume and verify Echo playback. Existing stable-1.2.0 device confirmation does not validate these new APIs. Do not merge/promote this candidate until live acceptance passes.
