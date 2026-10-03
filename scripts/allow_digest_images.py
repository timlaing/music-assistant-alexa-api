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
    path = Path(sys.argv[1])
    schema = extend_schema(json.loads(path.read_text()))
    path.write_text(json.dumps(schema, indent=2) + "\n")
