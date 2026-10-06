# Repository automation

This follows the maintained `timlaing/ha_tuya_ble` policy, adapted for Alexa.

- Issues receive `needs-triage` when opened or reopened, including API-created issues. Issue forms also set `bug`, `enhancement`, `documentation` or `question`. Remove `needs-triage` after reviewing an issue.
- PR labels follow changed documentation/CI files, conventional title prefixes and feature/fix/Dependabot branch names. Labels are hints; maintainers should correct them when the scope differs. Metadata labeling uses `pull_request_target` without checking out or running PR code, so it can label fork PRs.
- Issues become stale after 60 inactive days and close 14 days later as `not planned`. Activity clears the stale label. `pinned`, `security` and `roadmap` are exempt. PRs are never marked stale or closed by this workflow.
- Release Drafter updates an unpublished draft on pushes to `main` and manual runs. Features suggest a minor version; `major` suggests a major version; other changes default to patch. `skip-changelog` excludes a PR. Suggested versions must be reconciled across the add-on and skill before publishing.
- Drafting does not bump application versions, sign tags, publish releases or build images. Follow the existing coordinated release process for those steps.

The label definitions are tracked in `.github/labels.json`. To reapply them without deleting other labels:

```sh
python3 - <<'PYLABELS'
import json
import subprocess
for label in json.load(open('.github/labels.json')):
    subprocess.run(['gh', 'label', 'create', label['name'], '--color', label['color'],
                    '--description', label['description'], '--force'], check=True)
PYLABELS
```
