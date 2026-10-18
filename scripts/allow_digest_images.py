"""Extend the upstream add-on linter's image regex to accept OCI SHA256 pins."""

import json
import sys
from pathlib import Path

# The only file this script may touch is the linter's build schema inside the
# pinned frenck/action-addon-linter checkout (.addon-linter/src at the repo
# root, per .github/workflows/lint.yaml). The location is derived from the
# working directory and never taken from an argument, so no user input can
# reach the read/write sinks (S2083: argv-derived paths must not).
SCHEMA_DIR = Path(".addon-linter") / "src"
SCHEMA_NAME = "build.schema.json"


def extend_schema(schema):
    variants = schema["properties"]["build_from"]["anyOf"]
    references = list(variants[0]["properties"].values()) + [variants[1]]
    for reference in references:
        pattern = reference["pattern"]
        if not pattern.endswith("$"):
            raise ValueError("Unexpected upstream image-reference schema")
        reference["pattern"] = pattern[:-1] + r"(@sha256:[a-f0-9]{64})?$"
    return schema


def schema_path(cwd=None):
    """The pinned linter schema under *cwd*, or None when it is absent."""
    base = Path(cwd) if cwd is not None else Path.cwd()
    path = base / SCHEMA_DIR / SCHEMA_NAME
    if not path.is_file():
        return None
    return path.resolve()


def main():
    path = schema_path()
    if path is None:
        sys.exit(
            "refusing to patch: run from the repository root with the pinned "
            f"{SCHEMA_DIR / SCHEMA_NAME} checkout present"
        )
    schema = extend_schema(json.loads(path.read_text()))
    path.write_text(json.dumps(schema, indent=2) + "\n")


if __name__ == "__main__":
    main()
