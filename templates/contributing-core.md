# Contributing

How work moves from an idea to production, for every agent: the home team's and any outside team's.

## Branches

| Branch | Role | Who changes it |
|---|---|---|
| `<work_branch>` | The trunk every slice branches from and targets | Merged PRs only |
| `<production_branch>` | Production | **Only a human**, by merging a PR from `<work_branch>` |
| `feat/…`, `fix/…`, `docs/…`, `chore/…` | One slice | Its author; deleted after merge |

Never commit straight to `<work_branch>` or `<production_branch>`.

## The path of a change

1. **Plan first for anything new.** A short spec is approved before building.
2. **Claim it** with a draft PR from `<work_branch>` as soon as you start. The open PR list is the live list of who
   does what. Check it for an overlapping claim before you start. If the slice adds a schema migration, put its
   number in the title so clashes show. A PR targets `<work_branch>`; the one exception is a stacked PR, which
   targets its parent's branch until the parent merges and says so in its body.
3. **Build** in your own working copy. Batch your fixes, run the affected tests, then push once. Bring
   `<work_branch>` in with `git merge`; never rebase or force-push a branch that has been pushed.
4. **Meet the definition of done** (`<docs.definition_of_done>`), sized by risk.
5. **Describe it in the PR body** (the template lists what), and update the doc that owns any behaviour you changed
   in the same PR.
6. **Mark it ready.** That replaces any "ready" message. While you work on review fixes, put it back to draft
   (`gh pr ready <N> --undo`), then mark it ready again.

## The merge gate

- **Through the coordinator:** anything touching `<merge_gate.high_risk>`, shared platform code, or a contract
  between modules. These get an independent second reviewer too.
- **Self-merge allowed** once the DoD evidence is in the body: `<merge_gate.self_merge_ok>`. This is for the home
  team only; **outside teams never merge.**
- **`<production_branch>`:** only a human.

After a merge, delete the head branch. First check that no other PR uses it as its base, because GitHub may close a
stacked PR instead of retargeting it.

## Keeping docs current

Whoever changes something updates the doc that owns it, in the same PR. There's no separate documentation task. One
topic lives in one file; every other file links to it.
