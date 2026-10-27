# Example: Cloudflare Tunnel

Putting a [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
in front of the skill and stream host. This guidance is compiled from the two
Cloudflare reports in [#40](https://github.com/timlaing/music-assistant-alexa-api/issues/40):

- one setup runs **Cloudflare Tunnel → Nginx Proxy Manager → add-on + Music Assistant**
  with the **wildcard / sub-domain** certificate option and plays end to end
  (2026-10-24);
- another fixed playback only by **dropping Cloudflare Tunnels entirely** for
  DuckDNS (2026-10-22).

The maintainer does not run this topology. The routing below reuses the tested
location table from the [main README](../../README.md#streams-and-nginx-proxy-manager);
what is tunnel-specific is called out here.

## Why use a tunnel

- **No port forwarding.** `cloudflared` dials out to Cloudflare; nothing needs
  to be reachable from the internet except the tunnel itself.
- **It fixes broken hairpin/NAT-loopback.** Alexa's POSTs and the Echo's audio
  fetch reach the Cloudflare edge, and the tunnel carries them in — so a router
  that cannot loop LAN→WAN→LAN traffic back (the split-horizon DNS failure in
  the troubleshooting sequence) works over a tunnel where direct port forwarding
  does not.
- **A stable origin address** for Cloudflare, independent of a changing home IP.

## Topology

One public hostname serves both the skill and the audio, exactly like the shared-hostname
NPM layout in the main README:

```text
Alexa skill / Echo
        │
        ▼
Cloudflare edge  ──►  cloudflared  ──►  Nginx Proxy Manager  ──┬──► add-on       :5000
  (TLS, WAF, cache)      (outbound)        (path routing)      └──► Music Assistant :8097
```

`docs/nginx-ha-ssl-proxy` works the same way in place of NPM: the tunnel points
at the NGINX Home Assistant SSL proxy and the locations from that example do the
routing.

**Why the proxy stays in the middle:** `cloudflared` ingress rules match a path
but never rewrite it, and the add-on serves its routes at the root — so a tunnel
pointed straight at the add-on would deliver `/ma-alexa-skill/…` to a route that
does not exist (the #40 report that could only use a bare `https://host:5000`
skill endpoint was hitting exactly this). The proxy strips the prefix, which the
location table above already does.

> **Direct-to-origin alternative.** If you skip the proxy, avoid path rewriting
> altogether: one hostname for the skill pointing at the add-on (all paths) and
> one for audio pointing at Music Assistant (all paths), then set the **Public
> skill endpoint** in Setup to the skill host's base URL without the
> `/ma-alexa-skill/` prefix. Copy the callback URL Setup generates — it derives
> from that endpoint.

## Setup

1. Create a tunnel and install `cloudflared` (as an add-on or container) where it
   can reach NPM's LAN address. Inside a container, `localhost` is not the host —
   use the Home Assistant host's LAN IP.

2. Route the public hostname to the proxy. Equivalent `config.yml` ingress:

   ```yaml
   tunnel: <TUNNEL_ID>
   credentials-file: /etc/cloudflared/<TUNNEL_ID>.json
   ingress:
     - hostname: streams.example.com
       service: https://<NPM_LAN_IP>
       originRequest:
         # Only needed when NPM's certificate is not publicly trusted;
         # a Let's Encrypt certificate for the hostname verifies without it.
         noTLSVerify: true
     - service: http_status:404
   ```

   `cloudflared` preserves the incoming `Host` header, so NPM needs the proxy
   host for `streams.example.com` with the custom locations from the main
   README (skill prefix stripped to `:5000`, stream paths preserved to `:8097`).
   The dashboard's **Public hostname** route creates the same mapping without a
   config file.

3. **The DNS record must stay proxied (orange cloud).** Tunnel routing requires
   it — unlike a direct setup, you **cannot grey-cloud a tunneled hostname** to
   bypass the edge. The bypass becomes the cache/WAF exclusions below.

4. In the add-on's **Skill setup**, select **Trusted sub-domain** for the
   certificate type: Cloudflare's edge certificate is a wildcard for the zone,
   and the plain trusted-CA option left the simulator unable to reach the skill
   in #40. Re-deploy with **Review settings → Deploy approved settings** after
   changing it.

5. In the Login with Amazon profile, the **Allowed Return URL** is the callback
   URL Setup shows you (derived from the public skill endpoint you saved), for
   example `https://streams.example.com/ma-alexa-skill/setup/oauth/callback`.

## Cloudflare dashboard checklist

Applied per public hostname:

| Setting                                       | Value                                                                             | Why                                                                                                                                              |
| --------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Cache Rules                                   | **Bypass cache** for `/flow/*`, `/pluginsource/*`, `/source/*`, `/announcement/*` | `.mp3` is in Cloudflare's default cacheable extension list; the edge must never cache a live one-shot stream (`cf-cache-status: HIT` breaks it). |
| Bot Fight Mode, security level, WAF rules     | Off for these hostnames, or a **skip rule**                                       | Amazon's server-side POSTs and the Echo's GETs get an HTML/JS challenge (403/503) instead of audio; the Echo cannot execute it.                  |
| TLS → Minimum TLS version                     | 1.2                                                                               | Echo devices negotiate TLS 1.2; a 1.3-only floor can strand them.                                                                                |
| Rocket Loader, Email Obfuscation, Auto-minify | Off for these hostnames                                                           | Response rewriting has no place on a streaming/API origin.                                                                                       |
| Origin response                               | First byte well within 100 s                                                      | Cloudflare answers 524 past its origin wait; Music Assistant should stream immediately.                                                          |
| Alexa certificate type (**Skill setup**)      | **Trusted sub-domain**                                                            | Matches the edge wildcard certificate (Setup step 4 above).                                                                                      |

## Verify

```bash
# Skill endpoint: add-on health JSON, HTTP 200
curl -s -o /dev/null -w '%{http_code}\n' https://streams.example.com/ma-alexa-skill/health

# A flow URL must stream real bytes (200 with size_download climbing in 10 s)
curl -s -m 10 -o /dev/null -w '%{http_code} %{size_download}\n' '<flow-url>'

# The edge must not have cached it: cf-cache-status DYNAMIC/MISS, never HIT
curl -s -m 10 -D - -o /dev/null '<flow-url>' | grep -iE '^(HTTP|cf-cache-status)'
```

Then fail a playback on purpose and read all three logs together — they locate
the break in one pass:

1. **`cloudflared` access log** — did the edge deliver the request, and what
   did the origin answer?
2. **NPM/nginx access log** — did the proxy receive it and forward it?
3. **Add-on log** — did the Echo's `GET /flow/…` arrive at all? No line means
   the request never reached your network (see _Isolate the broken hop_ in the
   troubleshooting guide).

## If playback still fails

- **You cannot grey-cloud a tunneled hostname.** Add the cache/WAF exclusions
  from the checklist instead — `cf-cache-status` on a flow URL is the litmus
  test.
- **Or move only the audio off the tunnel:** a second, DNS-only hostname with a
  port forward bypasses the edge, but it reintroduces the hairpin/NAT-loopback
  requirement from the split-horizon DNS warning.
- **Or drop the tunnel entirely** — that is what restored playback on one #40
  setup, while the other kept the tunnel and fixed the certificate option
  instead.
