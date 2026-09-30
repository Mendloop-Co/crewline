---
name: slice
description: Start and finish one slice of work in a repository run by a crew of AI agents. Start means claiming it with a draft PR from the work branch before building. Finish means meeting the team's definition of done, sized by risk, and handing the PR to the merge gate. Use it when beginning any feature, fix, docs or tooling change, and again before marking a PR ready. Use it even if you're only told "start on X", "open the PR", "is this done?", "ship it" or "next task".
---

# One slice, start to finish

Read `.claude/crewline.yml` first; `{…}` below are its values. The rules and their reasons live in
`{docs.contributing}` and `{docs.definition_of_done}`. This skill is the order of steps; if they disagree, the docs
win.

## Start

1. **Know who you are and where your work comes from** (the "Who you are" section of `{docs.rules}`):
   - **The home team:** the next item on `{docs.board}`, else the next unclaimed bug fix or specified slice.
   - **An outside team:** only a task agreed in a `for:<team>` issue.

   Run the reading routine of the `collab` skill first. An open `for:everyone` notice may change how you work or
   freeze an area.
2. **Something new with no spec?** Write the plan first and get it approved, then build.
3. **Check for an overlapping claim.** Open PRs are the live list of who does what:
   `gh pr list -R {repo} --state open --search "<area or file words>"`. If a draft already covers it, don't start:
   - the home team asks the coordinator;
   - an outside team asks in a `for:{home_team}` issue.
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
     `Claimed in #<PR>. — <signature>`.

   If your project has schema migrations and the slice adds one, put its number in the title, e.g.
   `[migr <app>/<NNNN>]`, so clashes show up in the PR list. Never target `{production_branch}`.

   **A stacked PR** (built on another open PR) uses `--base <parent's branch>` instead, and says "stacked on #N"
   in its body. The coordinator retargets it to `{work_branch}` before merging the parent; then you merge
   `{work_branch}` in.

## Build

- Work only in your own working copy. Never run anything inside another agent's.
- Follow `{docs.rules}` in full.
- Batch your fixes, run the affected tests, then push once. Don't push, fix, push.
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
   - new owner decisions as lines for `{docs.decisions}`. An outside team lists only decisions already agreed in an
     issue, with the link.

   **Referring to another PR or issue:** write `Refs #N`. Never put `close`, `fix` or `resolve` (in any form)
   directly before `#N` in a commit message or the PR body unless you mean to close N. GitHub closes it as soon
   as the text lands on the default branch, even when N is someone else's open PR.
5. **Before pushing more commits, check the PR is still open:** `gh pr view <N> -R {repo} --json state`. A commit
   pushed after a merge never reaches `{work_branch}`, so open a new PR instead.
6. **Mark it ready:** `gh pr ready <N> -R {repo}`. Marking it ready replaces any "ready" message.
   - **Review fixes on a PR that's already ready:** put it back to draft with `gh pr ready <N> -R {repo} --undo`
     when you start them, and mark it ready again when they're done. The PR's state is the signal; without it,
     "ready again" has nothing to change.
   - **The home team** self-merges only `{merge_gate.self_merge_ok}`. Everything else waits for the coordinator.
   - **Outside teams never merge.**
7. **After the merge:**
   - delete the branch, but first check no other PR uses it as its base. The coordinator retargets those children
     to `{work_branch}` first, because GitHub closes a PR whose base branch is deleted;
   - run the reading routine again;
   - start the next slice.
