"""Extend the upstream add-on linter's image regex to accept OCI SHA256 pins."""

import json
import sys
from pathlib import Path

# The only file this script may touch is the linter's build schema inside the
# pinned frenck/action-addon-linter checkout (.addon-linter/src at the repo
# root, per .github/workflows/lint.yaml). Restrict both the filename and the
# containing directory so a stray argument can never redirect the read/write
# (S2083: argv-derived paths must not reach file sinks unvalidated).
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


def resolve_schema_path(arg, cwd=None):
    """Resolve *arg* to the linter schema, refusing anything else.

    Both the basename and the containing directory must match the pinned
    checkout layout; resolves symlinks and relative segments before checking.
    """
    base = Path(cwd) if cwd is not None else Path.cwd()
    schema_dir = (base / SCHEMA_DIR).resolve()
    candidate = (base / arg).resolve()
    if candidate.name != SCHEMA_NAME or candidate.parent != schema_dir:
        sys.exit(f"refusing to patch unexpected file: {candidate}")
    if not candidate.is_file():
        sys.exit(f"refusing to patch unexpected file: {candidate}")
    return candidate


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} <path-to-build.schema.json>")
    path = resolve_schema_path(sys.argv[1])
    schema = extend_schema(json.loads(path.read_text()))
    path.write_text(json.dumps(schema, indent=2) + "\n")
