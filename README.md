# Music Assistant Alexa API add-on repository

[![Test](https://github.com/timlaing/music-assistant-alexa-api/actions/workflows/test.yml/badge.svg)](https://github.com/timlaing/music-assistant-alexa-api/actions/workflows/test.yml)
[![Lint](https://github.com/timlaing/music-assistant-alexa-api/actions/workflows/lint.yaml/badge.svg)](https://github.com/timlaing/music-assistant-alexa-api/actions/workflows/lint.yaml)
[![License](https://img.shields.io/github/license/timlaing/music-assistant-alexa-api)](LICENSE)

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=timlaing_music-assistant-alexa-api&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=timlaing_music-assistant-alexa-api)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=timlaing_music-assistant-alexa-api&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=timlaing_music-assistant-alexa-api)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=timlaing_music-assistant-alexa-api&metric=coverage)](https://sonarcloud.io/summary/new_code?id=timlaing_music-assistant-alexa-api)

[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=timlaing_music-assistant-alexa-api&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=timlaing_music-assistant-alexa-api)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=timlaing_music-assistant-alexa-api&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=timlaing_music-assistant-alexa-api)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=timlaing_music-assistant-alexa-api&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=timlaing_music-assistant-alexa-api)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=timlaing_music-assistant-alexa-api&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=timlaing_music-assistant-alexa-api)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=timlaing_music-assistant-alexa-api&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=timlaing_music-assistant-alexa-api)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=timlaing_music-assistant-alexa-api&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=timlaing_music-assistant-alexa-api)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=timlaing_music-assistant-alexa-api&metric=bugs)](https://sonarcloud.io/summary/new_code?id=timlaing_music-assistant-alexa-api)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=timlaing_music-assistant-alexa-api&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=timlaing_music-assistant-alexa-api)

This repository packages the [Music Assistant Alexa skill service](https://github.com/timlaing/music-assistant-alexa-skill) as a maintained Home Assistant Supervisor add-on. Install this repository for Home Assistant; use the skill repository for application development or standalone Docker deployment.

Stable **1.2.0** includes the merged [add-on fixes](https://github.com/timlaing/music-assistant-alexa-api/pull/28), [skill fixes](https://github.com/timlaing/music-assistant-alexa-skill/pull/1) and [publication repair](https://github.com/timlaing/music-assistant-alexa-api/pull/29). The maintainer confirmed playback works on a real Alexa device with the Nginx Proxy Manager configuration on 3 October 2026. Automated validation passed 46 combined tests and HTTP/concurrency/shutdown checks in ARM64 and AMD64 containers, plus lint, CodeQL and image builds. This confirmation covers the tested installation; it does not establish compatibility with every device or validate every optional feature.

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/timlaing/music-assistant-alexa-api)

## Add-on

This repository contains the following add-ons

### [Music Assistant Alexa API add-on](./music-assistant-alexa-api)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

Many Thanks to @alams154 for the API, this repo turns his good work into an add-on.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg

## Configuration

### Settings

For stable **1.3.0**, open the add-on **Web UI → Setup** through Home Assistant ingress to edit all application settings. The table below describes these web settings; older **1.2.0** installations use the add-on Configuration tab. Amazon credentials and the generated callback URL are covered in the [Skill Setup](#skill-setup). The public skill endpoint defaults to the public audio URL origin plus `/ma-alexa-skill/`; the Advanced endpoint field overrides this default. Music Assistant API credentials are in **Credentials**. Additional connection settings and troubleshooting controls are under **Advanced settings**.

Existing values are imported once from available legacy `/data/options.json` values and environment variables into `/data/app-settings.json`; later saves and restarts use that file. Secrets stay masked, with an explicit **Show current API password** action for connecting Music Assistant. Saving applies locally without deploying to Amazon. The unused AWS region option is removed. Persist and protect `/data` backups.

| Name                            | Description                                                                                                                                                     | Required |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| Music Assistant Hostname        | The external hostname, port and root URI to be used for Streams                                                                                                 | Y        |
| Alexa Skill Hostname            | Optional override for the public HTTPS skill endpoint; defaults to the public audio URL origin plus `/ma-alexa-skill/`                                          | N        |
| API Username                    | The username to be provided to Music Assistant for communication to this API, defaults to (ma-local-alexa-api)                                                  | Y        |
| API Password                    | The password to be provided to Music Assistant for communication to this API, if blank on start one will be generated                                           | N        |
| Alexa Skill Locale              | The locale used by the skill setup flow, defaults to en-US; must match the locale registered to your Echo devices (for example en-GB for UK-registered devices) | N        |
| Skip Stream URL Validation      | Skip the external stream reachability check when local network routing prevents it                                                                              | N        |
| Music Assistant Control API URL | optional local MA API address for mapped voice controls                                                                                                         | N        |
| Music Assistant API Token       | access token for the MA control API                                                                                                                             | N        |
| Enable Echo Show Display        | opt into APL display; defaults to false                                                                                                                         | N        |

### Alexa API

Use **Web UI → Setup** to create or update your personal skill as described in [Skill Setup](#skill-setup). Its public HTTPS endpoint reaches this add-on's root route through the NPM skill location. The add-on listens internally on **5000**; changing the Supervisor host port mapping does not change its internal port.

### Streams and Nginx Proxy Manager

Alexa needs public HTTPS access to the skill endpoint and audio stream on both screenless and APL devices.
Nginx Proxy Manager can provide both. Forward external HTTPS port **443** to
NPM; keep add-on port **5000** and Music Assistant stream port **8097** internal.
Direct internet forwarding of those two application ports is unnecessary.

| Address                       | NPM upstream              | Setup setting    |
| ----------------------------- | ------------------------- | ---------------- |
| `https://alexa.example.com`   | `http://<HA-LAN-IP>:5000` | `skill_hostname` |
| `https://streams.example.com` | `http://<MA-LAN-IP>:8097` | `ma_hostname`    |

Set Music Assistant's Alexa provider **API URL** to `http://<HA-LAN-IP>:5000`
without `/ma`. Configure its Basic Auth fields with the add-on API credentials.
This LAN API address is separate from the public skill and stream addresses.
Use a publicly trusted TLS certificate on NPM. Alexa's public skill endpoint
must accept signed POST requests without an additional NPM login/access list.

For a shared public hostname, configure these NPM custom locations. Stream routes preserve their full paths; the skill route strips its prefix.

| NPM location       | Forward to                | Path handling                                         | When needed                                                                 |
| ------------------ | ------------------------- | ----------------------------------------------------- | --------------------------------------------------------------------------- |
| `/ma-alexa-skill/` | `http://<HA-LAN-IP>:5000` | Strip `/ma-alexa-skill/`; forward to the add-on root. | Skill requests and Amazon setup callback.                                   |
| `/flow/`           | `http://<MA-LAN-IP>:8097` | Preserve the full path.                               | Music Assistant queue streams.                                              |
| `/pluginsource/`   | `http://<MA-LAN-IP>:8097` | Preserve the full path.                               | Plugin audio streams using this route.                                      |
| `/source/`         | `http://<MA-LAN-IP>:8097` | Preserve the full path.                               | Live sources, including iPhone audio via AirPlay Receiver.                  |
| `/announcement/`   | `http://<MA-LAN-IP>:8097` | Preserve the full path.                               | Announcement audio using this route.                                        |
| `/imageproxy/`     | `http://<MA-LAN-IP>:8097` | Preserve the full path.                               | Music Assistant artwork.                                                    |
| `/alexa/`          | `http://<HA-LAN-IP>:5000` | Preserve the full path, including `/alexa/intents`.   | Only if Music Assistant's Alexa provider API URL uses this public hostname. |
| `/ma/`             | `http://<HA-LAN-IP>:5000` | Preserve the full path, including `/ma/push-url`.     | Only if Music Assistant's Alexa provider API URL uses this public hostname. |

A dedicated stream hostname forwarding all paths to **8097** already covers the stream locations and needs no extra custom locations. A dedicated add-on hostname forwarding all paths to **5000** already covers `/alexa/` and `/ma/`; keep the core `/ma-alexa-skill/` route for the Amazon setup callback. `/status` and `/setup` are provided through Home Assistant ingress and need no public NPM locations.

If Music Assistant connects directly to the add-on LAN API URL, `/alexa/` and `/ma/` proxy locations are unnecessary. If it connects through the public proxy instead, set its Alexa provider **API URL** to the hostname's base URL (for example, `https://music.example.com`, without `/ma` or `/ma-alexa-skill`). Use the add-on API credentials in its Basic Auth fields and avoid an additional NPM authentication layer on these API locations. The optional Music Assistant control API on **8095** is separate from these routes.

The add-on supports a public audio URL path prefix without duplicating it when rewriting stream URLs. Changing the Supervisor host port mapping does not change internal port **5000**; adjust NPM's forwarding port and the LAN API URL to match the host mapping.

If a live stream returns 404, compare the same path through the public HTTPS hostname and directly against the internal Music Assistant stream server while the iPhone is actively streaming. Internal success with a public 404 points to proxy routing; a 404 from both requires investigation of the Music Assistant stream URL. The maintainer confirmed successful iPhone-to-Alexa playback on 6 October 2026 after adding `/source/` and correcting the NPM configuration. This confirms the tested installation, rather than every live-source configuration.

### Optional voice controls and Echo Show display

In 1.2.0, set `ma_api_url` to the local Music Assistant server API address (normally
`http://<MA-LAN-IP>:8095`) and `ma_api_token` to a Music Assistant access token.
These are optional for basic playback, and distinct from the public stream URL.
Open `/devices`, trigger a skill request from each Echo, and pair its opaque
Alexa device ID with the actual Music Assistant **player_id**, not its display
name. Device mappings persist at `/data/device_players.json`, and ASK credentials
at `/data/.ask`, across add-on upgrades.

Next, previous and start-over route to the mapped MA player. Pause, stop and
resume also synchronize mapped players while retaining Alexa AudioPlayer handling
and one-shot suppression of commands echoed back by MA.
Set `enable_apl: true` to opt into Echo Show artwork and controls; it defaults
to false. `skip_url_validation` remains false unless local routing prevents
this container from checking a stream which the Echo can reach publicly.

## Skill Setup

Create or update your personal Alexa development skill through the **Setup** page. You do not need to manually create the skill, import interaction-model JSON, configure interfaces or build it in the Alexa Developer Console. One-time **Login with Amazon (LWA) security-profile registration** is still required.

1. Configure the public HTTPS skill and audio routes in the NPM table above, then start the add-on. Open **Web UI** in Home Assistant and select **Set up personal Alexa skill →** on the status page. Setup uses Home Assistant ingress with no separate app login. For standalone Docker, open `/setup` and sign in with the app credentials.
2. In **Application settings**, enter the public audio URL and save. In **Credentials**, set or reveal the API username/password that Music Assistant will use. The **Public skill endpoint** field is also here, and defaults to the audio URL's origin plus `/ma-alexa-skill/`. Override it only when the skill is served from a different public host than your streams — for example when streams are on `https://streams.example.com` but the skill is on `https://alexa.example.com`. Save the endpoint before moving on: the callback URL on the next step is derived from it, and Amazon keeps that registered value until you change it.
3. In **Connect to Amazon**, follow the registration instructions and open the linked [Login with Amazon console](https://developer.amazon.com/loginwithamazon/console/site/lwa/overview.html). Create a security profile with the Amazon developer account associated with your Echo devices. The page's generated **Amazon callback URL** is derived from the public skill endpoint saved in step 2, not the audio URL. Copy it into the profile's **Web Settings → Allowed Return URLs**. It uses `https://<public-host>/ma-alexa-skill/setup/oauth/callback` and the existing skill proxy route.
4. Copy the profile's **Client ID** and **Client Secret** into **Connect to Amazon**, select **Save Amazon settings**, then **Connect**. Approve Amazon access and return to Setup; the connection finishes automatically. Allow pop-ups, or use **Continue to Amazon sign-in** if the window does not open. A green tick confirms connection.
5. In **Skill setup**, select the developer account and your existing personal skill, or explicitly choose **Create a new personal skill**. Set the Echo's locale and optional Echo Show display. Under **Advanced skill settings**, choose **Trusted** for a normal CA-issued certificate such as NPM Let's Encrypt, **Trusted sub-domain** for a wildcard certificate, or **File** for a self-signed development certificate with a public PEM upload. Select **Save skill settings**.
6. Select **Review settings**, check the skill ID/name, endpoint, locale, certificate and display preference, then select **Deploy approved settings**. The app configures the skill, imports/builds the voice model, applies the add-on icon and enables development testing. Saving settings alone does not deploy them. This creates a personal development skill; it does not publish it to the Alexa Skills Store.
7. In Music Assistant's Alexa provider, set **API URL** to `http://<HA-LAN-IP>:5000` (without `/ma`) and copy the API credentials from Setup. Return to **Status** to check URL reachability, then start playback in Music Assistant and test your Echo using the skill's displayed invocation name.

The callback and audio must be publicly reachable; Home Assistant's Setup and Status pages remain private through ingress. For standalone deployment, use your container's API address instead of the add-on LAN address.

### Migration release compatibility

Stable 1.3.0 keeps the legacy Supervisor schema with migration-only labels to preserve existing configuration during upgrade. Settings are imported once into `/data/app-settings.json`; all subsequent edits belong in ingress Setup. Later edits to the legacy fields are ignored. The obsolete AWS region option remains removed. Remove this temporary compatibility schema only in a later release once migration is verified.

### Troubleshooting

**The skill answers but the Echo stays silent.** Music Assistant reports the track as playing, the add-on logs an HTTP 200 for the `PlayAudio` request, and Alexa still fails with `MEDIA_ERROR_SERVICE_UNAVAILABLE` and `offsetInMilliseconds: 0`. Work through these in order:

1. **Read what Alexa actually did.** Open the Alexa app → **Alexa Privacy → Review Alexa History** and find the invocation. A request that never appears there never reached your add-on — either the deployed invocation name no longer matches what Music Assistant says (step 2), or it was lost in DNS, TLS or proxy routing rather than at playback.
2. **Check the invocation name.** Music Assistant starts playback with a scripted voice command that must address the skill's invocation name — `music assistant` in **every** locale for current releases. A skill deployed with an older `<language> radio` name never matches that command, so nothing appears in Alexa History either. In **Skill setup**, select **Review settings** and then **Deploy approved settings** to adopt the bundled model, then relearn the launch phrase. From the add-on release that bundles this fix onwards, the status page's **Invocation name** check compares the deployed name against Music Assistant's start command for the configured locale and fails on any mismatch.
3. **Confirm the stream URL is still live.** Music Assistant's `/flow/` queue URLs are one-shot: once a queue's flow session has streamed to the end, Music Assistant answers 404 for that stored URL. Recent skill versions validate a stored URL before handing it to Alexa and ask Music Assistant to resume the player for a fresh one, so a stale URL normally recovers rather than failing. If playback still fails after an idle period, check the add-on log for `Audio URL returned HTTP 404` — that means the stored URL was dead and the resume did not produce a replacement.
4. **Check the reachability colours honestly.** On the status page, `Stream host: HTTPS reachable (HTTP 404)` is the expected result for the bare stream origin — Music Assistant has no route at `/`, so a 404 proves TLS and routing work without claiming audio is servable. Test a real audio URL to confirm playback access. If that check turns red with a 502, the proxy accepted the connection but could not reach Music Assistant upstream.
5. **Verify the proxy forwards the full stream path.** `/flow/`, `/pluginsource/`, `/source/`, `/announcement/` and `/imageproxy/` must all preserve their full paths to port **8097**. A location that strips a prefix, or one that exists for the skill route only, silently breaks audio while the skill endpoint stays healthy.
6. **Trust the proxy's client address.** If requests traverse a reverse proxy, Home Assistant must trust its `X-Forwarded-For` or proxied requests are rejected. See the [NGINX Home Assistant SSL proxy example](./docs/nginx-ha-ssl-proxy/README.md) for the `use_x_forwarded_for` and `trusted_proxies` ranges a proxied setup needed.
7. **Collect logs for a report.** The add-on log around the failed request, the proxy's error log for the same seconds, and the Alexa History entry are usually enough. The skill's diagnostics download captures its own configuration and the read-only Music Assistant channel checks. Logs can be shared privately on Discord (timlaing) if you prefer.

#### Cloudflare or another CDN/WAF in front

**Cloudflare (or another CDN/WAF) between Amazon and your skill or stream host** can break audio while the skill itself stays healthy. Two reports of this failure class are in [#40](https://github.com/timlaing/music-assistant-alexa-api/issues/40). Work through these in order:

1. **Edge caching of `.mp3`.** Music Assistant's `/flow/<…>/<player>.mp3` URLs match Cloudflare's default cacheable extension list, so the edge can cache a live one-shot stream and replay a stale copy. Fetch a flow URL and read the `cf-cache-status` response header: it must be `DYNAMIC` or `MISS`, never `HIT`.
2. **Bot Fight Mode, security level and WAF rules.** These can answer Amazon's server-side fetches with an HTML/JS challenge (HTTP 403 or 503) instead of audio. The Echo cannot execute the challenge, and the failure looks identical to `MEDIA_ERROR_SERVICE_UNAVAILABLE` at offset 0.
3. **Certificate type.** With a Cloudflare edge certificate, the skill must use the **Trusted sub-domain** (wildcard) certificate option in **Skill setup**; the plain **Trusted** CA option left the simulator unable to reach the skill in [#40](https://github.com/timlaing/music-assistant-alexa-api/issues/40). Re-deploy with **Review settings → Deploy approved settings** after changing it.

**Bypass recipe.** Grey-cloud (set to DNS-only) the stream host so audio traffic bypasses the edge, or exclude `/flow/` from the cache and challenge rules. On the one affected setup that kept Cloudflare, the wildcard certificate option plus Cloudflare Tunnel → Nginx Proxy Manager worked; another reporter fixed playback by dropping Cloudflare Tunnels for DuckDNS.
