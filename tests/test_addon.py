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
    assert "aws_default_region" not in config["schema"]
    assert config["schema"]["api_password"] == "password?"
    assert config["schema"]["ma_api_token"] == "password?"
    assert "migration only" in labels["api_password"]["name"]
    assert set(config.get("schema", {})) <= set(labels)
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


def test_personal_deployment_option_and_logging_contract():
    config = yaml.safe_load((ADDON / "config.yaml").read_text())
    assert set(config["schema"]) == {
        "skill_certificate_type",
        "skill_hostname",
        "api_password",
        "ma_api_url",
        "api_username",
        "enable_apl",
        "ma_api_token",
        "ma_hostname",
        "lwa_client_id",
        "lwa_client_secret",
        "locale",
        "skip_url_validation",
    }
    assert config["ingress"] and config.get("ingress_port", 8099) == 8099
    assert config["ingress_entry"] == "status"
    # Supervisor appends the configured entry to an ingress URL ending in /.
    assert "/api/hassio_ingress/session/" + config["ingress_entry"] == (
        "/api/hassio_ingress/session/status"
    )
    assert "8099/tcp" not in config["ports"]
    assert "webui" not in config
    run = (ADDON / "rootfs/etc/services.d/music-assistant-alexa-api/run").read_text()
    assert "/data/app-settings.json" in run
    assert "bashio::config" not in run
    assert "AWS_DEFAULT_REGION" not in run
    assert "/data/skill-deployment.json" in run
    log_format = (ADDON / "gunicorn.conf.py").read_text()
    assert "%(U)s" in log_format and "%(r)s" not in log_format
    assert (ROOT / "docs/PERSONAL_SKILL_DEPLOYMENT.md").read_bytes() == (
        ADDON / "skill-api/docs/PERSONAL_SKILL_DEPLOYMENT.md"
    ).read_bytes()
