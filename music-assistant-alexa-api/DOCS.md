# Home Assistant Add-on: Music Assistant Alexa API add-on

This maintained add-on packages the [Alexa skill service](https://github.com/timlaing/music-assistant-alexa-skill) for Home Assistant Supervisor on **aarch64** and **amd64**. Add `https://github.com/timlaing/music-assistant-alexa-api` to the Add-on Store repositories and install **Music Assistant Alexa API add-on**. The development wrapper bundled in the skill repository is a separate deployment.

The experimental **1.2.0-beta.1** candidate is tracked in [add-on PR #28](https://github.com/timlaing/music-assistant-alexa-api/pull/28) and [skill PR #1](https://github.com/timlaing/music-assistant-alexa-skill/pull/1). Its 46 combined tests and HTTP/concurrency/shutdown checks passed in ARM64 and AMD64 add-on containers; lint, CodeQL and image builds also passed. Live HA/Echo/NPM acceptance is required before stable release. An open PR does not establish that the candidate has been published. The candidate-only options below require that version.

## How to use

1. Configure `ma_hostname` and `skill_hostname` with the public HTTPS stream and skill URLs described below.
2. Set the API credentials and `locale` (default `en-US`), start the add-on and open its Web UI.
3. Select **Setup** for guided Alexa authorization and skill/model creation or update. The manual alternative is described in the [repository README](https://github.com/timlaing/music-assistant-alexa-api#skill-setup).
4. In Music Assistant's Alexa provider, set **API URL** to the add-on LAN base URL, such as `http://<HA-LAN-IP>:5000`, without `/ma`, and provide the add-on Basic Auth credentials.

Supervisor uses the lowercase options below; uppercase environment variables in the skill's standalone Docker guide are not Supervisor option names.

## Configuration

| Option | Description |
| --- | --- |
| `ma_hostname` | Public HTTPS base URL for Music Assistant streams and local artwork. Required when MA supplies internal stream URLs. |
| `skill_hostname` | Public HTTPS endpoint Alexa uses to reach the skill. Required for guided setup. |
| `api_username` | API username. Defaults to `ma-local-alexa-api`. |
| `api_password` | API password. A random value is generated and saved when left empty. |
| `aws_default_region` | ASK CLI region. Defaults to `us-east-1`. |
| `locale` | Alexa locale used by guided setup. Defaults to `en-US`. |
| `skip_url_validation` | Defaults to false. Skip only the server-side stream reachability check when local routing prevents it; Alexa still needs public HTTPS access. |
| `ma_api_url` | Candidate: optional local MA control API URL, normally `http://<MA-LAN-IP>:8095`. Unnecessary for basic playback. |
| `ma_api_token` | Candidate: MA access token needed when the control API requires authentication. Distinct from the add-on API credentials. |
| `enable_apl` | Candidate: opt into Echo Show artwork and controls. Defaults to false. |

## Public HTTPS and Nginx Proxy Manager

| Address | Proxy upstream | Add-on option |
| --- | --- | --- |
| `https://alexa.example.com` | `http://<HA-LAN-IP>:5000` | `skill_hostname` |
| `https://streams.example.com` | `http://<MA-LAN-IP>:8097` | `ma_hostname` |

Expose NPM's HTTPS port **443** to the internet; keep add-on **5000** and MA stream **8097** internal. Alexa needs public HTTPS audio on both screenless and APL devices. Direct internet forwarding of application ports is unnecessary. Use publicly trusted TLS certificates and allow signed Alexa POST requests without an additional NPM login or access list on the skill proxy.

Separate hosts simplify configuration. A skill location such as `/ma-alexa-skill/` must strip that prefix when proxying to the add-on root; stream locations preserve their paths. The candidate supports a public stream URL path prefix without duplicating it during rewriting. Changing the Supervisor host port mapping does not change internal service port 5000; update the LAN API URL and NPM forwarding port if you change that mapping.

If Music Assistant connects directly to the add-on LAN API URL above, no NPM locations are needed for `/alexa/` or `/ma/`. If it connects through a shared public hostname instead, set its Alexa provider **API URL** to that hostname's base URL (for example, `https://music.example.com`, without `/ma` or `/ma-alexa-skill`) and add these NPM custom locations:

| Location | Forward to | Path handling |
| --- | --- | --- |
| `/alexa/` | `http://<HA-LAN-IP>:5000` | Preserve `/alexa/`, including `/alexa/intents`. |
| `/ma/` | `http://<HA-LAN-IP>:5000` | Preserve `/ma/`, including `/ma/push-url`. |

Use the add-on's API username and password in Music Assistant's Basic Auth fields; avoid an additional NPM authentication layer on these API locations. These locations reach the add-on API, not the MA stream server on 8097 or the optional control API on 8095. A dedicated proxy host forwarding all paths to the add-on on 5000 already covers them and needs no custom API locations.

## Candidate voice controls, persistence and status

Use `/devices` to map each opaque Alexa device ID to its actual MA `player_id`, rather than the player display name. With optional MA control credentials, next, previous and start-over route to MA. Pause, stop and resume also synchronize mapped players, while retaining Alexa AudioPlayer handling and one-shot suppression of commands echoed back by MA.

Device mappings persist at `/data/device_players.json`, and ASK credentials at `/data/.ask`, across add-on upgrades. `/health` checks process liveness without authentication; status pages and APIs require the configured credentials. An idle state before the first pushed stream is normal.

Independent simultaneous streams remain an upstream limitation. See `docs/UPDATE_PLAN.md` in the [candidate update PR](https://github.com/timlaing/music-assistant-alexa-api/pull/28) for the validation record and remaining release gates. The add-on container checks do not validate the skill repository's standalone Docker image or bundled development wrapper.
