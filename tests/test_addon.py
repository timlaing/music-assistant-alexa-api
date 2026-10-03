from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "music-assistant-alexa-api"


def test_addon_option_contract():
    config = yaml.safe_load((ADDON / "config.yaml").read_text())
    labels = yaml.safe_load((ADDON / "translations/en.yaml").read_text())[
        "configuration"
    ]
    assert config["slug"] == "ma_alexa_api"
    assert config["arch"] == ["aarch64", "amd64"]
    assert config["schema"]["ma_api_token"] == "password?"
    assert config["options"]["enable_apl"] is False
    assert set(config["schema"]) <= set(labels)
    run = (ADDON / "rootfs/etc/services.d/music-assistant-alexa-api/run").read_text()
    assert "PORT=5000" in run and "bashio::addon.port" not in run
    assert "--workers 1 --worker-class gthread --threads 8" in run
    assert "/data/.ask" in run and "/data/device_players.json" in run
    assert 'log.info "Password' not in run


def test_runtime_is_pinned():
    build = yaml.safe_load((ADDON / "build.yaml").read_text())
    assert all("@sha256:" in image for image in build["build_from"].values())
    lines = (ADDON / "requirements.lock").read_text().splitlines()
    assert all("==" in line for line in lines if line and not line.startswith("#"))
    assert "gunicorn==26.2.0" in lines
