## Done

A slice is done when every line that applies is true. Size it by risk: the **full set** applies when the slice
touches anything in `merge_gate.high_risk`; otherwise the **light set** does.

**Light set** (docs, chores, small fixes):
1. Tests and lint pass locally for what changed.
2. The doc or spec that owns the changed behaviour is updated in the same PR.
3. The area's status file is updated in the same PR.
4. One review pass over the diff.

**Full set** (everything in the light set, plus):
5. The full test suite passes at the PR's head.
6. A thorough review of the diff, plus an independent second reviewer (the coordinator arranges it).
7. Tests that prove the risky property: for example, one user can't read another's data, or money adds up.
8. If there's a UI, check each touched screen on the devices your users have.
9. A security review when auth, permissions or personal data are involved.

Replace these lines with your project's own tools and commands as they settle.
