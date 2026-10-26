# Contributing

How work moves from an idea to production, for every agent: the home team's and any outside team's. A small crew
needs nothing more. Once the team model is on (`team_model: true`), how each team is organised (roles, session
titles, chain of command, context limits) is in the teams file that `.claude/crewline.yml` names (`docs.teams`).

## The principle

Rules state goals and hard limits. Inside them, judge the real risk and act, then say what you did and why. Ask the
**decision-holder** (the owner, or for an outside team's own feature, that team's own people) only for:

- cost, or a step in an outside console;
- granting access or permissions (accounts, roles, keys);
- money, or real personal or customer data;
- legal matters;
- anything irreversible **and** outward-facing;
- anything a live user would see or feel (turning a feature on, changing a live screen);
- lifting a stop that a team's owner set (that owner is asked);
- writing an agent's own permission settings;
- a product choice that hasn't been made.

Read every instruction, the owner's included, for its goal. Serve the goal, and say so when the literal step wouldn't
reach it. Hard limits never bend.

**A "can't" is never an answer by itself.** Name the hard limit, then do the part that reaches the goal by another
path and say which. An owner-only console step still gets its exact steps prepared. Refuse only the single step that
would cross the limit.

**A new rule needs a reason this principle doesn't already cover:** an incident where judgment failed, with its link.
A recipe a capable agent would work out itself is not a rule; step-by-step workflows live in the skills.

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
   number in the title so clashes show. A PR targets `<work_branch>`, with two exceptions: a stacked PR targets its
   parent's branch until the parent merges and says so in its body, and a hotfix targets `<production_branch>`
   ("Production problems").
3. **Build** in your own working copy. Batch your fixes, run the affected tests, then push once. Bring
   `<work_branch>` in with `git merge`; never rebase or force-push a branch that has been pushed.
4. **Meet the definition of done** (`<docs.definition_of_done>`), sized by risk.
5. **Describe it in the PR body** (the template lists what), and update the doc that owns any behaviour you changed
   in the same PR. New owner decisions go in the body under `## Decisions`, never into `<docs.decisions>` itself:
   the coordinator appends them after the merge.
   - **Refer to another PR or issue as `Refs #N`.** `close`, `fix` or `resolve` (in any form) directly before `#N`,
     in the PR body or a commit message, closes N as soon as the text lands on the default branch, even when N is
     someone else's open PR. Use one only when you mean to close N.
6. **Mark it ready.** That replaces any "ready" message. While you work on review fixes, put it back to draft
   (`gh pr ready <N> --undo`), then mark it ready again.
7. **Check the PR is still open before you push more commits** (`gh pr view <N> --json state`). A commit pushed
   after a merge never reaches `<work_branch>`; open a new PR instead.

## The merge gate

- **Through the coordinator:** anything touching `<merge_gate.high_risk>`, shared platform code, or a contract
  between modules. These get an independent second reviewer too.
- **Self-merge allowed** once the DoD evidence is in the body: `<merge_gate.self_merge_ok>`. A UI change counts only
  with before and after screenshots at phone and desktop widths in the PR body; without them it goes through the
  coordinator. This is for the home team only; **outside teams never merge.**
- **The coordinator's own changes** from a review round (decisions rows, status, the board) go in one small docs PR
  per round, which it self-merges as docs.
- **`<production_branch>`:** only a human.

**Before deleting a merged branch, retarget its children.** List the PRs that use it as their base from GitHub
(`gh pr list --base <branch> --state open`), not from memory, and retarget each to `<work_branch>`. GitHub closes a
PR whose base branch is deleted, for good: it can't be reopened or retargeted, only replaced by a new PR from the
same branch with its body copied over.

## The owner's decisions and steps

