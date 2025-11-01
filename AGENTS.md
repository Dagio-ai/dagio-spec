# Adding a New AI Assistant

This guide describes the minimal steps required to wire a new assistant into the internal `specify` CLI. Every change lives inside `src/specify_cli` and the bundled data directory.

## 1. Register the Assistant

Edit `src/specify_cli/__init__.py` and extend `AGENT_CONFIG`:

```python
AGENT_CONFIG = {
    "claude": { ... },
    # existing entries
    "new-agent-cli": {
        "name": "New Agent",
        "folder": ".newagent/",
        "install_url": "https://example.internal/new-agent",
        "requires_cli": True,
    },
}
```

Guidelines:

- Use the executable name (`shutil.which`) as the dictionary key.
- `folder` is the workspace-relative directory that will hold generated prompts (e.g. `.newagent/commands/`).
- Set `requires_cli` to `False` for IDE integrations that do not ship a CLI.

The CLI help text automatically reflects the keys in `AGENT_CONFIG`, but update the documentation table in the README if you want the assistant listed explicitly.

## 2. Provide Command Templates

Add prompts under `src/specify_cli/data/templates/commands/`. Each template is copied into the workspace during `specify init` and rendered per agent.

Typical naming convention:

```
src/specify_cli/data/templates/commands/specify.<flow>.md
```

Inside the template, make sure you reference the workspace paths:

- `.specify/templates/...` for shared templates
- `.specify/scripts/bash/...` or `.specify/scripts/powershell/...` for helper scripts
- `.specify/memory/constitution.md` for the constitution

Use the existing entries (for example `specify.plan.md` or `specify.architecture.create.md`) as references for argument placeholders and formatting.

## 3. Verify Workspace Output

From a fresh checkout run:

```bash
# optional: ensure the build still succeeds
python -m compileall src/specify_cli

# create a disposable workspace
python src/specify_cli/__init__.py init ./sandbox --ai new-agent-cli --ignore-agent-tools
```

Confirm that:

- The agent folder (`.newagent/`) is created with rendered prompts.
- `.specify/templates/` and `.specify/scripts/` contain the expected helpers referenced by your templates.
- `specs/architecture/architecture.json` is still generated and the architecture slash commands work with the new agent.

## 4. Document Any Nuances

If the assistant requires extra environment variables, authentication steps, or non-default tooling, capture that in the internal README and (if relevant) inside the prompt itself. Keep this file up to date whenever new assistants are added or retired.
