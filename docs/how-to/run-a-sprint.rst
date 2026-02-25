Run a Sprint
============

1) Create or select an ARC.
2) Create Sprint ID: <ARC-ID>-SPRINT-YYYYMMDD-XX.
3) Stage 2 planning outputs go to `.agile/workspace/`.
4) SM gates at Stage 3.
5) Only then: `EXECUTE SPRINT <SPRINT-ID>`.

Unstuck a blocked PR
--------------------

If a PR is blocked by merge conflicts, create a small follow-up PR from latest target branch:

1) Update local target branch (for example `main`) and branch off a new fix branch.
2) Re-apply only required changes with minimal scope.
3) Run project checks before commit.
4) Open a fresh PR and close/replace the blocked one.

Recommended conflict workflow:

- Keep the old PR as audit trail.
- Reference old PR in the new PR description.
- Prefer small, reviewable commits to reduce future conflicts.
