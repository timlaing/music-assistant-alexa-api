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
