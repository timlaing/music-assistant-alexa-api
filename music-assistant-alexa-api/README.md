# Home Assistant Add-on: Music Assistant Alexa API add-on

Turn your Alexa Echo devices into Music Assistant players.

This add-on packages the [Music Assistant Alexa skill service](https://github.com/timlaing/music-assistant-alexa-skill) for Home Assistant Supervisor. It runs the API that Music Assistant's Alexa provider talks to, and its Setup page guides you through registering a personal Alexa skill in your own Amazon developer account — no manual Alexa Developer Console work is needed.

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

## Installation

1. Add `https://github.com/timlaing/music-assistant-alexa-api` as a custom repository: **Settings → Add-ons → Add-on Store → ⋮ → Repositories**.
2. Install **Music Assistant Alexa API add-on** (available for **aarch64** and **amd64**).
3. Start the add-on and open **Web UI → Setup** through Home Assistant ingress — no separate app login.

## Getting started

1. In **Setup**, save the public audio URL and the API credentials Music Assistant will use, then **Connect to Amazon** with a Login with Amazon (LWA) security profile.
2. Select your existing personal skill or create a new one, review the settings and **Deploy approved settings**.
3. In Music Assistant's Alexa provider, set **API URL** to the add-on LAN base URL (for example `http://<HA-LAN-IP>:5000`, without `/ma`) and use the add-on API username and password for Basic Auth.

Alexa needs public HTTPS endpoints for both the skill and the audio streams; the [Streams and Nginx Proxy Manager](https://github.com/timlaing/music-assistant-alexa-api#streams-and-nginx-proxy-manager) section of the repository guide shows a working proxy layout. Full option reference is in the add-on's **Documentation** tab ([DOCS.md](DOCS.md)).

## Support

- Issues and requests: [timlaing/music-assistant-alexa-api](https://github.com/timlaing/music-assistant-alexa-api/issues)
- Release history: [Releases](https://github.com/timlaing/music-assistant-alexa-api/releases)

Many thanks to [@alams154](https://github.com/alams154) for the original API that this add-on packages.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
