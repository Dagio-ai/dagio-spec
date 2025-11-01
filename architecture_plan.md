# Architecture Workflow Updates - Work Plan

## Objectives
- Introduce a model-as-data source of truth (`specs/architecture/architecture.json`) that `/specify.architecture.create` produces before generating C1-C6 artefacts.
- Expand the architecture command set so C2-C4 views are emitted per container/component, aligned with the structure described in `architecture_repository.md`.
- Enhance `architecture_overview.md` with a table of contents linking to every generated file and ensure `architecture.json` indexes all containers/components with version metadata for selective updates.

## Tasks
1. **Architecture JSON Source of Truth** *(complete)*
   - Update the architecture command templates (both create/update) to instruct agents to write `specs/architecture/architecture.json` first.
   - Define the JSON schema (global metadata, per-view records with version hashes, container/component inventories).
   - Adjust helper scripts and CLI scaffolding so the file is created when missing and preserved during updates.
   - Ensure `/specify.architecture.update` compares versions to decide which view files to refresh.

2. **Per-Container C2/C3/C4 Outputs** *(complete)*
   - Rework prompt templates so the agent emits one file per container/component (e.g., `c2_containers/<container>/container_diagram.md`, `c3_components/<container>/<component>/component_diagram.md`, `c4_code/<component>/code_structure.md`).
   - Sync `architecture.json` to record generated paths and ownership.
   - Verify the workflow with `architecture_repository.md` structure; update scripts that enumerate architecture files.

3. **Architecture Overview & Logging Enhancements** *(complete)*
   - Update the overview template to generate a Markdown table of contents pointing to every generated artefact and record the architecture model version.
   - Ensure `architecture.json` stores per-view, per-container, and per-component version metadata plus a history pointer to `architecture_logs.md`.
   - Design the workflow so each regeneration appends a summary entry to `architecture_logs.md` (version, date, affected files, rationale).
   - Document expectations in the command prompts so agents keep the overview, JSON index, and log aligned.

4. **Tooling & Documentation** *(complete)*
   - Extend helper scripts (bash/PowerShell) to surface the JSON schema and new file layout.
   - Update README and docs to explain the model-as-data workflow.

5. **Rename template files** *(complete)*
   - Converted all architecture templates to the `*-template` naming convention (e.g., `c1-system-context-template.md`, `c4-code-structure-template.md`, `c6-deployment-template.md`).
   - Updated supporting templates (`architecture_overview-template.md`, `architecture_logs-template.md`, `architecture-template.json`) and CLI constants/prompts to reference the new filenames.

6. **Complete c2-containers-overview-template.md** *(complete)*
   - Replaced the example content with a reusable guidance template for summarising all containers.
   - Updated the architecture create prompt to call out the overview file so agents follow the new template.
   
7. **Complete c3-components-overview-template.md** *(complete)*
   - Replaced the sample component listing with a reusable template focused on container decomposition.
   - Updated the architecture prompts so `components_overview.md` generation follows `.specify/templates/c3-components-overview-template.md`.

8. **Remove components_overview.md under c3_components folder** *(complete)*
   - Adjusted helper scripts so the default view set no longer references a root-level `components_overview.md`.
   - Agents now generate one `components_overview.md` per container only, using the templated guidance under `.specify/templates/`.
  
9. **Update Table of Contents guidance** *(complete)*
   - Restored the nested Table of Contents example so agents mirror the provided C4 hierarchy when composing links.

10. **Navigation Links** *(complete)*
   - Added navigation blocks to every architecture template so views link back to the overview, parent, and next logical documents.
   - Updated architecture commands to require maintaining these headers during create/update flows.

11. **Update the specs/architecture/Readme.md file** *(complete)*
   - Documented the index (`architecture_overview.md`) and change-log (`architecture_logs.md`) files in `specs/architecture/README.md`.
   - Reinforced the expectation that `architecture.json` remains the authoritative source of truth for all Markdown artefacts.
