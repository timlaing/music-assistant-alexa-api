# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
# See the documentation for more information
# This requires the submodule skill-api to be present

ARG BUILD_FROM
FROM $BUILD_FROM

# Execute during the build of the image
ARG TEMPIO_VERSION BUILD_ARCH
RUN \
    curl -sSLf -o /usr/bin/tempio \
    "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}"

# Install runtime and build dependencies. The ASK CLI powers the upstream
# browser-based skill setup flow.
RUN apk add --no-cache \
        nodejs \
        npm \
        python3 \
        py3-pip \
        py3-virtualenv && \
    apk add --no-cache --virtual .build-dependencies \
        build-base \
        cargo \
        libffi-dev \
        openssl-dev \
        python3-dev

WORKDIR /app

# Install dependencies before copying the application so source-only changes
# can reuse the dependency layer.
COPY skill-api/app/requirements.txt /app/requirements.txt
COPY scripts/patch_python_dependencies.py /tmp/patch_python_dependencies.py
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir gunicorn==26.0.0 -r requirements.txt && \
    python /tmp/patch_python_dependencies.py && \
    npm install --global ask-cli@2.30.7 && \
    npm cache clean --force && \
    apk del .build-dependencies && \
    rm /tmp/patch_python_dependencies.py

# Copy the complete refactored upstream application. Its setup tooling expects
# the repository app directory at /app/app, so use a symlink rather than a
# second copy of the Python modules.
COPY skill-api/app /app/src
COPY skill-api/assets /app/assets
COPY skill-api/scripts /app/scripts
RUN ln -s /app/src /app/app && \
    chmod +x /app/scripts/*.sh

# Copy the Home Assistant service definition last.
COPY rootfs /

ENV AWS_DEFAULT_REGION="us-east-1" \
    LOCALE="en-US" \
    MA_HOSTNAME="" \
    PORT="5000" \
    QUIET_HTTP="1" \
    SKILL_HOSTNAME="" \
    SKIP_URL_VALIDATION="false"

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl --silent --output /dev/null --write-out "%{http_code}" \
        "http://localhost:${PORT}/status" | grep -Eq "^(200|401)$"
