---
description: Use the AI assistant to refresh architecture artefacts based on `architecture.json` model data.
scripts:
  sh: scripts/bash/architecture-info.sh
  ps: scripts/powershell/architecture-info.ps1
---

## User Input

```text
$ARGUMENTS
```

Clarify whether the user wants a full refresh or targeted updates (specific containers/components/views).

## Required Flow

1. **Gather context**
   - Run `{SCRIPT}` from the repo root to obtain the current file inventory.
   - Load `specs/architecture/architecture.json`; abort with guidance if the file does not exist (the user must run `/specify.architecture.create` first).
   - Capture the existing `model_version`, per-view versions, container/component definitions, and last log entry.
   - Review `specs/architecture/architecture_overview.md` and `specs/architecture/architecture_logs.md` to understand recent changes and outstanding TODOs.
   - Refer to `architecture_repository.md` to keep the directory layout consistent when adding or removing artefacts.

2. **Assess required updates**
   - Determine which parts of the architecture are affected (system-wide, container-level, component-level, or documentation-only updates).
   - For each impacted view, bump only the PATCH component (e.g., `1.0.2` -> `1.0.3`) to stay aligned with the `1.0.x` lifecycle.
   - Decide whether the overall `model_version` also needs a bump. Follow the patch-only progression (`1.0.0`, `1.0.1`, … `1.0.99`) unless explicitly instructed otherwise.

3. **Update the architecture model**
   - Modify `architecture.json` first:
     - Update `model_version`, `generated_at`, and `source.commit`/metadata.
     - For each touched view entry, update `version`, clear or mark `checksum` pending recompute, and set a provisional `last_updated` timestamp.
     - Adjust container/component structures to reflect additions, removals, or renamed elements (make sure every container and component still includes the correct `views` list).
   - Persist the updated JSON before regenerating Markdown.

4. **Regenerate required Markdown views**
   - Refresh only the files identified in step 2, ensuring the content aligns with the revised JSON model.
   - Maintain the folder hierarchy:
     - `c2_containers/<container>/container_diagram.md`
     - `c3_components/<container>/<component>/component_diagram.md`
     - `c4_code/<component>/code_structure.md`
   - Rebuild summary files using the templates in `.specify/templates/` (e.g., `c2-containers-overview-template.md`, `c3-components-overview-template.md`) before refreshing individual container/component diagrams.
   - Confirm each regenerated Markdown file retains the navigation header (overview, parent, and next links updated to the current structure).
   - Ensure component-level artefacts still include both structural flowcharts and `sequenceDiagram` blocks as defined in the templates, and refresh the security considerations section (auth, data protection, monitoring).
   - After writing each file, compute its checksum (e.g., SHA-256) and update the corresponding entry in `architecture.json` with the definitive checksum and `last_updated` timestamp.
   - Ensure the tests overview (`c7_tests/tests_overview.md`) stays in sync with recent coverage updates before finalising the run.
   - Confirm `code_structure.md` files capture the current database schema (tables, relationships, constraints) when changes have occurred.
   - Re-save every generated file as UTF-8 without BOM. For each path you can run:
     ```bash
     python - <<'PY'
     from pathlib import Path
     path = Path("<file>")
     text = path.read_text(encoding="utf-8-sig")
     path.write_text(text, encoding="utf-8")
     PY
     ```
     (adjust for PowerShell).
   - Validate Mermaid syntax for updated diagrams (`npx @mermaid-js/mermaid-cli -i <diagram-file> -o /tmp/diagram.svg` or mermaid.live) to catch lexical errors before delivery.

5. **Update overview and change log**
   - Revise `architecture_overview.md` with the latest `model_version`, highlight what changed, and regenerate the `## Table of Contents` so it links to every view listed in `architecture.json`.
   - Append a new entry to `architecture_logs.md` that records the version bump, timestamp, impacted views, and follow-up actions.

6. **Report**
   - Summarise the changes, explicitly listing updated files and the new versions recorded in `architecture.json`.
   - Call out remaining risks or TODOs.

## Output Expectations
- `specs/architecture/architecture.json` is updated first and reflects the new `model_version`, per-view versions, and container/component inventory.
- Only the necessary Markdown files (C1 through C6 plus per-container/per-component documents) are regenerated, and each has a refreshed checksum/timestamp recorded in the JSON model.
- `specs/architecture/architecture_logs.md` includes a new entry describing this update.
- `architecture_overview.md` references the current `model_version`, includes a table of contents, and summarises changes.
- All regenerated files are written using UTF-8 (no BOM).
- `c7_tests/tests_overview.md` reflects the latest automation status and any required remediation work.
- Final response lists updated files, bumped versions, and next steps.
