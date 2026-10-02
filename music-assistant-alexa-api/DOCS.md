# Home Assistant Add-on: Music Assistant Alexa API add-on

## How to use

- Configure the external Music Assistant hostname used for public stream URLs.
- Configure the public Alexa skill hostname if you want to use guided skill setup.
- Start the add-on and open its Web UI. The status page links to guided setup, the simulator, and invocation logs.
- Provide the configured API username and password to Music Assistant.

## Configuration

| Option | Description |
| --- | --- |
| `ma_hostname` | Public HTTPS hostname used to rewrite Music Assistant stream and artwork URLs. |
| `skill_hostname` | Public HTTPS endpoint Alexa uses to reach the skill. Required for guided setup. |
| `api_username` | Username Music Assistant uses for the add-on API. |
| `api_password` | API password. A random value is generated and saved when left empty. |
| `aws_default_region` | AWS region used by ASK CLI. Defaults to `us-east-1`. |
| `locale` | Alexa locale used by guided setup. Defaults to `en-US`. |
| `skip_url_validation` | Skips the server-side stream URL reachability check when enabled. |

## Proxy URLs and voice controls

Use public HTTPS skill and stream URLs through Nginx Proxy Manager. Only NPM
needs internet-facing 443; add-on 5000 and MA stream 8097 remain internal.
The MA Alexa provider's API URL is the add-on LAN base URL without `/ma`.

| Option | Description |
| --- | --- |
| `ma_api_url` | Optional MA control API URL, normally local port 8095. |
| `ma_api_token` | Optional MA access token required by authenticated servers. |
| `enable_apl` | Opt into Echo Show display; defaults to false. |

Use `/devices` to map Alexa IDs to MA player IDs. `/health` checks process
liveness without authentication; status API pages require the API credentials.
An idle status before the first pushed stream is normal.

A release candidate does not establish live-device acceptance. See the root
repository's `docs/UPDATE_PLAN.md` for the validation record and release gates.
