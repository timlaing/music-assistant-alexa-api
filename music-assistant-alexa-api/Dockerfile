# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
# The application layer ships prebuilt: the skill image contains the Python
# 3.12 environment (with the verifier/certvalidator patches applied), ASK CLI,
# the skill code and the assets. This layer adds the add-on runtime glue.
# The tag+digest here and in build.yaml must stay identical — see AGENTS.md.
ARG BUILD_FROM=ghcr.io/timlaing/music-assistant-skill:v1.5.0-beta.2@sha256:3622f5212b7e99ba623ff9a2c5abf012ed95600b1eb920f8a50e0114a293ecb6
FROM $BUILD_FROM

# Serve with gunicorn instead of the skill image's Flask dev server, using the
# Home Assistant ingress log format from gunicorn.conf.py.
RUN /app/venv/bin/pip install --no-cache-dir gunicorn==26.2.0

# Add-on service definition. The skill image is Ubuntu-based and has no Home
# Assistant base s6-overlay/bashio, so the service is a plain entrypoint
# replacing the image CMD.
COPY gunicorn.conf.py /app/gunicorn.conf.py
COPY rootfs /

ENV LOCALE="en-US" \
    MA_HOSTNAME="" \
    PORT="5000" \
    QUIET_HTTP="1" \
    SKILL_HOSTNAME="" \
    SKIP_URL_VALIDATION="false" \
    ENABLE_APL="false" \
    PYTHONFAULTHANDLER="1"

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail --silent --output /dev/null "http://localhost:5000/health"
