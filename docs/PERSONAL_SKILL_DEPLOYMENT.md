# Personal Alexa skill deployment

This feature is implemented on the personal-skill-deployment branch for candidate **1.3.0-beta.1**. Stable **1.2.0** does not contain this wizard. Automated tests use Amazon API fixtures; live Amazon sign-in/deployment and Echo playback with the new wizard still need acceptance testing.

The web app creates or updates your **personal development skill** under your own Amazon developer account. It configures the endpoint and interfaces, imports and builds the bundled voice model, and enables development testing. It does not publish or certify a skill.

## One-time Amazon registration

1. Use the Amazon developer account associated with your Echo devices. Register a **Login with Amazon security profile** following [Amazon's SMAPI access-token guide](https://developer.amazon.com/en-US/docs/alexa/smapi/get-access-token-smapi.html).
2. Under the profile's **Web Settings**, register an **Allowed Return URL** of `https://alexa.example.com/setup/oauth/callback`, replacing the hostname with your public proxy hostname. The entire URL must match, including the path; use HTTPS on public port 443.
3. Copy the client ID and client secret into your installation's options. This registration remains a manual prerequisite. The wizard handles the skill's developer-console configuration afterwards.

| Home Assistant option | Standalone environment variable | Value |
|---|---|---|
| `lwa_client_id` | `LWA_CLIENT_ID` | Your security profile's client ID |
| `lwa_client_secret` | `LWA_CLIENT_SECRET` | The private client secret; never share it |
| `lwa_redirect_uri` | `LWA_REDIRECT_URI` | Exact registered `https://…/setup/oauth/callback` URL |
| `skill_hostname` | `SKILL_HOSTNAME` | Full public HTTPS skill endpoint, including any proxy prefix |
| `skill_certificate_type` | `SKILL_CERTIFICATE_TYPE` | `Trusted` for a normal NPM Let's Encrypt certificate; `Wildcard` for a wildcard certificate |
| `locale` | `LOCALE` | Echo's locale, matching a bundled voice model, such as `en-GB` |
| `enable_apl` | `ENABLE_APL` | Optional Echo Show display, disabled by default |
| `api_username` / `api_password` | `APP_USERNAME` / `APP_PASSWORD` | Required authentication for deployment controls |

Standalone secrets may be supplied through mounted files using the environment-secret convention already used by the app. Persist `/data`, or set `SKILL_DEPLOYMENT_PATH` to a file in another persistent private volume. Existing ASK CLI credentials are not reused because they belong to a different OAuth client. Legacy CLI files may remain for manual administration.

## Nginx Proxy Manager

Keep the skill and stream routes described in the main setup guide. In addition, route **`/setup` and `/setup/`**, preserving the paths, to the add-on's internal port **5000**. This includes **`/setup/oauth/callback`**. A dedicated proxy host forwarding all paths to port 5000 already covers these routes. On a shared hostname, add `/setup` and `/setup/` locations alongside the existing skill prefix and `/alexa/` / `/ma/` routes. Music Assistant stream routes still forward to **8097**.

Open `https://alexa.example.com/setup` on the **same public hostname as the callback**, rather than opening the LAN Web UI to connect Amazon. Keep app authentication enabled. The callback uses browser sign-in state and the app credentials; do not configure a separate NPM access list for it. Protect proxy logs too: the Amazon callback contains a short-lived authorization code in its query string. The add-on's Gunicorn access logs omit query strings; configure NPM access logging to omit them for `/setup/oauth/callback`, or disable that location's access log. HTTPS certificates and public access are still required for skill requests and audio playback.

## Deploy your existing skill

1. Restart after saving the options, open the public `/setup` page, and authenticate with the app credentials.
2. Select **Connect Amazon**. Approve the requested skill/model management access. Amazon returns to the app automatically; there is no code to copy.
3. Choose the developer account and your **existing personal skill**. The skill ID is shown to distinguish identical names. Only custom skills in development are listed. For a fresh installation, explicitly choose **Create a new personal skill** instead.
4. Select **Review settings**. The app exports the selected skill and prepares a package preserving other locales, permissions and unrelated files. The selected locale's voice model is replaced with the bundled Music Assistant model, while its existing invocation name is retained. A new English skill uses “music assistant”; new non-English skills retain the bundled locale's invocation name. Your endpoint replaces the default and any regional endpoints. AudioPlayer is enabled and the APL setting is applied.
5. Check the displayed name, skill ID, endpoint, locale, invocation name, certificate and APL preference. Select **Deploy approved settings** within ten minutes. Changes made in Amazon after review cause deployment to stop and request another review; avoid editing the skill concurrently during deployment.
6. Wait for Amazon to confirm the import, manifest/model build, exported package and development enablement. Then test playback on your Echo using the displayed invocation name. An API confirmation does not prove device playback or proxy reachability.

No skill is selected by name or deleted automatically. After creation the ID is saved, and subsequent updates reuse explicitly selected IDs. Creation is blocked if an ID is already saved or a previous creation request has an uncertain result. Refresh the account's skill list and select the existing skill before continuing.

## Recovery and privacy

Credentials, OAuth state, selected ID and job state are stored in `skill-deployment.json`; the reviewed package is stored alongside it as `skill-deployment.zip`. Both are written atomically with owner-only file permissions. Treat backups of `/data` as sensitive. The status API never returns tokens, authorization codes or the client secret. Authentication and browser CSRF protection guard deployment controls; OAuth state expires after ten minutes and is single use, bound to the connecting browser.

Expired access tokens are refreshed automatically. If refresh is rejected, reconnect Amazon. A changed client registration invalidates the saved connection. A restarted worker marks in-progress work as interrupted. **Resume accepted import** checks the saved Amazon operation instead of creating another skill. If no import was accepted, select the saved skill and review again. Failed builds remain unsuccessful; inspect the selected skill's build diagnostics in Amazon's developer console, correct settings and retry. Network failures during creation deliberately block another create attempt until an existing skill is explicitly selected. Skill packages larger than 10 MiB are currently rejected.

The status page reports the saved verification time and ID. It is a record of the last deployment, not a continuous check of Amazon-side changes. Run a new review/deployment after making changes in the developer console.

## Acceptance still required

Test the wizard against a real Amazon account: sign in, select an existing skill, deploy twice to the same ID, restart during a build and resume, reconnect after revocation, then verify Echo playback through the public proxy. The earlier real-device confirmation for stable 1.2.0 validates playback, not this new deployment flow. Keep the candidate unmerged until those checks pass.
