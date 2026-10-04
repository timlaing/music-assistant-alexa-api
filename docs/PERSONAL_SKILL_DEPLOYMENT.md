# Personal Alexa skill deployment

This feature is available on main in candidate **1.3.0-beta.3**. Stable **1.2.0** does not contain this wizard. Automated tests use Amazon API fixtures; live Amazon sign-in/deployment and Echo playback with the new wizard still need acceptance testing.

The web app creates or updates your **personal development skill** under your own Amazon developer account. It configures the endpoint and interfaces, imports and builds the bundled voice model, and enables development testing. It does not publish or certify a skill.

## One-time Amazon registration

1. Use the Amazon developer account associated with your Echo devices. Register a **Login with Amazon security profile** following [Amazon's SMAPI access-token guide](https://developer.amazon.com/en-US/docs/alexa/smapi/get-access-token-smapi.html).
2. Under the profile's **Web Settings**, register an **Allowed Return URL** of `https://alexa.example.com/ma-alexa-skill/setup/oauth/callback`, replacing the hostname with your public proxy hostname. The entire URL must match, including the path; use HTTPS on public port 443.
3. Copy the client ID and client secret into **Setup → Application settings**. This registration remains a manual prerequisite. The wizard handles the skill's developer-console configuration afterwards.

| Setup setting | Standalone bootstrap variable | Value |
|---|---|---|
| `lwa_client_id` | `LWA_CLIENT_ID` | Your security profile's client ID |
| `lwa_client_secret` | `LWA_CLIENT_SECRET` | The private client secret; never share it |
| Callback URL (read only) | Derived from `SKILL_HOSTNAME` | Origin of the skill URL plus `/ma-alexa-skill/setup/oauth/callback`; copy it into Amazon registration |
| `skill_hostname` | `SKILL_HOSTNAME` | Full public HTTPS skill endpoint, including any proxy prefix |
| `skill_certificate_type` | `SKILL_CERTIFICATE_TYPE` | `Trusted` for a normal NPM Let's Encrypt certificate; `Wildcard` for a wildcard certificate |
| `locale` | `LOCALE` | Echo's locale, matching a bundled voice model, such as `en-GB` |
| `enable_apl` | `ENABLE_APL` | Optional Echo Show display, disabled by default |
| `api_username` / `api_password` | `APP_USERNAME` / `APP_PASSWORD` | Playback/control API credentials; ingress pages use Home Assistant authentication |

All application settings are edited on Setup. API username and password are in **Credentials**, as Music Assistant needs them to authenticate with the API. Public skill endpoint, generated Amazon callback, Music Assistant control API URL/token, certificate type and skip-validation are under **Advanced settings**. The public skill endpoint remains required for Amazon deployment. Secrets are masked; a blank input retains the saved value, with explicit removal for the optional MA token and Amazon secret. **Show current API password** reveals only the provider password after a deliberate action, so it can be copied into Music Assistant. Saving updates local playback/control settings immediately; it never deploys to Amazon. API credential changes require updating Music Assistant. Reconnect Amazon after changing client credentials, and prepare a fresh review after any settings change. Pending sign-in is preserved for unrelated changes (such as locale) and is invalidated only when the Amazon client or callback configuration changes. Saving is blocked while deployment work is active.

Settings persist in owner-only `/data/app-settings.json` (override with `APP_SETTINGS_PATH`). Available legacy add-on options and environment values are imported once on add-on startup; the saved file takes precedence thereafter. This migration release retains the legacy Supervisor schema solely to preserve existing values until the importer runs. Those fields are labelled migration-only; after initial import, edit settings in ingress Setup, because later legacy edits are ignored. The obsolete AWS region option remains removed. Remove the compatibility schema only in a later release after migration coverage is verified. Back up existing settings before upgrading. Standalone environments remain bootstrap defaults until the first web save. AWS region configuration is removed from the app.

With the bundled Docker Compose file, create `./secrets/app_username.txt`, `./secrets/app_password.txt` and `./secrets/lwa_client_secret.txt` before starting the container. The Amazon secret file may be empty if you will enter it in Setup later, but it must exist even if you do not use the wizard; Compose refuses to start when a declared secret file is missing.

Standalone secrets may be supplied through mounted files using the environment-secret convention already used by the app. Persist `/data`, or set `SKILL_DEPLOYMENT_PATH` to a file in another persistent private volume. Existing ASK CLI credentials are not reused because they belong to a different OAuth client. Legacy CLI files may remain for manual administration.

## Home Assistant ingress and Nginx Proxy Manager

Open the add-on's **Web UI** inside Home Assistant. `/status` and `/setup`, including their polling and deployment controls, use Home Assistant ingress and require **no separate app username/password**. The private ingress listener uses **8099** and accepts only the Supervisor gateway. These pages are blocked on the external API listener, even with app credentials. Internal API/skill traffic still uses **5000**; its `/ma/` and `/alexa/` credentials remain unchanged. The standalone web app retains its existing app authentication.

Keep the existing `/ma-alexa-skill/` NPM route to port **5000**, stripping that prefix as described in the main guide. Register the public Amazon callback as **`https://alexa.example.com/ma-alexa-skill/setup/oauth/callback`**. It is covered by this same core skill route; no public `/setup` or `/status` proxy locations are needed. The app also recognizes the full callback path if your proxy preserves it. For a dedicated host that previously forwarded the root endpoint, add the core `/ma-alexa-skill/` location for this callback. Music Assistant stream routes still forward to **8097**.

Amazon sign-in opens in a separate browser window. Its public callback validates the short-lived, single-use state and retains the authorization code privately; it does not connect the account on its own. The wizard polls inside ingress and completes the token exchange only when the original browser presents its ingress-scoped sign-in cookie and CSRF token. The callback window closes when possible; otherwise close it and return to Home Assistant. Allow pop-ups for the wizard. If no window opens, use **Continue to Amazon sign-in** beside the Connect button. Connection progress and errors appear there too; missing client credentials or callback settings must be saved before connecting. No code needs copying and your Home Assistant URL does not have to be public.

Do not add a separate NPM access list to the callback: it is protected by OAuth state. Configure proxy access logging to omit callback query strings, or disable that location's access log, because the return contains a short-lived authorization code. Gunicorn and Werkzeug omit these query strings. Public HTTPS remains required for skill requests, callback and audio playback.

## URL verification on status

The ingress status page checks the configured skill endpoint through its `/health` path, the HTTPS stream host, and the current rewritten audio URL when a stream has been pushed. Green means a successful response (and confirmed add-on health for the skill endpoint). TLS, DNS, timeout, redirect or HTTP errors show a diagnostic. A stream host returning 404/405 is reachable but remains yellow until an actual audio URL is checked. Signed audio URL query strings are omitted from displayed results.

Checks run in the background, with short timeouts and a one-minute cache, so they do not block playback or the status UI. These checks originate from the add-on's network and validate certificates. A local DNS/proxy success alone does not prove Amazon/Echo reachability; keep the real-device acceptance check.

## Deploy your existing skill

1. Open the add-on Web UI through Home Assistant ingress, select **Setup**, fill in **Application settings** and save. There is no second app login or restart required. Copy the generated callback into your Amazon security profile.
2. Select **Connect Amazon**. Approve the requested skill/model management access. Amazon returns through the callback under `/ma-alexa-skill/`, and the ingress wizard finishes automatically; there is no code to copy.
3. Choose the developer account and your **existing personal skill**. The skill ID is shown to distinguish identical names. Only custom skills in development are listed. For a fresh installation, explicitly choose **Create a new personal skill** instead.
4. Select **Review settings**. The app exports the selected skill and prepares a package preserving other locales, permissions and unrelated files. The selected locale's voice model is replaced with the bundled Music Assistant model, while its existing invocation name is retained. A new English skill uses “music assistant”; new non-English skills retain the bundled locale's invocation name. Your endpoint replaces the default and any regional endpoints. AudioPlayer is enabled and the APL setting is applied.
5. Check the displayed name, skill ID, endpoint, locale, invocation name, certificate and APL preference. Select **Deploy approved settings** within ten minutes. Changes made in Amazon after review cause deployment to stop and request another review; avoid editing the skill concurrently during deployment.
6. Wait for Amazon to confirm the import, manifest/model build, exported package and development enablement. Then test playback on your Echo using the displayed invocation name. An API confirmation does not prove device playback or proxy reachability.

No skill is selected by name or deleted automatically. After creation the ID is saved, and subsequent updates reuse explicitly selected IDs. Creation is blocked if an ID is already saved or a previous creation request has an uncertain result. Refresh the account's skill list and select the existing skill before continuing.

## Recovery and privacy

Credentials, OAuth state, selected ID and job state are stored in `skill-deployment.json`; the reviewed package is stored alongside it as `skill-deployment.zip`. Both are written atomically with owner-only file permissions. Treat backups of `/data` as sensitive. The status API never returns tokens, authorization codes or the client secret. Home Assistant authenticates ingress access, and browser CSRF protection guards deployment controls. OAuth state expires after ten minutes and is single use; connection completion is bound to the original ingress browser.

Expired access tokens are refreshed automatically. If refresh is rejected, reconnect Amazon. A changed client registration invalidates the saved connection. A restarted worker marks in-progress work as interrupted. **Resume accepted import** revalidates access to the saved developer account and development custom skill before checking the saved Amazon operation; it does not create another skill. Reconnect the original developer account if that ownership context is unavailable. If no import was accepted, select the saved skill and review again. Failed builds remain unsuccessful; inspect the selected skill's build diagnostics in Amazon's developer console, correct settings and retry. Network failures during creation deliberately block another create attempt until an existing skill is explicitly selected. If Amazon may have accepted an import but its operation ID was not saved (lost response, shutdown or invalid response), the app persists an uncertain-import marker and blocks further previews/deployments across restarts. Use **Recover an uncertain import** in Setup after confirming the operation’s terminal result with Amazon. Reconnect the original developer account if necessary, type the saved skill ID, select success/failure/confirmed non-acceptance, provide Amazon’s confirmation reference or explanation without secrets, and explicitly confirm that no import is still running for this attempt. The protected action revalidates access to the saved vendor and skill, records this owner-confirmed result and time privately, and clears the marker atomically. It never declares API-verified deployment success or starts another import; prepare a fresh review afterwards. A running or unknown result, a stale attempt or an active local job cannot clear the block. Do not resubmit while the result is unknown. Automatic discovery of a missing operation ID is not implemented. Skill packages larger than 10 MiB are currently rejected.

The status page reports the saved verification time and ID. It is a record of the last deployment, not a continuous check of Amazon-side changes. Run a new review/deployment after making changes in the developer console.

## Acceptance still required

Test the wizard against a real Amazon account: sign in, select an existing skill, deploy twice to the same ID, restart during a build and resume, reconnect after revocation, then verify Echo playback through the public proxy. The earlier real-device confirmation for stable 1.2.0 validates playback, not this new deployment flow. Keep the candidate unmerged until those checks pass.
