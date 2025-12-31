# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
# See the documentation for more information
ARG BUILD_FROM
FROM $BUILD_FROM

# Execute during the build of the image
ARG TEMPIO_VERSION BUILD_ARCH
RUN \
    curl -sSLf -o /usr/bin/tempio \
    "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}"

# Copy root filesystem
COPY rootfs /
COPY skill-api/app/lambda/py/src /app/src


RUN apk add --update --no-cache \
    python3\
    py3-pip \
    py3-virtualenv

WORKDIR /app
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip gunicorn && \
    pip install -r src/requirements.txt

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD [ "curl", "-f", "http://localhost:5000/status" ]