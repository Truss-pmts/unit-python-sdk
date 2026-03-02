---
name: truss-unit-sdk-local-install
description: Install the local unit-python-sdk fork into the API virtualenv in editable mode so SDK changes are immediately reflected. Use when modifying unit-python-sdk, adding new SDK types, or after any edit to unit-python-sdk/unit/models/ that needs to be picked up by the API.
---

# Truss Unit SDK Local Install

After modifying anything in `unit-python-sdk/`, run this to make the API venv pick up the changes:

```bash
/Users/averykushner/cursor-projects/truss-fullstack/api/.venv/bin/pip install -e /Users/averykushner/cursor-projects/truss-fullstack/unit-python-sdk
```

The `-e` flag installs in editable mode — the venv symlinks to the local source, so subsequent edits to the SDK are reflected immediately without reinstalling. Only run this command again if the venv is recreated or the SDK package metadata changes (e.g. `pyproject.toml`).
