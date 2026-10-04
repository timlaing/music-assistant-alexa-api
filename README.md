# Music Assistant Alexa API add-on repository

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

For candidate **1.3.0-beta.3**, open the add-on **Web UI → Setup** through Home Assistant ingress to edit all application settings. The table below describes these web settings; stable **1.2.0** still uses the add-on Configuration tab. Amazon credentials and the generated callback URL are covered in the [deployment guide](docs/PERSONAL_SKILL_DEPLOYMENT.md). Music Assistant API credentials are in **Credentials**. Additional connection settings and troubleshooting controls are under **Advanced settings**.

Existing values are imported once from available legacy `/data/options.json` values and environment variables into `/data/app-settings.json`; later saves and restarts use that file. Secrets stay masked, with an explicit **Show current API password** action for connecting Music Assistant. Saving applies locally without deploying to Amazon. The unused AWS region option is removed. Persist and protect `/data` backups.

| Name | Description | Required |
| ---- | ----------- | -------- |
| Music Assistant Hostname | The external hostname, port and root URI to be used for Streams | Y |
| Alexa Skill Hostname | The public HTTPS endpoint Alexa uses to reach this add-on; required for guided setup | N |
| API Username | The username to be provided to Music Assistant for communication to this API, defaults to (ma-local-alexa-api) | Y |
| API Password | The password to be provided to Music Assistant for communication to this API, if blank on start one will be generated | N |
| Alexa Skill Locale | The locale used by the skill setup flow, defaults to en-US | N |
| Skip Stream URL Validation | Skip the external stream reachability check when local network routing prevents it | N |
| Music Assistant Control API URL | optional local MA API address for mapped voice controls | N |
| Music Assistant API Token | access token for the MA control API | N |
| Enable Echo Show Display | opt into APL display; defaults to false | N |

### Alexa API

Create an Alexa skill whose HTTPS endpoint reaches this add-on's root route. Set `skill_hostname` to that public endpoint and use guided setup, or follow the manual skill setup below. The add-on listens internally on **5000**; changing the Supervisor host port mapping does not change its internal port.

### Streams and Nginx Proxy Manager

Alexa needs public HTTPS access to the skill endpoint and audio stream on both screenless and APL devices.
Nginx Proxy Manager can provide both. Forward external HTTPS port **443** to
NPM; keep add-on port **5000** and Music Assistant stream port **8097** internal.
Direct internet forwarding of those two application ports is unnecessary.

| Address | NPM upstream | Setup setting |
| --- | --- | --- |
| `https://alexa.example.com` | `http://<HA-LAN-IP>:5000` | `skill_hostname` |
| `https://streams.example.com` | `http://<MA-LAN-IP>:8097` | `ma_hostname` |

Set Music Assistant's Alexa provider **API URL** to `http://<HA-LAN-IP>:5000`
without `/ma`. Configure its Basic Auth fields with the add-on API credentials.
This LAN API address is separate from the public skill and stream addresses.
Use a publicly trusted TLS certificate on NPM. Alexa's public skill endpoint
must accept signed POST requests without an additional NPM login/access list.

For existing custom locations, `/ma-alexa-skill/` must
proxy to the add-on root with that prefix stripped. `/flow/`, `/pluginsource/`,
`/announcement/`, and `/imageproxy/` should proxy to the stream server while
preserving their paths. In 1.2.0, a `ma_hostname` path prefix is prepended exactly once
when rewriting an internal stream URL. Separate proxy hosts simplify setup.

If Music Assistant connects directly to the add-on LAN API URL above, no NPM locations are needed for `/alexa/` or `/ma/`. If it connects through a shared public hostname instead, set its Alexa provider **API URL** to that hostname's base URL (for example, `https://music.example.com`, without `/ma` or `/ma-alexa-skill`) and add these NPM custom locations:

| Location | Forward to | Path handling |
| --- | --- | --- |
| `/alexa/` | `http://<HA-LAN-IP>:5000` | Preserve `/alexa/`, including `/alexa/intents`. |
| `/ma/` | `http://<HA-LAN-IP>:5000` | Preserve `/ma/`, including `/ma/push-url`. |

Use the add-on's API username and password in Music Assistant's Basic Auth fields; avoid an additional NPM authentication layer on these API locations. These locations reach the add-on API, not the MA stream server on 8097 or the optional control API on 8095. A dedicated proxy host forwarding all paths to the add-on on 5000 already covers them and needs no custom API locations.

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

See [the update plan](docs/UPDATE_PLAN.md) for findings and validation evidence.

## Skill Setup

Candidate **1.3.0-beta.3** replaces interactive ASK CLI setup with a personal-skill deployment wizard. It requires one-time Login with Amazon security profile registration, then connects Amazon through Home Assistant ingress without a second app login, explicitly selects your existing skill, reviews settings, imports/builds the voice model and enables development testing. See the [personal skill deployment guide](docs/PERSONAL_SKILL_DEPLOYMENT.md) for options, the callback under the existing `/ma-alexa-skill/` route, ingress access and URL reachability checks and recovery. Stable **1.2.0** retains the previous setup flow; the candidate still needs live Amazon and Echo acceptance testing.

The manual steps below remain available when you prefer to manage the skill directly in the Alexa Developer Console.

### Steps

1. Login to the Amazon Alexa Developer Console `https://developer.amazon.com/alexa/console/ask`
2. Select `Create Skill`
3. Name & Locale,
    * Skill name: `Music Assistant`
    * Locale: Use the configured add-on `locale` value. The default is `en-US`.
4. Experience, Model, Hosting service
    * Experience: Music & Audio
    * Model: Custom
    * Hosting services: Provision your own
5. Templates:
    * Start from Scratch

#### Configuration of the Skill
1) Interaction Model > JSON Editor

Import the current interaction model for your configured locale from
`music-assistant-alexa-api/skill-api/app/models/<locale>.json` (for example
`en-GB.json`). This includes the latest playback and voice-control intents.
Do not reuse the earlier minimal PlayAudio-only model when updating a skill.

2) Assets > Endpoint
    * Type: HTTPS
    * Location: Default Region
        * URL: The public HTTPS skill endpoint configured through NPM, see Alexa API above.
        * Certificate Type: Your https certificate type

3) Interfaces

Enable Audio Player. Enable Alexa Presentation Language if you intend to opt into
APL rendering with `enable_apl: true`.

4) Build History > Build skill

Done 🙂, Your skill should now be live - enjoy.

### Migration release compatibility

Candidate 1.3.0-beta.3 keeps the legacy Supervisor schema with migration-only labels to preserve existing configuration during upgrade. Settings are imported once into `/data/app-settings.json`; all subsequent edits belong in ingress Setup. Later edits to the legacy fields are ignored. The obsolete AWS region option remains removed. Remove this temporary compatibility schema only in a later release once migration is verified.
