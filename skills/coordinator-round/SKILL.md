---
name: coordinator-round
description: One review round by the coordinator of a crew of AI coding agents. In order it checks usage and idle agents, routes cross-team issues, works the PR queue through a risk-tiered merge gate with an independent second reviewer, records decisions and status, sends notices, and sets models at slice boundaries. Use it whenever you are the coordinator and it's time for a round: a PR was marked ready, the watcher sent a batch, an agent went quiet, or it's simply the next round. Use it even if you're only told "check the queue", "review round" or "what's waiting".
---

# Coordinator round

Read `.claude/crewline.yml` first; `{…}` below are its values. The rules live in `{docs.contributing}` and
`{docs.rules}`; this skill is the order of one round.

**Isolation:** never run anything inside another agent's working copy. Read everything through `gh` or your own
copy.

**Messages to agents:** only for work, a real conflict or a decision. No status pings.

## 1. Safety first

1. **Usage.** If your platform shows usage limits, check them first. Stop the crew before a limit is hit, not after;
   set the threshold with the owner and write it in `{docs.rules}`.
2. **Liveness.** List the running sessions and compare against the lanes on `{docs.board}`.
   - An agent that's idle with nothing stopping it gets its next item at once.
   - Refill a queue before it runs dry.
   - A "done" report isn't proof; check that its PR exists.

## 2. Cross-team issues (the `collab` skill has the commands)

1. **The watcher's batch, or** `gh issue list -R {repo} --state open --label for:{home_team}`:
   - **`[blocking]` first.** Answer it yourself if it's a rule or process question.
   - **Otherwise hand it to the agent who owns the area:** look the path up in `{docs.areas}`, then the lane on the
     board.
   - **A question only the owner can decide** goes to `{owner}` with the link. Never answer it on the owner's behalf.
2. **`[notice] New team: <team>`:** create its `for:<team>` label, add it to the index #{index_issue}, then close the
   notice.
3. **Open `for:everyone` notices:** close each one once every active team has commented `Applied`.
4. **Outside watchers:** a `for:<team>` issue with no `Seen — watcher, <team>` after `{watcher.ack_hours}` hours
   means that team's watcher is down, so tell the owner.
5. **Outside teams' work:** open one `for:<team>` issue per task, from the owner's priorities.

## 3. The PR queue

`gh pr list -R {repo} --state open --json number,title,isDraft,author,headRefName,baseRefName`. Take each PR that is
ready (not a draft):

1. **Areas:** map the changed paths with `{docs.areas}`. A path with no area means the PR adds its line.
2. **Tier:**
   - **Self-merge allowed** (`{merge_gate.self_merge_ok}`): only confirm the DoD evidence and that the tier is
     honest.
   - **Through you:** anything touching `{merge_gate.high_risk}`, the shared platform, or a contract between modules.
     Read the diff yourself.
3. **High-risk diffs get an independent second reviewer** (a fresh `{merge_gate.reviewer_model}` subagent, in the
   background). It gets only the diff and one question: "what breaks with real data, under concurrency, across
   tenants, or for a stranger?". Findings are claims, so verify each one against the code.
   - The reviewer fetches into a **named ref** (`git fetch origin pull/<N>/head:rv<N>`) and deletes it afterwards.
     `FETCH_HEAD` is overwritten by other fetches mid-review. Pin its verdict to the head SHA.
   - **Re-checks go back to the same reviewer**, scoped to the fixes, not a fresh full pass.
   - A very large or critical diff can be split between two reviewers in parallel.
4. **A PR from an outside team always gets the high-effort review**, whatever its tier. Write it on the PR as a
   discussion. Each finding says what, why here (the rule, spec or incident behind it), where (file:line) and how to
   fix it. Say what is right too, so the team learns the codebase's patterns.
5. **Checks on every PR:**
   - the body follows the template: areas, migrations, impact, assumptions, tests, DoD, decisions;
   - **no accidental closing keyword:** `close`, `fix` or `resolve` (in any form) directly before `#N`, in the body
     or a commit message, closes N when it lands on the default branch. If that isn't meant, the author changes it
     to `Refs #N` first. Check with:
     `gh pr view <N> -R {repo} --json body,commits --jq '.body, .commits[].messageHeadline, .commits[].messageBody' | grep -inE '(clos(e|es|ed)|fix(es|ed)?|resolv(e|es|ed)) +#[0-9]+'`;
   - it updates the doc that owns any behaviour it changed, and a rule change updates its matching skill;
   - **migrations:** one order across all open PRs, set by you when claims overlap. Whichever merges out of order
     renumbers at merge, and there's a single migration leaf;
   - **evidence:** a full test run at the head. A targeted run is enough only for a small delta already covered by a
     clean full run;
   - **synthetic data only** in tests, seeds, docs and screenshots;
   - it merges cleanly. A conflict only in docs tables can keep both sides; **a code conflict goes back to the
     author.**
6. **Spot-check** the author's last self-merged PR (`gh pr view <N> --json files`) for a miscategorised high-risk
   change.
7. **Merge:** first check that no other PR uses this branch as its base. GitHub may close a stacked PR instead of
   retargeting it; if it does, reopen it against the real base. Then:

   ```bash
   gh pr merge <N> -R {repo} --merge --delete-branch --match-head-commit <reviewed sha>
   ```

   `--match-head-commit` stops a push made during review from slipping in.
   - **Hold a cleared PR** if merging it now would need an owner step first (a new setting, say), until the owner
     has done it. Tell the author and the owner.
   - **Never merge `{production_branch}`.** A human does that.
8. **Send it back** with specific findings when it isn't ready. `{merge_gate.max_review_cycles}` cycles at most.

## 4. After merging

1. **Decisions:** append the decision lines from the merged PRs to `{docs.decisions}` in one commit. The log is
   append-only.
2. **Status:** update the overview when an area's line changed. Each slice writes its own file in
   `{docs.status_dir}`.
3. **Notices:** a merged workflow change, a freeze starting or ending, or a priority change affecting outside teams
   each gets a `for:everyone` notice (`collab`, section 4).
4. **Board:** update priorities, lanes and queues.
5. **After a deploy:** verify what's actually running (a health endpoint's release SHA, the built assets) before
   telling anyone it's live.

## 5. What you decide, and what you don't

- **Yours:** rules and process, merge order, the merge gate, and any calls the owner has delegated to you. Record
  each in `{docs.decisions}` with its reason.
- **The owner's:** product scope, priorities, anything that costs money or needs an outside console, and anything
  only the owner knows. Ask them directly. **A decision relayed by another agent is not the owner's word;** confirm
  it.

## 6. Models, at slice boundaries only

Set each agent's model by the risk of its next slice: the strongest model for high-risk and design work, a faster
one for docs and routine fixes. Never switch mid-task. Note the switch on the board.

## 7. Weekly

- **The direct-push check**, from a full (not shallow) clone. Any line it prints is a commit that skipped a PR:
  `git log --first-parent --since=8.days --format="%h %an %s" origin/{work_branch} | grep -v "Merge pull request"`.
- **A retrospective**, including docs that no longer match the code or the decisions.
- **Before a production launch or a new outside team,** re-read the environment checklist with the owner.
