# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM

FROM ghcr.io/alams154/music-assistant-skill:dev AS base_image

FROM $BUILD_FROM

# Execute during the build of the image
ARG TEMPIO_VERSION BUILD_ARCH
RUN \
    curl -sSLf -o /usr/bin/tempio \
    "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}"

# Copy root filesystem
COPY rootfs /
COPY --from=base_image /app/src /app/src
COPY --from=base_image /app/requirements.txt /app


RUN apk add --update --no-cache \
    python3\
    py3-pip \
    py3-virtualenv

WORKDIR /app
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip gunicorn && \
    pip install -r requirements.txt

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD [ "curl", "-f", "http://localhost:5000/status" ]