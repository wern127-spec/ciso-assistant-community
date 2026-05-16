# Business Continuity module

A service-centric Business Continuity (BC) module. It answers one question for
each business service: *"If this service goes down, what is the impact, what do
we depend on, what is our plan, and have we tested it?"*

## Concepts (5 objects)

| Object | What it is |
|---|---|
| **Business service** | A service the organisation delivers (e.g. Service Desk, Email). Holds criticality, RTO/RPO/MTPD, owner, domain impact. |
| **Service–asset link** | Connects a service to an asset it relies on, with a dependency type (Critical / Important / Supporting) and the impact if that asset is lost. |
| **Asset recovery procedure** | A procedure (Backup / Restore / Failover / Hardening / Monitoring) describing how to recover a specific asset. |
| **Continuity plan** | The plan for a service: scenario, recovery strategy, procedure steps, responsible team, review dates, status. |
| **Continuity plan test** | A recorded exercise of a plan: date, type (Tabletop / Walkthrough / Simulation / Full recovery), result, findings, actions. |

## Aggregate service view (main screen)

`/business-services/{id}` is a dedicated read view that assembles everything
about one service into 7 sections: domain breadcrumb, parameters, domain
impact, assets used (with dependency & recovery procedures), continuity plan,
test history (newest first, colour-coded result), and action buttons. It is a
purpose-built page (single `overview` API call) — independent of the generic
detail page.

## API

Under `/api/business-continuity/`:
`business-services/`, `service-asset-links/`, `continuity-plans/`,
`continuity-plan-tests/`, `asset-recovery-procedures/` — standard DRF list /
retrieve / create / update / delete, plus
`business-services/{id}/overview/` for the aggregate view and the usual choice
endpoints (e.g. `business-services/criticality/`).

## Permissions

Standard CISO RBAC: READER/APPROVER get view rights on all 5 objects;
ANALYST/DOMAIN_MANAGER/ADMINISTRATOR get full CRUD. Each object is scoped to a
folder/domain like the rest of CISO Assistant.

## Demo data

```
python manage.py populate_business_continuity --fresh
```

Creates the domain *"BC Demo - IT Operations"* with 2 services (Service Desk,
Email Service), 5 assets, 5 recovery procedures, 2 continuity plans and 5
tests. Idempotent; `--clean` removes it.

## Known limitation

The **generic detail page** for individual sub-objects (a single continuity
plan / test / procedure / link) returns HTTP 500. The error is raised before
the page's load function runs and is not exposed by SvelteKit's default error
handling. It does **not** affect the aggregate service view (which uses its own
route), the list views, or record creation. Tracked for a future fix.
