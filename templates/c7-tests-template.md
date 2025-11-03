# Tests Overview

> <small>[Architecture Overview](../architecture_overview.md) > <strong>Tests Overview</strong></small>

Use this guidance to document the test strategy, coverage, and automation status captured during `/specify.architecture.create`.

## Strategy Summary
- Describe the overall testing philosophy (for example, shift-left, automation-first, contract-driven).
- Highlight environments, pipelines, and tools (CI, QA platforms, device labs).
- Note ownership (teams, squads) and gating policies for releases.

## Coverage Matrix
Provide an exhaustive table covering every suite/layer you run. Duplicate rows as needed.

| Suite / ID | Description | Layer (unit/integration/e2e/contract/load/etc.) | Owner / Team | Entry Points (commands, files, pipelines) | Pass Criteria | Current Status (pass/fail/blocked) | Coverage Focus (modules/features) | Known Gaps / Risks | Last Execution (timestamp/pipeline) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| _example: svc-orders-unit_ | Unit tests for order service domain logic. | Unit | Platform Core | `pytest ./src/orders/tests` | 100% pass, coverage >= 85% | Failing (2 tests) | Orders domain models, adapters | Missing tests for edge cases around refunds | 2025-01-15 (CI #1234) |
| _example: api-gateway-contract_ | Provider/consumer tests for API gateway endpoints. | Contract | API Platform | `pnpm test:contract` | All contracts verified | Blocked (mock service down) | Checkout & billing endpoints | Waiting on billing mock fix | 2025-01-14 (CI #1230) |

Replace rows with actual suites, tools, and status (pass/fail/blocked). Add more tiers (contract, visual regression, load) as needed.

## Test Artefacts
- **Key suites / tools**: list frameworks (pytest, Playwright, k6), runners, fixture libraries.
- **Generated outputs**: coverage reports, screenshots, log bundles, trace files.
- **Data management**: seeding strategy, anonymisation, reset policies.

## Security & Quality Signals
- Summarise recent test results (pass rates, MTTR for failures).
- Capture known flaky tests or gaps awaiting automation.
- Reference dashboards or reports (CI URLs, analytics).

## Follow-up Actions
- Use bullet list to track remediation tasks (for example, "Automate contract tests for invoices API by Q4").
- Map actions back to architecture components so `/specify.architecture.update` can prioritise.
