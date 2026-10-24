# Example: NGINX Home Assistant SSL proxy

A tested example of proxying the Music Assistant Alexa API add-on through the
[NGINX Home Assistant SSL proxy](https://github.com/home-assistant/addons/tree/master/nginx_proxy)
add-on. This is the plain-YAML alternative to Nginx Proxy Manager described in
the add-on README's routing table; the maintainer runs this configuration.

Two files:

| File                       | Install at                        | Purpose                                                                                                  |
| -------------------------- | --------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `nginx_proxy_default.conf` | `/share/nginx_proxy_default.conf` | Custom locations inside the main HTTPS server: skill endpoint, provider API and stream routes. Required. |
| `ma.conf.example`          | `/share/nginx_proxy/ma.conf`      | Optional separate subdomain for direct Music Assistant web/API access. Not needed for Alexa playback.    |

`docs/nginx-example.conf` in this repository is the equivalent configuration
for a standalone nginx install instead of the add-on.

## Setup

1. Install **NGINX Home Assistant SSL proxy** from the add-on store.

2. Obtain a certificate into `/ssl` (Let's Encrypt, DuckDNS or another
   method). It must cover the `domain` below; if you also use the optional
   `ma.conf`, it must cover that hostname too (for example a wildcard
   certificate), since the add-on's `certfile` only covers the main domain.

3. Add-on configuration:

   ```yaml
   domain: music.example.com
   certfile: fullchain.pem
   keyfile: privkey.pem
   hsts: "max-age=31536000; includeSubDomains"
   customize:
     active: true
     default: nginx_proxy_default*.conf
     servers: nginx_proxy/*.conf
   ```

4. Copy `nginx_proxy_default.conf` to `/share/nginx_proxy_default.conf`
   (File editor, Studio Code Server or Samba) and edit the two upstream
   addresses:
   - `<HA_LAN_IP>` — the Home Assistant host's LAN IP; the add-on publishes
     port `5000` there.
   - `<MA_LAN_IP>` — the Music Assistant host's LAN IP (stream port `8097`).

5. Optionally copy `ma.conf.example` to `/share/nginx_proxy/ma.conf` and set
   its hostname and upstream.

6. In `configuration.yaml`, trust the proxy:

   ```yaml
   http:
     use_x_forwarded_for: true
     trusted_proxies:
       - 172.30.33.0/24
   ```

   Restart Home Assistant. Without this the UI returns `400 Bad Request`.

   One reported setup (issue #40) additionally needed the loopback, LAN
   and Docker networks trusted before proxied requests — notably the
   streams URL endpoint — were accepted. Equivalent in the UI under
   **Settings → System → Network → HTTP server → Reverse proxy**:

   ```yaml
   http:
     use_x_forwarded_for: true
     trusted_proxies:
       - 127.0.0.1/32 # loopback
       - ::1/128 # IPv6 loopback
       - 192.168.0.0/16 # your LAN range
       - 172.0.0.0/8 # Docker networks (includes 172.30.33.0/24)
   ```

7. Start the add-on and check its log for configuration errors.

## Add-on and Music Assistant settings

- **Music Assistant Alexa API → Setup**: set _Music Assistant Hostname_ to
  the public audio origin (`music.example.com`). The skill endpoint correctly
  defaults to `https://music.example.com/ma-alexa-skill/`.
- **Music Assistant Alexa provider**: _API URL_ is either the LAN address
  `http://<HA_LAN_IP>:5000` (recommended; then the public `/alexa/` and
  `/ma/` locations are unused but harmless) or the public base URL
  `https://music.example.com` (then those locations are required, as
  configured). Use the add-on API credentials for Basic Auth either way,
  and do not add any proxy authentication in front of them.

## Verify

- `https://music.example.com/ma-alexa-skill/health` returns the add-on
  health JSON (the prefix is stripped, so this reaches `/health`).
- A `/flow/...` path returns a Music Assistant stream response.
- The skill endpoint answers Alexa's signed POSTs with no login page or
  access-list challenge.

## Notes

- The skill location strips the `/ma-alexa-skill/` prefix (trailing slash on
  `proxy_pass`); all other locations preserve the full path (no URI on
  `proxy_pass`).
- The stream locations rely on the add-on template's server-level
  `proxy_buffering off`, and raise read/send timeouts for long tracks. Alexa
  probes streams with `HEAD` before `GET`; nginx handles both.
- `/status` and `/setup` are served through Home Assistant ingress and need
  no public location. Do not forward the add-on's port `5000` or Music
  Assistant's ports `8095`/`8097` directly to the internet.
