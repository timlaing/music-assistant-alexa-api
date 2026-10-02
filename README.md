# Music Assistant Alexa API add-on repository

This repository contains the Local Alexa API for Music Assistant

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

| Name | Description | Required |
| ---- | ----------- | -------- |
| Music Assistant Hostname | The external hostname, port and root URI to be used for Streams | Y |
| Alexa Skill Hostname | The public HTTPS endpoint Alexa uses to reach this add-on | N |
| API Username | The username to be provided to Music Assistant for communication to this API, defaults to (ma-local-alexa-api) | Y |
| API Password | The password to be provided to Music Assistant for communication to this API, if blank on start one will be generated | N |
| AWS Default Region | The default region used for communication to AWS, defaults us-east-1. Leave unset unless problems occur | N |
| Alexa Skill Locale | The locale used by the skill setup flow, defaults to en-US | N |
| Skip Stream URL Validation | Skip the external stream reachability check when local network routing prevents it | N |
| Music Assistant Control API URL | Optional local MA API address for mapped voice controls | N |
| Music Assistant API Token | Access token for the MA control API | N |
| Enable Echo Show Display | Opt into APL display; defaults to false | N |

### Alexa API

In order to allow Alexa to work with Music Assistant, an Alexa skill needs to be created and configured to commuicate with this API. Skill setup instructions are provided below.

When configuring the Skill you need to provide a https url for Alexa to communicate with to obtain the Stream information, including the Stream URL.

This URL needs to point at this add-ons port (5000 by default). If using NginX Proxy Manager add-on for Home Assistant, this can be configured as a custom location on your existing proxy host.

Assuming you are using the default values adding a custom location with these parameters will work. ** The `/` values are very important **

* Location: `/ma-alexa-skill/`
* Scheme: `http`
* Forward Hostname / IP: `homeassistant/`
* Forward Port: `5000`

The endpoint value to provide to the Alexa skill would then be: `https://<your-home-assistant-domain>/ma-alexa-skill/`

### Streams and Nginx Proxy Manager

Alexa needs public HTTPS access to the skill endpoint and the audio stream.
Nginx Proxy Manager can provide both. Forward external HTTPS port **443** to
NPM; keep add-on port **5000** and Music Assistant stream port **8097** internal.
Direct internet forwarding of those two application ports is unnecessary.

| Address | NPM upstream | Add-on option |
| --- | --- | --- |
| `https://alexa.example.com` | `http://<HA-LAN-IP>:5000` | `skill_hostname` |
| `https://streams.example.com` | `http://<MA-LAN-IP>:8097` | `ma_hostname` |

Set Music Assistant's Alexa provider **API URL** to `http://<HA-LAN-IP>:5000`
without `/ma`. Configure its Basic Auth fields with the add-on API credentials.
This LAN API address is separate from the public skill and stream addresses.
Use a publicly trusted TLS certificate on NPM. Alexa's public skill endpoint
must accept signed POST requests without an additional NPM login/access list.

Existing custom locations also work. For example, `/ma-alexa-skill/` should
proxy to the add-on root with that prefix stripped. `/flow/`, `/pluginsource/`,
`/announcement/`, and `/imageproxy/` should proxy to the stream server while
preserving their paths. A `ma_hostname` path prefix is prepended exactly once
when rewriting an internal stream URL. Separate proxy hosts simplify setup.

### Optional voice controls and Echo Show display

Set `ma_api_url` to the local Music Assistant server API address (normally
`http://<MA-LAN-IP>:8095`) and `ma_api_token` to a Music Assistant access token.
These are optional for basic playback, and distinct from the public stream URL.
Open `/devices`, trigger a skill request from each Echo, and pair its opaque
Alexa device ID with the actual Music Assistant **player_id**, not its display
name. Mappings and ASK credentials survive add-on upgrades under `/data`.

Next, previous and start-over are routed to the mapped MA player. Pause, stop
and resume retain upstream's suppression of commands echoed back by MA.
Set `enable_apl: true` to opt into Echo Show artwork and controls; it defaults
to false. `skip_url_validation` remains false unless local routing prevents
this container from checking a stream which the Echo can reach publicly.

See [the update plan](docs/UPDATE_PLAN.md) for findings and validation evidence.

## Skill Setup

The add-on includes a guided skill setup flow. Configure `Alexa Skill Hostname`, start the add-on, open its Web UI, and select **Setup**. The setup page guides you through Alexa ASK authorization and creates or updates the skill for the configured locale. ASK credentials are persisted in the add-on data directory.

The manual steps below remain available when you prefer to manage the skill directly in the Alexa Developer Console.

### Steps

1. Login to the Amazon Alexa Developer Console `https://developer.amazon.com/alexa/console/ask`
2. Select `Create Skill`
3. Name & Locale,
    * Skill name: `Music Assistant`
    * Locale: Use the configured add-on `locale` value. The default is `en-US`.
4. Exoerience, Model, Hosting service
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
        * URL: Public URL for access to port 5000 or configured port number on this add-on, see Alexa API above.
        * Certificate Type: Your https certificate type

3) Build History > Build skill

Done 🙂, Your skill should now be live - enjoy.
