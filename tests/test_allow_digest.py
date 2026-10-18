"""Schema extension and path confinement for scripts/allow_digest_images.py.

The linter patch script takes no arguments: the schema location is derived
from the working directory only, so no user input can reach the read/write
sinks (S2083) and stray files are never touched.
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
                    {"type": "string", "pattern": r"^ghcr\.io/[a-z0-9_.-]+$"},
                ]
            }
        }
    }


def _make_checkout(base):
    schema_file = base / ".addon-linter" / "src" / "build.schema.json"
    schema_file.parent.mkdir(parents=True)
    schema_file.write_text(json.dumps(_upstream_like_schema()))
    return schema_file


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


def test_schema_path_finds_pinned_checkout(tmp_path):
    schema_file = _make_checkout(tmp_path)
    assert allow_digest_images.schema_path(cwd=tmp_path) == schema_file.resolve()


def test_schema_path_none_when_checkout_absent(tmp_path):
    assert allow_digest_images.schema_path(cwd=tmp_path) is None


def test_schema_path_ignores_stray_files(tmp_path):
    _make_checkout(tmp_path)
    stray = tmp_path / "build.schema.json"
    stray.write_text("{}")
    resolved = allow_digest_images.schema_path(cwd=tmp_path)
    assert resolved != stray.resolve()
    assert resolved.parts[-3:] == (".addon-linter", "src", "build.schema.json")


def test_main_patches_in_process(tmp_path, monkeypatch):
    schema_file = _make_checkout(tmp_path)
    monkeypatch.chdir(tmp_path)
    allow_digest_images.main()
    patched = json.loads(schema_file.read_text())
    assert patched["properties"]["build_from"]["anyOf"][1]["pattern"].endswith(
        "(@sha256:[a-f0-9]{64})?$"
    )


def test_main_refuses_without_checkout(tmp_path, monkeypatch):
    stray = tmp_path / "build.schema.json"
    stray.write_text("{}")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as excinfo:
        allow_digest_images.main()
    assert "refusing to patch" in str(excinfo.value)
    assert json.loads(stray.read_text()) == {}


def test_cli_patches_schema_in_place(tmp_path):
    schema_file = _make_checkout(tmp_path)
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
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


def test_cli_refuses_without_checkout(tmp_path):
    stray = tmp_path / "build.schema.json"
    stray.write_text("{}")
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        check=False,
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "refusing to patch" in result.stderr
    assert json.loads(stray.read_text()) == {}
