# System Context

> <small>[Architecture Overview](../architecture_overview.md) > <strong>System Context</strong></small>

Use this guidance when generating the system context view with `/specify.architecture.create`.

## What to cover
- **Purpose**: one paragraph explaining why the system exists and which outcomes it supports.
- **Scope**: bullet list describing the system boundary and core audiences.
- **Primary elements**: Markdown table of people, our system, and adjacent/external systems with short descriptions.
- **Relationships**: summary of critical interactions and data exchanges between actors and the system.
- **Diagram**: Mermaid `flowchart` (or `graph`) showing the system boundary, users, and integrations; group related actors with `subgraph` blocks so the layout stays readable.
- **Notes**: constraints, compliance considerations, open questions, or risks.

## Quality checklist
- Every actor or external service referenced in downstream views appears here.
- Data flows are labelled with verbs that describe the interaction.
- Notes call out key assumptions or integration contracts worth validating.

## Security Overview
- Identify trust boundaries, authentication/authorisation actors, and data classification at the system level.
- Highlight privacy/compliance obligations (GDPR, SOC2, HIPAA) and how they influence integration decisions.
- List known threats or open security questions that downstream views must address.

