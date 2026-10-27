# Music Assistant Alexa API add-on

This maintained add-on packages the [Alexa skill service](https://github.com/timlaing/music-assistant-alexa-skill) for Home Assistant Supervisor on **aarch64** and **amd64**. Add `https://github.com/timlaing/music-assistant-alexa-api` to the Add-on Store repositories and install **Music Assistant Alexa API add-on**. The development wrapper bundled in the skill repository is a separate deployment.

Stable **1.2.0** includes the merged [add-on fixes](https://github.com/timlaing/music-assistant-alexa-api/pull/28), [skill fixes](https://github.com/timlaing/music-assistant-alexa-skill/pull/1) and [publication repair](https://github.com/timlaing/music-assistant-alexa-api/pull/29). The maintainer confirmed playback works on a real Alexa device with the Nginx Proxy Manager configuration on 3 October 2026. Automated validation passed 46 combined tests and HTTP/concurrency/shutdown checks in ARM64 and AMD64 containers, plus lint, CodeQL and image builds. This confirmation covers the tested installation; it does not establish compatibility with every device or validate every optional feature.

## How to use

1. Open **Web UI → Setup**, configure the public audio URL and save. The **Public skill endpoint** field sits alongside it and defaults to the audio URL's origin plus `/ma-alexa-skill/`; override it only when the skill is served from a different public host than your streams, and save it before copying the callback URL on the next step.
2. Save the API credentials and `locale` (default `en-US`); use **Show current API password** to copy the generated password into Music Assistant. The locale must match the locale registered to your Echo devices — for example `en-GB` for UK-registered devices — or Alexa rejects requests sent with an unexpected locale.
3. Follow [Skill Setup](https://github.com/timlaing/music-assistant-alexa-api#skill-setup): register the LWA security profile using Setup's callback URL, connect Amazon, select or create your personal skill, review and deploy. Manual skill/model configuration in the Alexa Developer Console is unnecessary.
4. In Music Assistant's Alexa provider, set **API URL** to the add-on LAN base URL, such as `http://<HA-LAN-IP>:5000`, without `/ma`, and provide the add-on Basic Auth credentials.

For stable **1.3.0**, edit application settings on **Web UI → Setup**. API credentials are in **Credentials**; optional control settings and troubleshooting controls are under **Advanced settings**. Legacy Supervisor fields are migration-only after upgrade.

## Configuration

Settings persist privately in `/data/app-settings.json`. On first start, available legacy add-on options and environment values are imported once; subsequent web edits take precedence after restarts. Secrets are masked and blank secret inputs retain existing values. Explicit removal is available for the optional MA token and Amazon secret. Changing API credentials requires updating Music Assistant; changing Amazon credentials requires reconnecting. Saving never deploys to Amazon.

| Option                | Description                                                                                                                                                    |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ma_hostname`         | Public HTTPS base URL for Music Assistant streams and local artwork. Required when MA supplies internal stream URLs.                                           |
| `skill_hostname`      | Optional public HTTPS skill endpoint override; blank defaults to the public audio URL origin plus `/ma-alexa-skill/`.                                          |
| `api_username`        | API username. Defaults to `ma-local-alexa-api`.                                                                                                                |
| `api_password`        | API password. A random value is generated and saved when left empty.                                                                                           |
| `locale`              | Alexa locale used by guided setup. Defaults to `en-US`; must match the locale registered to your Echo devices (for example `en-GB` for UK-registered devices). |
| `skip_url_validation` | Defaults to false. Skip only the server-side stream reachability check when local routing prevents it; Alexa still needs public HTTPS access.                  |
| `ma_api_url`          | optional local MA control API URL, normally `http://<MA-LAN-IP>:8095`. Unnecessary for basic playback.                                                         |
| `ma_api_token`        | MA access token needed when the control API requires authentication. Distinct from the add-on API credentials.                                                 |
| `enable_apl`          | opt into Echo Show artwork and controls. Defaults to false.                                                                                                    |

## Public HTTPS and Nginx Proxy Manager

| Address                       | Proxy upstream            | Add-on option    |
| ----------------------------- | ------------------------- | ---------------- |
| `https://alexa.example.com`   | `http://<HA-LAN-IP>:5000` | `skill_hostname` |
| `https://streams.example.com` | `http://<MA-LAN-IP>:8097` | `ma_hostname`    |

Expose NPM's HTTPS port **443** to the internet; keep add-on **5000** and MA stream **8097** internal. Alexa needs public HTTPS audio on both screenless and APL devices. Direct internet forwarding of application ports is unnecessary. Use publicly trusted TLS certificates and allow signed Alexa POST requests without an additional NPM login or access list on the skill proxy.

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

## Voice controls, persistence and status

Use `/devices` to map each opaque Alexa device ID to its actual MA `player_id`, rather than the player display name. With optional MA control credentials, next, previous and start-over route to MA. Pause, stop and resume also synchronize mapped players, while retaining Alexa AudioPlayer handling and one-shot suppression of commands echoed back by MA.

Device mappings persist at `/data/device_players.json`, and ASK credentials at `/data/.ask`, across add-on upgrades. `/health` checks process liveness without authentication; candidate status/setup pages use Home Assistant ingress without a second login; playback APIs retain the configured credentials. An idle state before the first pushed stream is normal.

Independent simultaneous streams remain an upstream limitation. The add-on container checks do not validate the skill repository's standalone Docker image or bundled development wrapper.

## Personal skill deployment

Stable **1.3.0** moves application settings into Setup, adds Amazon credentials and certificate selection, derives the callback URL automatically, and removes the unused AWS region setting. Open `/status` and `/setup` through the add-on Web UI in Home Assistant ingress, with no second app login. The private ingress port is 8099; APIs remain on 5000. Set the registered callback to `https://your-public-host/ma-alexa-skill/setup/oauth/callback`, covered by the existing core skill proxy route. No public `/setup` or `/status` locations are required. The status page checks public URL reachability in the background. See [Skill Setup](https://github.com/timlaing/music-assistant-alexa-api#skill-setup). The maintainer confirmed the setup flow was tested and working on 4 October 2026; this is owner-reported acceptance, rather than verification of every recovery scenario.

### Migration release compatibility

Stable 1.3.0 keeps the legacy Supervisor schema with migration-only labels to preserve existing configuration during upgrade. Settings are imported once into `/data/app-settings.json`; all subsequent edits belong in ingress Setup. Later edits to the legacy fields are ignored. The obsolete AWS region option remains removed. Remove this temporary compatibility schema only in a later release once migration is verified.

## Troubleshooting

### Which failure is this?

[#40](https://github.com/timlaing/music-assistant-alexa-api/issues/40) covered three separate faults with near-identical symptoms. Match yours before working the sequence below:

| What you see                                                                                                              | Failure class                                                                                                                                         | What to do                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Step 4 or the deployment fails with **"Amazon's exported package differs from the approved deployment"**                  | Package fingerprint mismatch: a bundled locale model without the custom slot list, differing icon URIs, or Amazon's optional `skill-package/` wrapper | Fixed by **1.3.7-beta.3** — update the add-on. The error now names the differing file and field. |
| Playback works, then fails after an idle period; the add-on log shows **`Audio URL returned HTTP 404`**                   | Stale one-shot `/flow/` URL                                                                                                                           | Fixed by **1.3.6** — update. If it still fails afterwards, work step 3 below.                    |
| The skill logs HTTP 200, Alexa fails at **`offsetInMilliseconds: 0`**, every status check is green and the log has no 404 | The Echo's fetch path: proxy, DNS or a CDN/WAF in front                                                                                               | Work the steps below, then [Isolate the broken hop](#isolate-the-broken-hop).                    |

**Every status-page check runs from the add-on's own network view.** It proves that the add-on, its proxy and Music Assistant are wired together — it cannot prove the path an Echo takes. Only a test on a real device does, which is why all the checks can pass while playback still fails. Checks that report **Unknown** for the Music Assistant API need `ma_api_url` and `ma_api_token`, which live in the add-on's **Configuration** tab rather than in the web Setup.

**The skill answers but the Echo stays silent.** Music Assistant shows the track as playing, the add-on logs HTTP 200 for the `PlayAudio` request, and Alexa still fails with `MEDIA_ERROR_SERVICE_UNAVAILABLE` and `offsetInMilliseconds: 0`. Work through these in order:

1. Open the Alexa app → **Alexa Privacy → Review Alexa History** and find the invocation. A request that never appears there never reached the add-on — either the deployed invocation name no longer matches what Music Assistant says (step 2), or it was lost in DNS, TLS or proxy routing rather than at playback.
2. Music Assistant starts playback with a scripted voice command that must address the skill's invocation name — `music assistant` in **every** locale for current releases. A skill deployed with an older `<language> radio` name never matches that command, so nothing appears in Alexa History. Re-deploy from **Skill setup**: select **Review settings**, then **Deploy approved settings**, to adopt the bundled model, then relearn the launch phrase. From the add-on release that bundles this fix onwards, the status page's **Invocation name** check compares the deployed name against Music Assistant's start command for the configured locale and fails on any mismatch.
3. Music Assistant's `/flow/` queue URLs are one-shot: once a flow session has streamed to the end, Music Assistant answers 404 for that stored URL. Recent skill versions validate a stored URL before handing it to Alexa and ask Music Assistant to resume the player for a fresh one. An add-on log line `Audio URL returned HTTP 404` means the stored URL was dead and no replacement was pushed.
4. `Stream host: HTTPS reachable (HTTP 404)` is the expected result for the bare stream origin — Music Assistant has no route at `/`, and the yellow row is healthy. A red 502 instead means the proxy accepted the connection but could not reach Music Assistant upstream.
5. A local resolver — AdGuard Home, Pi-hole, router DNS — that rewrites the public hostname to a LAN address makes every add-on reachability check resolve internally and test only the LAN loopback. The checks can be fully green while the Echo's path (public DNS → home IP → router hairpin/NAT-loopback) is broken, and the skill endpoint still works because Alexa's POSTs arrive from Amazon over the public path, bypassing the rewrite (issue #40). **How to check:** AdGuard Home's Query log during a failed playback — does the Echo's client query the hostname, and what answer does it get? **Fixes:** make the Echo use the rewriting resolver, enable hairpin/NAT-loopback on the router, or add a local DNS/host entry for the device.
6. `/flow/`, `/pluginsource/`, `/source/`, `/announcement/` and `/imageproxy/` must each preserve their full path to port **8097**; a location that strips a prefix breaks audio while the skill endpoint stays healthy.
7. If requests cross a reverse proxy, Home Assistant must trust its `X-Forwarded-For` or proxied requests are rejected. See the [NGINX Home Assistant SSL proxy example](https://github.com/timlaing/music-assistant-alexa-api/tree/main/docs/nginx-ha-ssl-proxy) for the ranges one setup needed.
8. Collect the add-on log around the failed request, the proxy's error log for the same seconds, and the Alexa History entry. The skill's diagnostics download adds its own configuration and the read-only Music Assistant channel checks. Logs can be shared privately on Discord (timlaing).

### Isolate the broken hop

When the sequence above has ruled everything out, three tests separate the remaining causes. All three come from closing [#40](https://github.com/timlaing/music-assistant-alexa-api/issues/40), where a correct proxy configuration and green checks hid a fault on the device path:

1. **Does the Echo's request reach you at all?** Start a playback that fails and watch the proxy access log at that moment (the NGINX add-on writes it to its add-on log; add `access_log /dev/stdout;` to the stream location if you don't see stream requests). No `GET /flow/…` line means the Echo never reached your proxy — the fault is DNS, hairpin/NAT-loopback or a CDN challenge in front (step 5 and the Cloudflare section below). A `200` line means it arrived and was served, so the problem is in the response itself. An error status points at the proxy → Music Assistant hop (step 6).
2. **Fetch the failing URL from outside your LAN.** Copy the `/flow/…` URL from the log and, on mobile data rather than Wi-Fi, run `curl -N -o /dev/null -w '%{http_code} %{size_download}\n' '<flow-url>'`. Bytes should download and `size_download` should keep climbing. A headers-only `200` with a stalled transfer means something between the origin and the internet is buffering or challenging the stream.
3. **Test hairpin/NAT-loopback explicitly.** From a LAN device, resolve the public hostname to your home public IP instead: `curl --resolve <host>:443:<home-public-ip> https://<host>/<path>`. Many routers do not loop LAN→WAN→LAN traffic back — exactly the gap that a local DNS rewrite (step 5) hides from every other check.

**Fastest confirmation:** if test 1 shows no line from the Echo, point the Echo at the resolver that rewrites the hostname to your LAN address (or add a local DNS/host entry for it) and retry. Playback starting immediately proves the diagnosis with no further digging.

### Cloudflare or another CDN/WAF in front

**Cloudflare (or another CDN/WAF) between Amazon and the skill or stream host** breaks audio while the skill itself stays healthy; two reports are in [#40](https://github.com/timlaing/music-assistant-alexa-api/issues/40).

1. **Edge caching of `.mp3`.** Music Assistant's `/flow/<…>/<player>.mp3` URLs match Cloudflare's default cacheable extension list, so the edge can cache a live one-shot stream and replay a stale copy. Fetch a flow URL and read the `cf-cache-status` response header: it must be `DYNAMIC` or `MISS`, never `HIT`.
2. **Bot Fight Mode, security level and WAF rules.** These can answer Amazon's server-side fetches with an HTML/JS challenge (HTTP 403 or 503) instead of audio. The Echo cannot execute the challenge, and the failure looks identical to `MEDIA_ERROR_SERVICE_UNAVAILABLE` at offset 0.
3. **Certificate type.** With a Cloudflare edge certificate, the skill must use the **wildcard / sub-domain** certificate option in the Alexa Developer Console; the "trusted CA" option left the simulator unable to reach the skill in [#40](https://github.com/timlaing/music-assistant-alexa-api/issues/40). The add-on's **Skill setup** maps this to **Trusted sub-domain**.
4. **Bypass recipe.** Grey-cloud (set to DNS-only) the stream host so audio traffic bypasses the edge, or exclude `/flow/` from the cache and challenge rules. In the #40 worked examples, the wildcard certificate option with Cloudflare Tunnel → Nginx Proxy Manager worked, and dropping Cloudflare Tunnels for DuckDNS restored playback on another setup.

#### Cloudflare Tunnel specifics

A tunnel changes both the failure modes and the fixes:

- **Tunneled hostnames are always proxied.** Cloudflare Tunnel requires the DNS record to be orange-clouded, so the grey-cloud bypass above is not available for that hostname. Use exclusions instead: a Cache Rule that bypasses cache for `/flow/`, `/pluginsource/`, `/source/`, `/announcement/` and `/imageproxy/`, and a WAF skip rule (or Bot Fight Mode off) for the skill and stream hostnames.
- **A tunnel removes port forwarding and NAT-loopback from the path.** Alexa's POSTs and the Echo's audio fetch reach the Cloudflare edge, and `cloudflared` dials out to your network — so a setup whose router cannot hairpin LAN→WAN→LAN traffic (step 5) works over a tunnel even though direct port forwarding does not. Moving the stream host onto a tunnel is one of the fixes for that failure.
- **Route the paths with a proxy, not with `cloudflared` alone.** `cloudflared` ingress rules match a path but never rewrite it, so the `/ma-alexa-skill/` prefix cannot be stripped on the way to the add-on's root routes — pointing a tunnel straight at the add-on serves that prefix to a 404. Keep the tunnel in front of Nginx Proxy Manager (or the NGINX Home Assistant SSL proxy) and reuse the location table above; the end-to-end worked example in [#40](https://github.com/timlaing/music-assistant-alexa-api/issues/40) used exactly that shape. See the repository's [`docs/cloudflare-tunnel`](https://github.com/timlaing/music-assistant-alexa-api/tree/main/docs/cloudflare-tunnel) example for a worked configuration and settings checklist.
- **Certificate type:** with Cloudflare's edge certificate, select **Trusted sub-domain** in **Skill setup** (item 3 above).
- **Diagnose on both sides:** the `cloudflared` access log shows whether the edge delivered the request and what the origin answered, while the proxy log shows whether the Echo's `GET /flow/…` arrived ([test 1 above](#isolate-the-broken-hop)). Together they locate the break in one pass.
