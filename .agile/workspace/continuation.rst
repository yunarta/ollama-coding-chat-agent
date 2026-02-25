What: BO asked to unblock stuck merge/conflict flow by creating a fresh PR path.
Delivered: Added runbook guidance for handling blocked PRs with a clean follow-up branch/PR.
Decision: Prefer a new small replacement PR over fighting large stale conflict stacks.
Flow: Rebase/branch from latest target branch, re-apply minimal changes, run checks, open fresh PR.
Flow: Keep old PR as audit trail and cross-link it in replacement PR description.
Risk: Longer-lived branches increase conflict probability; enforce smaller PR slices.
Validation: Documentation updated under allowed write scope.
Next: BO can proceed with replacement-PR workflow immediately to unblock merge.
