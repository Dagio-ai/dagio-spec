---
description: Use the AI assistant to analyse the repository and create the full C1-C6 architecture views.
scripts:
  sh: scripts/bash/architecture-info.sh
  ps: scripts/powershell/architecture-info.ps1
---

## User Input

```text
$ARGUMENTS
```

If the user provided extra context, incorporate it into the analysis.

## Required Flow

1. **Gather context**
   - Run `{SCRIPT}` from the repo root to obtain a JSON summary (`architecture_dir`, `expected_views`, etc.).
   - If `architecture.json` already exists, load it to understand the previous `model_version`, individual view versions, and container/component inventory.
   - Review `specs/architecture/architecture_overview.md` and `specs/architecture/architecture_logs.md` to capture prior highlights, risks, and follow-up items.
   - Use `.specify/templates/architecture-template.json` and `.specify/templates/c*-*-template.md` files as schema and style references (do not copy them verbatim).

2. **Comprehensive code analysis**
   - Inventory languages, frameworks, build tools, and key packages (backend, frontend, infrastructure-as-code).
   - Identify deployable units, services, data stores, messaging layers, and external integrations.
   - Note cross-cutting concerns: auth, observability, performance, compliance, reliability, and operational practices.

3. **Build the architecture model (source of truth)**
   - Derive the set of architecture entities (system, containers, components, supporting infrastructure) from the analysis.
   - Decide on the new `model_version`. Start at `1.0.0` for the first run and increment the PATCH component only (`1.0.1`, `1.0.2`, … up to `1.0.99`) for each subsequent run unless you receive explicit instructions to change the scheme. Apply the same patch-only increment rule to individual view versions in the `views` map.
   - Assemble `specs/architecture/architecture.json` with the following structure:
     - `model_version`: string semver for the overall model
     - `generated_at`: ISO-8601 timestamp
     - `source`: `{ "tool": "specify.architecture.create", "commit": <git sha or null> }`
     - `overview`: `{ "path": "specs/architecture/architecture_overview.md", "version": <semver for the overview doc> }`
     - `views`: map of view identifiers (e.g., `c1/system`, `c2/<container>`, `c4/<component>`) to `{ "path": <file path>, "version": <semver>, "checksum": <sha256 of final file>, "last_updated": <ISO timestamp> }`
     - `containers`: array of objects describing each container:
       - `name`, `slug`, `summary`
       - `views`: list of Markdown files that describe the container (C2/C3/C4 artefacts)
       - `components`: array of component objects with `name`, `slug`, `summary`, `views`
     - `log`: `{ "path": "specs/architecture/architecture_logs.md", "latest_entry": <model_version> }`
   - Treat `architecture.json` as the single source of truth; every Markdown document must be derivable from it.

4. **Persist the model before generating Markdown**
   - Write the fully populated `architecture.json` to disk (overwrite the old version atomically).
   - Append a new section to `architecture_logs.md` recording the `model_version`, timestamp, notable changes, affected views, and follow-up actions.

5. **Materialise architecture views**
   - Follow the directory layout documented in `architecture_repository.md`.
   - Populate `c2_containers/containers_overview.md` using the guidance from `.specify/templates/c2-containers-overview-template.md`.
   - Create a dedicated subdirectory under `c2_containers/` for each container and generate `container_diagram.md`.
   - Under `c3_components/`, create a folder per container; within each, create folders per component and generate `components_overview.md` (following `.specify/templates/c3-components-overview-template.md`) plus individual `component_diagram.md` files guided by `.specify/templates/c3-component-diagram-template.md`.
   - Under `c4_code/`, create a directory per component that needs code-level detail and write `code_structure.md` aligned with the model, including database schema summaries (ER diagrams, key tables, constraints) as guided by `.specify/templates/c4-code-structure-template.md`.
   - Populate `c1_context/system_context.md`, `c5_dynamic_view/view_diagram.md`, and `c6_deployment/deployment_diagram.md` with rich narratives and diagrams that follow the updated Mermaid scaffolds (flowchart + sequence where required).
   - Populate `c7_tests/tests_overview.md` using `.specify/templates/c7-tests-template.md` to capture strategy, coverage matrix, and follow-up actions.
   - Ensure every component-level artefact includes both a structural flowchart, a `sequenceDiagram`, and explicit security considerations (use the templates to cover threats, auth, data protection, and monitoring).
   - Prepend every Markdown file with navigation links that mirror the templates (overview, parent, and next logical view).
   - After writing each file, update the corresponding entry in `architecture.json` with the final checksum and `last_updated` timestamp.
   - Normalise encodings immediately after writing: for each generated path run a short helper such as  
     ```bash
     python - <<'PY'
     from pathlib import Path
     path = Path("<file>")
     text = path.read_text(encoding="utf-8-sig")
     path.write_text(text, encoding="utf-8")
     PY
     ```
     (adjust for PowerShell). This guarantees UTF-8 output without a BOM so Mermaid diagrams render correctly.
   - Validate Mermaid syntax: run `npx @mermaid-js/mermaid-cli -i <diagram-file> -o /tmp/diagram.svg` when available (or paste into https://mermaid.live) to confirm diagrams render without lexical errors.

6. **Update the overview**
   - Refresh `architecture_overview.md` with a narrative summary, highlight high-risk decisions, and clearly state the latest `model_version` and generation timestamp.
   - Generate the `## Table of Contents` section so it contains Markdown links to every generated view file (use the `views` map in `architecture.json` to derive the list).
   - Ensure the overview references the JSON model and change log so readers can trace provenance.

7. **Report**
   - Summarise the analysis, mention major subsystems, data stores, external dependencies, and generated artefacts.
   - Provide next steps or verification ideas if there are gaps.

## Output Expectations
- `specs/architecture/architecture.json` is the authoritative model and reflects the latest `model_version`, view metadata, and container/component inventory.
- `specs/architecture/architecture_logs.md` contains an entry for the new `model_version`.
- Architecture directory contains refreshed Markdown views that adhere to the guidance in `.specify/templates/c*-*-template.md` and the layout documented in `architecture_repository.md`.
- Overview mirrors the generated views, calls out key characteristics, includes a table of contents, and references the JSON model.
- All generated files are saved as UTF-8 (no BOM) to keep Mermaid diagrams and downstream tooling functioning correctly.
- `c7_tests/tests_overview.md` documents the agreed testing strategy, coverage levels, and follow-up actions.
- Final response links to updated files and summarises key findings.
