"""Extend the upstream add-on linter's image regex to accept OCI SHA256 pins."""

import json
import sys
from pathlib import Path


def extend_schema(schema):
    variants = schema["properties"]["build_from"]["anyOf"]
    references = list(variants[0]["properties"].values()) + [variants[1]]
    for reference in references:
        pattern = reference["pattern"]
        if not pattern.endswith("$"):
            raise ValueError("Unexpected upstream image-reference schema")
        reference["pattern"] = pattern[:-1] + r"(@sha256:[a-f0-9]{64})?$"
    return schema


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} <path-to-build.schema.json>")
    # The only file this script may touch is the linter's build schema; refuse
    # anything else so a stray argument can never redirect the write.
    path = Path(sys.argv[1]).resolve()
    if path.name != "build.schema.json" or not path.is_file():
        sys.exit(f"refusing to patch unexpected file: {path}")
    schema = extend_schema(json.loads(path.read_text()))
    path.write_text(json.dumps(schema, indent=2) + "\n")
