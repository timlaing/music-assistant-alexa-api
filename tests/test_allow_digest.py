"""Path confinement and schema extension for scripts/allow_digest_images.py.

The linter patch script accepts a CLI path argument; S2083 requires that the
argument can never redirect the read/write outside the pinned checkout.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "allow_digest_images.py"

_spec = importlib.util.spec_from_file_location("allow_digest_images", SCRIPT)
allow_digest_images = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(allow_digest_images)


def _upstream_like_schema():
    ref = {"type": "string", "pattern": "^aarch64[a-z0-9_.-]*$"}
    return {
        "properties": {
            "build_from": {
                "anyOf": [
                    {"properties": {"aarch64": ref, "amd64": dict(ref)}},
                    {"type": "string", "pattern": "^ghcr\\.io/[a-z0-9_.-]+$"},
                ]
            }
        }
    }


def test_extend_schema_accepts_digest_suffix():
    schema = allow_digest_images.extend_schema(_upstream_like_schema())
    variants = schema["properties"]["build_from"]["anyOf"]
    for reference in list(variants[0]["properties"].values()) + [variants[1]]:
        assert reference["pattern"].endswith("(@sha256:[a-f0-9]{64})?$")


def test_extend_schema_rejects_unexpected_pattern():
    schema = _upstream_like_schema()
    schema["properties"]["build_from"]["anyOf"][1]["pattern"] = "^no-anchor"
    with pytest.raises(ValueError):
        allow_digest_images.extend_schema(schema)


def test_resolve_schema_path_accepts_pinned_checkout(tmp_path):
    schema_file = tmp_path / ".addon-linter" / "src" / "build.schema.json"
    schema_file.parent.mkdir(parents=True)
    schema_file.write_text("{}")
    resolved = allow_digest_images.resolve_schema_path(
        ".addon-linter/src/build.schema.json", cwd=tmp_path
    )
    assert resolved == schema_file.resolve()


def test_resolve_schema_path_rejects_traversal_and_elsewhere(tmp_path):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / "build.schema.json").write_text("{}")
    for arg, cwd in (
        ("../elsewhere/build.schema.json", tmp_path),
        (str(elsewhere / "build.schema.json"), tmp_path),
        ("elsewhere/build.schema.json", tmp_path),
        ("/etc/build.schema.json", tmp_path),
        (".addon-linter/src/build.schema.yml", tmp_path),
        ("-rf/build.schema.json", tmp_path),
    ):
        with pytest.raises(SystemExit):
            allow_digest_images.resolve_schema_path(arg, cwd=cwd)


def test_resolve_schema_path_requires_existing_file(tmp_path):
    (tmp_path / ".addon-linter" / "src").mkdir(parents=True)
    with pytest.raises(SystemExit):
        allow_digest_images.resolve_schema_path(
            ".addon-linter/src/build.schema.json", cwd=tmp_path
        )


def test_cli_patches_schema_in_place(tmp_path):
    schema_file = tmp_path / ".addon-linter" / "src" / "build.schema.json"
    schema_file.parent.mkdir(parents=True)
    schema_file.write_text(json.dumps(_upstream_like_schema()))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), ".addon-linter/src/build.schema.json"],
        check=False,
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    patched = json.loads(schema_file.read_text())
    assert patched["properties"]["build_from"]["anyOf"][1]["pattern"].endswith(
        "(@sha256:[a-f0-9]{64})?$"
    )


def test_cli_refuses_unexpected_path(tmp_path):
    evil = tmp_path / "build.schema.json"
    evil.write_text("{}")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "build.schema.json"],
        check=False,
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "refusing to patch" in result.stderr
    assert json.loads(evil.read_text()) == {}


def test_main_patches_in_process(tmp_path, monkeypatch):
    schema_file = tmp_path / ".addon-linter" / "src" / "build.schema.json"
    schema_file.parent.mkdir(parents=True)
    schema_file.write_text(json.dumps(_upstream_like_schema()))
    monkeypatch.chdir(tmp_path)
    allow_digest_images.main(
        ["allow_digest_images.py", ".addon-linter/src/build.schema.json"]
    )
    patched = json.loads(schema_file.read_text())
    assert patched["properties"]["build_from"]["anyOf"][1]["pattern"].endswith(
        "(@sha256:[a-f0-9]{64})?$"
    )


def test_main_usage_error():
    with pytest.raises(SystemExit) as excinfo:
        allow_digest_images.main(["allow_digest_images.py"])
    assert "usage:" in str(excinfo.value)
