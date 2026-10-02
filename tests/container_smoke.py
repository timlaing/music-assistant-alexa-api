"""Probe real Gunicorn HTTP handling and shutdown inside a built image."""

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASELINE = "--baseline" in __import__("sys").argv
os.environ.update(
    APP_USERNAME="test-user",
    APP_PASSWORD="test-password",
    PORT="5000",
    AWS_EC2_METADATA_DISABLED="true",
    SKIP_URL_VALIDATION="true",
    MA_HOSTNAME="https://streams.example.com/music",
    ASK_CREDENTIALS_DIR="/tmp/ask-data/.ask",
    DEVICE_MAPPING_PATH="/tmp/device_players.json",
)
AUTH = "Basic dGVzdC11c2VyOnRlc3QtcGFzc3dvcmQ="


def request(path, payload=None, auth=True, extra_headers=None):
    headers = {"Authorization": AUTH} if auth else {}
    headers.update(extra_headers or {})
    # NPM-style forwarded values must not make internal status checks call the internet.
    headers.update(
        {"X-Forwarded-Proto": "https", "X-Forwarded-Host": "alexa.example.com"}
    )
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        "http://127.0.0.1:5000" + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


command = [
    "/app/venv/bin/gunicorn",
    "--workers",
    "1",
    "--bind",
    "127.0.0.1:5000",
    "--chdir",
    "/app/src",
    "--error-logfile",
    "-",
    "--capture-output",
    "app:app",
]
if not BASELINE:
    command[1:1] = ["--config", "/app/gunicorn.conf.py"]
    command[1:1] = ["--worker-class", "gthread", "--threads", "8"]
proc = subprocess.Popen(command)
try:
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise AssertionError(f"Gunicorn exited during startup: {proc.returncode}")
        try:
            if request("/status", auth=False)[0] == 401:
                break
        except (OSError, TimeoutError):
            pass
        time.sleep(0.1)
    else:
        raise AssertionError("Gunicorn did not become ready")
    for _ in range(10):
        assert request("/", auth=False)[0] in (401, 405)
        assert request("/status")[0] == 200
    if BASELINE:
        print(
            "BASELINE: ordinary HTTP requests did not reproduce issue #23", flush=True
        )
    else:
        assert request("/health", auth=False) == (200, '{"status":"ok"}\n')
        assert request("/alexa/intents")[0] == 200
        assert request("/ma/latest-url")[0] == 404
        status, body = request(
            "/ma/push-url",
            {"streamUrl": "http://ma.local:8097/flow/song.mp3", "title": "Smoke test"},
        )
        assert status == 200, body
        status, body = request("/ma/latest-url")
        assert (
            status == 200
            and json.loads(body)["streamUrl"]
            == "https://streams.example.com/music/flow/song.mp3"
        )
        envelope = {
            "version": "1.0",
            "context": {
                "System": {
                    "application": {"applicationId": "test-skill"},
                    "user": {"userId": "test-user"},
                    "device": {
                        "deviceId": "echo-1",
                        "supportedInterfaces": {"AudioPlayer": {}},
                    },
                }
            },
            "request": {
                "type": "LaunchRequest",
                "requestId": "smoke-request",
                "locale": "en-US",
            },
        }
        assert (
            request(
                "/", envelope, auth=False, extra_headers={"X-Simulator-Bypass": "true"}
            )[0]
            == 403
        )
        status, body = request(
            "/", envelope, extra_headers={"X-Simulator-Bypass": "true"}
        )
        assert status == 200, body
        assert (
            json.loads(body)["response"]["directives"][0]["audioItem"]["stream"]["url"]
            == "https://streams.example.com/music/flow/song.mp3"
        )
        with ThreadPoolExecutor(8) as pool:
            paths = ["/health", "/status/ma", "/status/alexa", "/ma/latest-url"] * 10
            assert all(status == 200 for status, _ in pool.map(request, paths))
        assert (
            request(
                "/",
                {"version": "1.0", "request": {"type": "LaunchRequest"}},
                auth=False,
            )[0]
            != 200
        )
        assert proc.poll() is None
        print(
            "UPDATED: HTTP, forwarded proxy requests, concurrent status and signature rejection passed",
            flush=True,
        )
finally:
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        raise AssertionError("Gunicorn did not shut down within 10 seconds")
    assert proc.returncode == 0, proc.returncode
    print("Gunicorn shutdown passed", flush=True)
