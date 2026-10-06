# Home Assistant Add-on: Music Assistant Alexa API add-on

This maintained add-on packages the [Alexa skill service](https://github.com/timlaing/music-assistant-alexa-skill) for Home Assistant Supervisor on **aarch64** and **amd64**. Add `https://github.com/timlaing/music-assistant-alexa-api` to the Add-on Store repositories and install **Music Assistant Alexa API add-on**. The development wrapper bundled in the skill repository is a separate deployment.

Stable **1.2.0** includes the merged [add-on fixes](https://github.com/timlaing/music-assistant-alexa-api/pull/28), [skill fixes](https://github.com/timlaing/music-assistant-alexa-skill/pull/1) and [publication repair](https://github.com/timlaing/music-assistant-alexa-api/pull/29). The maintainer confirmed playback works on a real Alexa device with the Nginx Proxy Manager configuration on 3 October 2026. Automated validation passed 46 combined tests and HTTP/concurrency/shutdown checks in ARM64 and AMD64 containers, plus lint, CodeQL and image builds. This confirmation covers the tested installation; it does not establish compatibility with every device or validate every optional feature.

## How to use

1. Open **Web UI → Setup**, configure the public audio URL and save. The skill endpoint defaults to that URL's origin plus `/ma-alexa-skill/`; override it under **Skill setup → Advanced skill settings** if needed.
2. Save the API credentials and `locale` (default `en-US`); use **Show current API password** to copy the generated password into Music Assistant.
3. Follow [Skill Setup](https://github.com/timlaing/music-assistant-alexa-api#skill-setup): register the LWA security profile using Setup's callback URL, connect Amazon, select or create your personal skill, review and deploy. Manual skill/model configuration in the Alexa Developer Console is unnecessary.
4. In Music Assistant's Alexa provider, set **API URL** to the add-on LAN base URL, such as `http://<HA-LAN-IP>:5000`, without `/ma`, and provide the add-on Basic Auth credentials.

For stable **1.3.0**, edit application settings on **Web UI → Setup**. API credentials are in **Credentials**; optional control settings and troubleshooting controls are under **Advanced settings**. Legacy Supervisor fields are migration-only after upgrade.

## Configuration

Settings persist privately in `/data/app-settings.json`. On first start, available legacy add-on options and environment values are imported once; subsequent web edits take precedence after restarts. Secrets are masked and blank secret inputs retain existing values. Explicit removal is available for the optional MA token and Amazon secret. Changing API credentials requires updating Music Assistant; changing Amazon credentials requires reconnecting. Saving never deploys to Amazon.

| Option | Description |
| --- | --- |
| `ma_hostname` | Public HTTPS base URL for Music Assistant streams and local artwork. Required when MA supplies internal stream URLs. |
| `skill_hostname` | Optional public HTTPS skill endpoint override; blank defaults to the public audio URL origin plus `/ma-alexa-skill/`. |
| `api_username` | API username. Defaults to `ma-local-alexa-api`. |
| `api_password` | API password. A random value is generated and saved when left empty. |
| `locale` | Alexa locale used by guided setup. Defaults to `en-US`. |
| `skip_url_validation` | Defaults to false. Skip only the server-side stream reachability check when local routing prevents it; Alexa still needs public HTTPS access. |
| `ma_api_url` | optional local MA control API URL, normally `http://<MA-LAN-IP>:8095`. Unnecessary for basic playback. |
| `ma_api_token` | MA access token needed when the control API requires authentication. Distinct from the add-on API credentials. |
| `enable_apl` | opt into Echo Show artwork and controls. Defaults to false. |

## Public HTTPS and Nginx Proxy Manager

| Address | Proxy upstream | Add-on option |
| --- | --- | --- |
| `https://alexa.example.com` | `http://<HA-LAN-IP>:5000` | `skill_hostname` |
| `https://streams.example.com` | `http://<MA-LAN-IP>:8097` | `ma_hostname` |

Expose NPM's HTTPS port **443** to the internet; keep add-on **5000** and MA stream **8097** internal. Alexa needs public HTTPS audio on both screenless and APL devices. Direct internet forwarding of application ports is unnecessary. Use publicly trusted TLS certificates and allow signed Alexa POST requests without an additional NPM login or access list on the skill proxy.

For a shared public hostname, configure these NPM custom locations. Stream routes preserve their full paths; the skill route strips its prefix.

| NPM location | Forward to | Path handling | When needed |
| --- | --- | --- | --- |
| `/ma-alexa-skill/` | `http://<HA-LAN-IP>:5000` | Strip `/ma-alexa-skill/`; forward to the add-on root. | Skill requests and Amazon setup callback. |
| `/flow/` | `http://<MA-LAN-IP>:8097` | Preserve the full path. | Music Assistant queue streams. |
| `/pluginsource/` | `http://<MA-LAN-IP>:8097` | Preserve the full path. | Plugin audio streams using this route. |
| `/source/` | `http://<MA-LAN-IP>:8097` | Preserve the full path. | Live sources, including iPhone audio via AirPlay Receiver. |
| `/announcement/` | `http://<MA-LAN-IP>:8097` | Preserve the full path. | Announcement audio using this route. |
| `/imageproxy/` | `http://<MA-LAN-IP>:8097` | Preserve the full path. | Music Assistant artwork. |
| `/alexa/` | `http://<HA-LAN-IP>:5000` | Preserve the full path, including `/alexa/intents`. | Only if Music Assistant's Alexa provider API URL uses this public hostname. |
| `/ma/` | `http://<HA-LAN-IP>:5000` | Preserve the full path, including `/ma/push-url`. | Only if Music Assistant's Alexa provider API URL uses this public hostname. |

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
