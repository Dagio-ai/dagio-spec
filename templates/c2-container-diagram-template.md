# <container-name> - Container Diagram

> <small>[Architecture Overview](../../architecture_overview.md) > [Containers Overview](../containers_overview.md) > <strong><container-name> - Container Diagram</strong></small>

_Replace `<container-name>` above with the actual identifier for this container._

Use this guidance when building the container-level view with `/specify.architecture.create`.

## What to cover
- **Purpose**: explain why the container view is useful to engineers and stakeholders.
- **Scope**: define the runtime boundaries covered (apps, services, data stores, external providers).
- **Containers table**: name, technology, primary responsibility for each container.
- **Relationships**: describe how containers interact with each other and with external systems.
- **Diagram**: Mermaid `flowchart` layout with subgraphs to keep containers aligned (see example below).
- **Notes**: deployment considerations, security boundaries, observability requirements.

## Diagram scaffold
Use a flowchart with explicit subgraphs to avoid overlapping nodes. Replace the placeholders with real containers and dependencies.

````markdown
```mermaid
flowchart LR
    %% Encourage predictable spacing
    linkStyle default stroke-width:2px,color:#555;

    subgraph Clients
        user[Primary User]
    end

    subgraph Core["<System Name>"]
        web[Web App\nNext.js]
        api[API Gateway\nFastAPI]
    end

    subgraph Data
        db[(Primary Database\nPostgreSQL)]
    end

    user --> web
    web --> api
    api -.-> db
```
````

Add additional subgraphs (for example, `External Services`) or `style` directives when you need more separation. Use arrow annotations (`-->`, `-.->`, `==>`) to convey protocol or synchronicity.

## Quality checklist
- Every container maps to a deployable or independently scalable runtime unit.
- Data stores and external dependencies are connected with labelled relationships.
- Notes capture reliability, performance, or compliance topics tied to each container.
- Diagram uses subgraphs/spacing so nodes remain legible (no overlapping labels).

## Linked Components
- List each component belonging to this container and link to `../../c3_components/<container-slug>/<component-slug>/component_diagram.md` (use Markdown bullet links with the name of the component) and a brief description of the component's role outside the link.
- Ensure the section stays in sync with the container inventory and components overview (no orphan links).
