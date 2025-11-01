# Architecture Directory

This folder stores the artefacts produced by `/specify.architecture.create` and `/specify.architecture.update`.

## Index Files
- `architecture_overview.md`: Entry point for the architecture documentation, including the table of contents linking to every view.
- `architecture_logs.md`: Versioned change log describing updates recorded in `architecture.json`.
- `c7_tests/tests_overview.md`: Centralised summary of the automated/manual test coverage supporting the architecture.

## Expected layout

```
architecture/
  c1_context/
    system_context.md
  c2_containers/
    containers_overview.md
    <container-slug>/
      container_diagram.md
  c3_components/
    <container-slug>/
      components_overview.md
      <component-slug>/
        component_diagram.md
  c4_code/
    <component-slug>/
      code_structure.md
  c5_dynamic_view/
    view_diagram.md
  c6_deployment/
    deployment_diagram.md
  c7_tests/
    tests_overview.md
  architecture_overview.md
  architecture_logs.md
  architecture.json
```

The JSON model (`specs/architecture/architecture.json`) acts as the source of truth and drives the Markdown views. Treat any Markdown edits as projections that must be reconciled back into the JSON model.

## Mermaid Validation

- Install Mermaid CLI once per machine: `npm install -g @mermaid-js/mermaid-cli` (provides the `mmdc` command).
- Validate diagrams whenever they are generated or updated: `mmdc -i <diagram-file> -o /tmp/diagram.svg` (or `npx @mermaid-js/mermaid-cli`).
- When collaborating with an AI assistant, call out that Mermaid validation is expected so it reruns fixes until `mmdc` succeeds.
