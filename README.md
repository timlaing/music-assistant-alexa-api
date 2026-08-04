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

### Streams

As discussed above, Alexa needs a public URL that it can recived a Stream, with is returned by a call to the API provided by this add-on.

Assuming Music Assistant is configured to use an IP address for the Stream provider setting. (Settings > System > Streams > Advanced settings > Published IP address)

This add-on will replace the IP address and Port number with the value provided in the `Music Assistant Hostname` setting.

By default Music Assistant will publish the stream on port 8097, with needs to be publicily accessible over https. If you are using NginX Proxy Manager add-on for Home Assistant, this can be also be configured as a custom location(s).

Assuming you are using the default values adding a custom locations with these parameters will work.

Flow stream location
* Location: `/flow/`
* Scheme: `http`
* Forward Hostname / IP: `homeassistant`
* Forward Port: `8097`

Plugin source location
* Location: `/pluginsource/`
* Scheme: `http`
* Forward Hostname / IP: `homeassistant`
* Forward Port: `8097`

The value for `Music Assistant Hostname` would be `https://<your-home-assistant-domain>`.

This would make your public URL used by Alexa for the Music Assistant streams to be:
* `https://<your-home-assistant-domain>/flow/...`
* `https://<your-home-assistant-domain>/pluginsource/...`

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

Enter the following JSON

```json
{
    "interactionModel": {
        "languageModel": {
            "invocationName": "music assistant",
            "intents": [
                {
                    "name": "PlayAudio",
                    "slots": [],
                    "samples": [
                        "play",
                        "start",
                        "play music assistant",
                        "play music assistant please",
                        "start music assistant",
                        "start music assistant please",
                        "start the audio",
                        "start the audio please",
                        "play the audio",
                        "play the audio please",
                        "start the music",
                        "start the music please",
                        "play the music",
                        "play the music please"
                    ]
                },
                {
                    "name": "AMAZON.PauseIntent",
                    "samples": []
                },
                {
                    "name": "AMAZON.ResumeIntent",
                    "samples": []
                },
                {
                    "name": "AMAZON.HelpIntent",
                    "samples": [
                        "help me please",
                        "help please",
                        "what should i do",
                        "what's next",
                        "how can I listen to music assistant",
                        "tell me how to play",
                        "tell me how to stop",
                        "tell me how to resume",
                        "how to stop"
                    ]
                },
                {
                    "name": "AMAZON.StopIntent",
                    "samples": []
                },
                {
                    "name": "AMAZON.CancelIntent",
                    "samples": []
                },
                {
                    "name": "AMAZON.StartOverIntent",
                    "samples": []
                },
                {
                    "name": "AMAZON.FallbackIntent",
                    "samples": []
                },
                {
                    "name": "AMAZON.NavigateHomeIntent",
                    "samples": []
                }
            ],
            "types": []
        }
    }
}
```

2) Assets > Endpoint
    * Type: HTTPS
    * Location: Default Region
        * URL: Public URL for access to port 5000 or configured port number on this add-on, see Alexa API above.
        * Certificate Type: Your https certificate type

3) Build History > Build skill

Done 🙂, Your skill should now be live - enjoy.
