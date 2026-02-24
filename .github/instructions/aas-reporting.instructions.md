---
applyTo: ".agile/reports/**"
---
# AAS Reporting Rules (Sphinx-ready) — v5

- Reports are immutable once a sprint is closed.
- Reports are organized by ARC:
  - `.agile/reports/arcs/<ARC-ID>/sprints/<SPRINT-ID>/`

Each sprint folder includes:
- `run-report.rst`
- `demo-pack.rst`
- `verification-summary.rst`
- `retro-report.rst`
- `index.rst` (toctree for this sprint)

Evidence lives under:
- `.agile/reports/evidence/<SPRINT-ID>/`

Use reStructuredText to avoid parser drama.
