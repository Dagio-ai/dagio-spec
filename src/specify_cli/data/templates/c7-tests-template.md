# Tests Overview

> <small>[Architecture Overview](../architecture_overview.md) > <strong>Tests Overview</strong></small>

Use this guidance to document the test strategy, coverage, and automation status captured during `/specify.architecture.create`.

## Strategy Summary
- Describe the overall testing philosophy (for example, shift-left, automation-first, contract-driven).
- Highlight environments, pipelines, and tools (CI, QA platforms, device labs).
- Note ownership (teams, squads) and gating policies for releases.

## Coverage Matrix
| Tier / Suite | Purpose | Key Targets | Status | Notes |
| --- | --- | --- | --- | --- |
| _Unit_ | _Validate isolated functions/services._ | _Core libraries, pure functions._ | _In-progress_ | _Add missing coverage for billing calculators._ |
| _Integration_ | _Exercise container/component boundaries._ | _API + DB, messaging bridges._ | _Planned_ | _Depends on local test harness refresh._ |
| _End-to-End_ | _Validate user journeys and regression flows._ | _Checkout, onboarding._ | _Automated_ | _Nightly run; flake rate < 3%._ |

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
