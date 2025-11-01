# Spec Kit

Spec Kit helps internal teams practise Spec-Driven Development (SDD). The toolkit bundles the `specify` CLI, reusable templates, and AI workflows so every project starts with the same structure and governance.

---

## Table of Contents

- [Install](#install)
- [Quick Start](#quick-start)
- [Slash Commands](#slash-commands)
- [Architecture Model](#architecture-model)
- [Reference](#reference)
- [Support](#support)

---

## Install

Spec Kit is designed for internal distribution. Point `uv` at the repository you cloned:

```bash
# persistent install
uv tool install --from path/to/spec-kit specify-cli

# one-off invocation
uvx --from path/to/spec-kit specify init
```

The CLI requires Python 3.11+ and `uv`. Optional agent CLIs (Claude, Gemini, Codex, etc.) are detected automatically unless you pass `--ignore-agent-tools`.

---

## Quick Start

```bash
# seed the current workspace
specify init --ai claude

# target another directory
specify init ../workspace --ai gemini

# choose PowerShell scripts explicitly
specify init --ai copilot --script ps

# skip agent tool detection
specify init --ai q --ignore-agent-tools

# overwrite existing .specify/ assets
specify init --force --ai codex
```

`specify init` copies all bundled assets into the workspace:

- `.specify/` - templates, helper scripts, and the project constitution
- `specs/` - per-feature specs plus `specs/architecture` for the model-as-data workflow
- agent-specific folders (`.claude/`, `.cursor/`, etc.) populated with generated commands

After an init the typical flow is:

1. `/specify.constitution` - establish project principles
2. `/specify.specify` - capture the functional spec
3. `/specify.plan` - define the implementation plan
4. `/specify.tasks` - break work into actionable steps
5. `/specify.implement` - execute the plan

---

## Slash Commands

| Command | Description |
|---------|-------------|
| `/specify.constitution` | Create or update project principles (`.specify/memory/constitution.md`) |
| `/specify.specify` | Capture functional requirements and user stories |
| `/specify.plan` | Produce the technical implementation plan |
| `/specify.tasks` | Generate an actionable checklist from the plan |
| `/specify.implement` | Execute the checklist and deliver the feature |
| `/specify.clarify` | Resolve underspecified or ambiguous requirements |
| `/specify.analyze` | Cross-check consistency across spec, plan, and tasks |
| `/specify.checklist` | Build custom QA checklists for sign-off |
| `/specify.architecture.create` | Analyse the repository and create the full architecture model |
| `/specify.architecture.update` | Refresh architecture artefacts using the saved model |

---

## Architecture Model

The architecture workflow is centred on `specs/architecture/architecture.json`. `/specify.architecture.create` populates that file before writing any Markdown views. The JSON model records:

- `model_version` and `generated_at`
- every view (C1-C6 plus per-container/per-component documents) with `path`, `version`, `checksum`, and `last_updated`
- containers and components with their associated views
- the change log pointer (`specs/architecture/architecture_logs.md`)

The slash commands generate Markdown under `specs/architecture/` by copying from `.specify/templates/` and then materialising one folder per container/component, following the structure captured in `architecture_repository.md`.

Markdown files under `specs/architecture/` are projections of the JSON model. After structural changes, run `/specify.architecture.update` to:

1. bump model and view versions
2. regenerate only the affected Markdown files
3. rebuild the table of contents in `architecture_overview.md`
4. append a versioned entry to `architecture_logs.md`

Treat the JSON as the single source of truth - manual edits to Markdown should be reflected back into the model before sharing the workspace.

---

## Reference

### CLI Options (`specify init`)

| Argument / Option | Description |
|-------------------|-------------|
| `target` | Workspace directory to seed (defaults to `.`) |
| `--ai` | Assistant to tailor commands for (claude, gemini, copilot, cursor-agent, qwen, opencode, codex, windsurf, kilocode, auggie, roo, codebuddy, amp, q) |
| `--script` | Script flavour: `sh` or `ps` |
| `--ignore-agent-tools` | Skip CLI detection for assistant tooling |
| `--force` | Overwrite existing `.specify/` assets without prompting |
| `--debug` | Print additional diagnostics on failure |

### Repository Layout

- `src/specify_cli/` - CLI implementation and bundled assets
  - `data/templates/` - spec, plan, tasks, checklist, architecture templates
  - `data/scripts/` - bash / PowerShell helpers copied into `.specify/scripts/`
  - `data/memory/` - constitution and long-lived references
- `specs/` - feature specs, plans, tasks, and `architecture/` model outputs

---

## Support

- **Questions / Issues**: open a thread in the internal Spec Kit channel
- **Agent additions**: update `src/specify_cli/data/templates/commands/` and `src/specify_cli/__init__.py` (`AGENT_CONFIG`) with the new assistant metadata
- **Bug reports**: capture the failing command, stack traces with `--debug`, and attach the relevant files from `.specify/` or `specs/`
