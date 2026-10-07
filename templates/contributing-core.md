# Contributing

How work moves from an idea to production, for every agent: the home team's and any outside team's.

## Branches

| Branch | Role | Who changes it |
|---|---|---|
| `<work_branch>` | The trunk every slice branches from and targets | Merged PRs only |
| `<production_branch>` | Production | **Only a human**, by merging a PR from `<work_branch>` (or a hotfix, see "Production problems") |
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
   in the same PR. New owner decisions go in the body under `## Decisions`, never into `<docs.decisions>` itself:
   the coordinator appends them when it merges.
6. **Mark it ready.** That replaces any "ready" message. While you work on review fixes, put it back to draft
   (`gh pr ready <N> --undo`), then mark it ready again.
7. **Check the PR is still open before you push more commits** (`gh pr view <N> --json state`). A commit pushed
   after a merge never reaches `<work_branch>`; open a new PR instead.

## The merge gate

- **Through the coordinator:** anything touching `<merge_gate.high_risk>`, shared platform code, or a contract
  between modules. These get an independent second reviewer too.
- **Self-merge allowed** once the DoD evidence is in the body: `<merge_gate.self_merge_ok>`. This is for the home
  team only; **outside teams never merge.**
- **`<production_branch>`:** only a human.

After a merge, delete the head branch. First list the PRs that use it as their base and retarget them to
`<work_branch>`: GitHub closes a PR whose base branch is deleted, for good. It can't be reopened or retargeted, only
replaced by a new PR from the same branch.

## The owner's decisions and steps

- **Only the owner's own words are a decision.** An agent passing on an instruction, the coordinator included, never
  stands in for them: **a relay is not approval.** Record each decision as a row in the PR that uses it, with the
  owner's words copied exactly and where they said them (the chat's name, the date). If two answers differ, the
  later one governs.
- **Whatever waits on the owner is an issue labelled `needs:owner`:** the question, the options with a
  recommendation, and what waits on the answer. The owner answers in chat as usual. The agent they told then
  copies the exact words onto the issue as a comment, acts, records the decision row and closes it. Never close
  one without the owner's own words on it.
- **A step only the owner can do** (a console, a command on their machine, a sign-in) is also labelled `owner:do`.
  It says why, gives exact steps with no secret in them, what the owner should see when it worked, and what to send
  back. Agents prepare these steps; the owner performs them.
- **The owner runs one wizard, never a command list.** For anything on their own machine: one interactive script
  that asks what it needs and calls one-job scripts, the same ones agents use and test. The exception is a step
  that already has a console UI (cloud, hosting, repository settings): give click-by-click steps there.
- **Sweep, don't sample.** When the owner asks for a "don't forget" task, it lists every owner-pending item from
  the conversation: decisions, habits to adopt, parked work, running costs. Each item has its full steps and what to
  send back.

## Production problems

- **Roll back first, investigate second.** If the release is under an hour old and the problem started with it,
  roll back to the previous release. Otherwise fix forward. A rollback only works if the release before can still
  read what the new one wrote, so schema changes add and never drop or rename in the same release.
- **The hotfix lane.** A production fix may skip a release freeze. Branch from `<production_branch>`, get one review
  by `<merge_gate.reviewer_model>`, and let a human merge and deploy it. Then merge it back into `<work_branch>` the
  same day.
- **After every incident,** one note on its issue: the cause, the fix, and the test or check added. A repeat gets a
  check that would have caught it.

## Scripts for the mechanical steps

- **A script for what is mechanical, repeated and error-prone; an agent for judgement.** Every tool call re-reads
  the whole conversation, so a step done by hand costs tokens every time and can slip every time. Reviews, specs,
  priorities and anything only the owner decides stay with an agent.
- **A script is small and strict:** bash or standard-library Python, GitHub through `gh`, a body read fresh before
  it is changed, a refusal in one line (changing nothing) instead of a guess, one line of output per fact, and a test
  with a stand-in `gh`. It never reads or prints a secret.

## One working session per task, and the right model

- **Start each slice in a fresh session** once none of your PRs is still open. A long conversation is re-read on
  every call and is most of an agent's cost. The rules live in the repository and the work state on GitHub, so
  nothing is lost.
- **Choose the model by the slice's risk:** the strongest for anything in `<merge_gate.high_risk>` and for design
  work, a faster one for docs and routine fixes. Never switch mid-task.

## Sharing one machine or clone

- **No `git stash`.** A clone's worktrees share one stash, and a pop can apply another agent's changes. Commit work
  in progress instead.
- **One test-database name per worktree.** Two runs on one name collide, and a killed run leaves rows behind, so
  rerun on a fresh name.
- **Never kill another agent's server.** Find out who owns a port before you free it. Each agent runs its
  end-to-end tests on its own ports.

## Keeping docs current

Whoever changes something updates the doc that owns it, in the same PR. There's no separate documentation task. One
topic lives in one file; every other file links to it.