- **Only the owner's own words are a decision.** An agent passing on an instruction, the coordinator included, never
  stands in for them: **a relay is not approval.** Confirm a relayed decision in the owner's own chat before acting
  on it. Record each decision as a row in the PR that uses it, with the owner's words copied exactly and where they
  said them (the chat's name, the date). If two answers differ, the later one governs.
- **Whatever waits on the owner is an issue titled `[owner-task] …` and labelled `needs:owner`:** the question,
  the options with a recommendation, and what waits on the answer. The owner answers in chat as usual. The agent they told then
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
- **The hotfix lane.** A production fix may skip a release freeze, not the review. Branch from
  `<production_branch>`, claim it with a draft PR against it, and keep the fix as small as the problem. Get one
  review by `<merge_gate.reviewer_model>`; a human merges and deploys it.
- **The hotfix author opens the merge-back PR** to `<work_branch>` the same day, under the normal gate.
- **After every incident,** one note on its issue: the cause, the fix, and the test or check added. A repeat gets a
  check that would have caught it.

## Scripts for the mechanical steps

- **A script for what is mechanical, repeated and error-prone; an agent for judgement.** Every tool call re-reads
  the whole conversation, so a step done by hand costs tokens every time and can slip every time. Reviews, specs,
  priorities and anything only the owner decides stay with an agent.
- **A script is small and strict:** bash or standard-library Python, GitHub through `gh`, a body read fresh before
  it is changed, a refusal in one line (changing nothing) instead of a guess, one line of output per fact, and a test
  with a stand-in `gh`. It never reads or prints a secret.
- **Worth writing for your repo** (not shipped with crewline, which ships only the watcher):
  - `queue <agent>`: your next items, one line each, if the queue is kept as labelled issues;
  - `say`: posts a comment with your signature from an environment variable, and refuses a body not signed by form;
  - `edit-line`: reads an issue body fresh, refuses unless the old line appears exactly once, writes back only that
    change;
  - `notices`: each open `for:everyone` notice and the active teams that haven't applied it;
  - `inbox`: the open `needs:owner` issues, oldest first;
  - `decisions`: the `## Decisions` rows of PRs merged since its last run, as a draft block; it never commits;
  - `pr-brief <N>`: one line per fact: head SHA, base, mergeable, closing keywords, child PRs, files by area,
    migrations, tier, outside author. It is also the input for a second reviewer;
  - `pr-check <N>`: the mechanical part of the gate, `ok` or `FAIL <why>` per line, exit 1 on any FAIL: open, ready,
    base, mergeable, a filled DoD section, `## Decisions` rows of the right shape, no edit to the decisions log. It
    states the tier but never decides it;
  - `merge <N> [<reviewed sha>]`: runs `pr-check`, refuses if the head moved, retargets child PRs, merges with
    `--match-head-commit`; `--dry-run` prints the writes instead;
  - `release-cut`: refuses unless the environment runs the commit, creates the release branch, and drafts the PR
    body with the PRs since the last release and every migration that drops or renames. A human still merges.

## One working session per task, and the right model

- **Start each slice in a fresh session** once none of your PRs is still open. A long conversation is re-read on
  every call and is most of an agent's cost. The rules live in the repository and the work state on GitHub, so
  nothing is lost. With a PR still open or a fix round likely, carry on in the same session, unless the context
  rule below says to clear sooner.
- **Clear at 50% of your context.** Save your state first (task, branch, head, decisions, next step, in your PR's body
  or, with no PR, the area's status file; work committed and pushed), then clear at the next safe point, even with a PR open; at 80% do it now. Where you can't see your
  context use, every merged slice counts as 50%. Where you can't clear yourself, ask the coordinator (with the team
  model, your manager) in your report: `needs: clear`.
- **Choose the model by the slice's risk:** the strongest for anything in `<merge_gate.high_risk>` and for design
  work, a faster one for docs and routine fixes. Never switch mid-task.

## Spending tokens wisely

Every tool call re-sends the whole conversation, so what sits in it is the main cost. These hold for every agent,
inside or outside, with no extra instruction:
- **Review by risk.** A full review (every specialist, a red team, an adversarial pass) for anything in
  `<merge_gate.high_risk>`. For screens and reports, only the specialists the diff touches plus one adversarial pass.
  For docs, CI and tooling, green tests and one reviewer if logic changes. At most two review rounds; a third only
  when the second found a blocker.
- **Cheap models for reading.** Search and read through a fast, read-only subagent and keep its conclusion, not the
  file dumps; review specialists can run on a mid-size model. Writing code and the adversarial pass stay on the
  session's model. Once a search is delegated, don't also run it yourself.
- **Small output.** Command output fills most of a conversation (measured on one crewline project: about 70% of
  everything tools returned was shell output, 16% file reads). Pipe tests to `tail` or grep for failures, run
  `git diff --stat` before a full diff, read files by line range, prefer page text to screenshots and take
  screenshots small.
- **One run per skill per slice.** Check a fix with a targeted test, not a new review or QA run.
- **Batch local fixes** and run the affected tests before pushing. No push-fix-push.
- **Parallel work in one call.** Once a slice's contract (request and response shapes, error and permission codes) is
  fixed, dispatch the independent parts as subagents together, then integrate and review the whole diff yourself.
- **Coordinate through the PR queue and the issues,** not chat messages. Message the coordinator only for a real
  conflict or a decision.

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
