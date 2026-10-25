---
name: slice
description: Start and finish one slice of work in a repository run by a crew of AI agents. Start means claiming it with a draft PR from the work branch before building. Finish means meeting the team's definition of done, sized by risk, and handing the PR to the merge gate. Use it when beginning any feature, fix, docs or tooling change, and again before marking a PR ready. Use it even if you're only told "start on X", "open the PR", "is this done?", "ship it" or "next task".
---

# One slice, start to finish

Read `.claude/crewline.yml` first; `{…}` below are its values. The rules and their reasons live in
`{docs.contributing}` and `{docs.definition_of_done}`. This skill is the order of steps; if they disagree, the docs
win.

## Start

1. **Know who you are and where your work comes from** (the "Who you are" section of `{docs.rules}`; a session that
   hasn't yet runs the `start` skill first):
   - **A Dev:** only the task your manager gave you. Your manager reads GitHub for the team and tells you what
     changes your work.
   - **A manager, or a crew without managers:** on the home team, the next item on `{docs.board}`, else the next
     unclaimed bug fix or specified slice; on an outside team, only a task agreed in a `for:<team>` issue. Run the
     reading routine of the `collab` skill first: an open `for:everyone` notice may change how you work or freeze an
     area. (A `queue` helper can list your next items: `{docs.contributing}`, "Scripts for the mechanical steps".)
2. **Something new with no spec?** Write the plan first and get it approved, then build.
3. **Check for an overlapping claim.** Open PRs are the live list of who does what:
   `gh pr list -R {repo} --state open --search "<area or file words>"`. If a draft already covers it, don't start:
   - a Dev tells its manager;
   - a home team's manager asks the coordinator;
   - an outside team's manager asks in a `for:{home_team}` issue.
4. **Branch from the latest work branch:**
   `git fetch origin && git switch -c <type>/<slug> origin/{work_branch}`. The type is `feat`, `fix`, `docs` or
   `chore`.
5. **Claim it now, before the work.** The draft PR is the claim:

   ```bash
   git commit --allow-empty -m "chore: claim <slice>" && git push -u origin HEAD
   gh pr create -R {repo} --draft --base {work_branch} --title "<type>(<scope>): <slice>" \
     --body-file .github/pull_request_template.md
   ```

   - **The scope** is the area from `{docs.areas}` that the slice mostly touches.
   - **If the slice came from an issue**, put `Refs #<issue>` in the PR body, and comment on the issue:
     `Claimed in #<PR>. — <signature>`. A Dev posts that comment only if its manager asked it to; otherwise its
     report names the PR, and the manager comments.

   If your project has schema migrations and the slice adds one, put its number in the title, e.g.
   `[migr <app>/<NNNN>]`, so clashes show up in the PR list. Never target `{production_branch}`, except for a
   hotfix (below).

   **A stacked PR** (built on another open PR) uses `--base <parent's branch>` instead, and says "stacked on #N"
   in its body. The coordinator retargets it to `{work_branch}` before merging the parent; then you merge
   `{work_branch}` in.

## Build

- Work only in your own working copy. Never run anything inside another agent's.
- Follow `{docs.rules}` in full.
- Batch your fixes, run the affected tests, then push once. Don't push, fix, push.
- **Sharing a machine or clone** ("Sharing one machine or clone" in `{docs.contributing}`): no `git stash`, a test
  database name of your own per worktree, and never kill a server or free a port before you know who owns it.
- Bring `{work_branch}` in with `git merge`. **Never rebase or force-push a branch that has been pushed:** others
  may have read, reviewed or built on it.

## Finish

1. **Bring the work branch in:** `git fetch origin && git merge origin/{work_branch}`. Resolve code conflicts by hand,
   then rerun the tests.
2. **Meet `{docs.definition_of_done}`**, sized by risk. Anything touching `{merge_gate.high_risk}` gets the full set
   of reviews and tests. Docs and chores get the light set.
3. **Update, in this same PR**, the spec or doc that owns any behaviour you changed, and the area's status file in
   `{docs.status_dir}`. Outside teams do this too; the coordinator reviews it with the rest. There's no separate docs
   task.
4. **Fill the PR body:**
   - areas touched (from `{docs.areas}`);
   - migrations, impact on other areas and shared contracts;
   - assumptions, tests, and DoD evidence;
   - new owner decisions as rows under `## Decisions`, with the owner's exact words and where they said them as the
     source. Never edit `{docs.decisions}` in the PR: the coordinator appends the rows after the merge. A relayed
     decision isn't the owner's word (`{docs.contributing}`, "The owner's decisions and steps"). An outside team
     lists only decisions already agreed in an issue, with the link.

   **Refer to another PR or issue as `Refs #N`**, never with a closing keyword (`{docs.contributing}`, "The path of
   a change").
5. **Before pushing more commits, check the PR is still open:** `gh pr view <N> -R {repo} --json state`. A commit
   pushed after a merge never reaches `{work_branch}`, so open a new PR instead.
6. **Mark it ready:** `gh pr ready <N> -R {repo}`. Marking it ready replaces any "ready" message.
   - **Review fixes on a PR that's already ready:** put it back to draft with `gh pr ready <N> -R {repo} --undo`
     when you start them, and mark it ready again when they're done. The PR's state is the signal; without it,
     "ready again" has nothing to change.
   - **The home team** self-merges only `{merge_gate.self_merge_ok}`. Everything else waits for the coordinator.
   - **Outside teams never merge.**
7. **After the merge:**
   - delete the branch once no open PR uses it as its base; the coordinator retargets any children first
     (`{docs.contributing}`, "The merge gate");
   - **clean up your clone:** `git fetch origin` and switch back to `{work_branch}`. Then check that
     `gh pr view <branch> -R {repo} --json state,headRefOid` says `MERGED` and that its `headRefOid` equals
     `git rev-parse <branch>`: the merge carried everything you have, for merge and squash merges alike. Only then
     remove its worktree, if it had one, with `git worktree remove` (never `rm` on a path held in a variable), and
     then delete the local branch with `git branch -D <branch>` (plain `-d` refuses after a squash merge). If the check fails, stop and
     report;
   - **a Dev** reports to its manager (the `report` skill) and waits; it doesn't pick its next item itself;
   - run the reading routine again (a Dev's manager does this for it);
   - **start the next slice with a fresh context** when `{docs.contributing}`, "One working session per task", or
     `{docs.teams}`, "Context limits", says so: save your state, then clear your chat or end your session where your
     platform lets you; otherwise ask for it in your report (`needs: clear`). Your manager (the coordinator, for a
     crew without managers) restarts you with "go read project" and your next item.

## A hotfix

A production problem that can't wait for the release: branch from `{production_branch}` and claim it with a draft PR
against it. Everything else (roll back first, the one review, who merges, the merge-back PR you open the same day,
the incident note) is in `{docs.contributing}`, "Production problems".
