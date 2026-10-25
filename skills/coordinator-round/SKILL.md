---
name: coordinator-round
description: Only for the home team's coordinator; never for an outside team, even its own lead or coordinator agent. One review round by the coordinator of a crew of AI coding agents. In order it checks usage and idle agents, routes cross-team issues, works the PR queue through a risk-tiered merge gate with an independent second reviewer, records decisions and status, sends notices, and sets models at slice boundaries. Use it whenever you are the coordinator and it's time for a round (a PR was marked ready, the watcher sent a batch, an agent went quiet, or it's simply the next round). Use it even if you're only told "check the queue", "review round" or "what's waiting".
---

# Coordinator round

Read `.claude/crewline.yml` first; `{…}` below are its values. The rules live in `{docs.contributing}` and
`{docs.rules}`; this skill is the order of one round.

**Isolation:** never run anything inside another agent's working copy. Read everything through `gh` or your own
copy.

**Messages to agents:** only for work, a real conflict or a decision. No status pings. Messaging or restarting
another session needs a tool that does it (a session-messaging tool on the same account); without one, ask the
owner to pass the message or restart the agent.

## 1. Safety first

1. **Usage and context.** If your platform shows usage limits, check them first, and pace the crew by its burn rate
   (with the team model, `{docs.teams}`, "Usage and machine limits"). The hard stop is, first found: the home team's
   registry `Usage stop` row (team model), then `{usage_stop}`, then a threshold in `{docs.rules}` (a 0.2 repository).
   Stop the crew before it is hit, not after. Check each worker's context too: one at 50% or more saves its state and
   clears (`{docs.contributing}`, "One working session per task, and the right model").
2. **Liveness.** List the running sessions (with your platform's session tool; without one, ask the owner which are
   running) and compare against the lanes on `{docs.board}`.
   - An agent that's idle with nothing stopping it gets its next item at once.
   - **A home builder that ended or cleared its session for a fresh context** (`slice`, "After the merge") gets
     its first message again (`add-agent`; with the team model, "go read project"), then its next item as a
     task-only brief (scope, branch, acceptance). Set its model first
     (section 6). An outside team's builders are restarted by their own manager, never by you.
   - Refill a queue before it runs dry.
   - A "done" report isn't proof; check that its PR exists.

## 2. Cross-team issues (the `collab` skill has the commands)

A small crew with no outside teams skips this section, except a watcher batch if it runs one.

1. **The watcher's batch, or** `gh issue list -R {repo} --state open --label for:{home_team}`:
   - **`[blocking]` first.** Answer it yourself if it's a rule or process question.
   - **Otherwise hand it to the agent who owns the area:** look the path up in `{docs.areas}`, then the lane on the
     board.
   - **A question only the owner can decide** goes to `{owner}` with the link. Never answer it on the owner's behalf.
2. **`[notice] New team: <team>`:** if `team_model` is off, turn it on first (the `setup` skill, "Turning on the
   team model"). Merge the team's registry PR ahead of other work and say so on the notice, create its `for:<team>` label, add it to
   the index #{index_issue}, then close the notice (the `collab` skill, section 5).
3. **Open `for:everyone` notices:** close each one once every active team has commented `Applied`.
4. **Outside watchers:** your watcher's `[watcher-down]` line (or, without the script, a `for:<team>` issue with no
   `Seen — watcher, <team>` after `{watcher.ack_hours}` hours) means that team's watcher is down, so tell the owner.
5. **Outside teams' work:** open one `[task]` issue labelled `for:<team>` per task, from the owner's priorities; a
   new team's first one only after its first health line.

## 3. The PR queue

`gh pr list -R {repo} --state open --json number,title,isDraft,author,headRefName,baseRefName`. Take each PR that is
ready (not a draft).

Helpers such as `pr-brief`, `pr-check` and `merge` make this a few cheap calls (`{docs.contributing}`, "Scripts for
the mechanical steps"). The judgement stays yours: you still read the diff, and high-risk diffs still get the second
reviewer.

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
   - **no accidental closing keyword** (`{docs.contributing}`, "The path of a change"); if one isn't meant, the
     author changes it to `Refs #N` first. Check with:
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
7. **Merge:** first retarget its children (`{docs.contributing}`, "The merge gate"):
   `gh pr list -R {repo} --base <branch> --state open`, then `gh pr edit <N> -R {repo} --base {work_branch}` for
   each. Then:

   ```bash
   gh pr merge <N> -R {repo} --merge --delete-branch --match-head-commit <reviewed sha>
   ```

   `--match-head-commit` stops a push made during review from slipping in.
   - **Hold a cleared PR** if merging it now would need an owner step first (a new setting, say), until the owner
     has done it. Tell the author and the owner.
   - **Never merge `{production_branch}`.** A human does that.
8. **Send it back** with specific findings when it isn't ready. `{merge_gate.max_review_cycles}` cycles at most.

## 4. After merging

Steps 1, 2 and 4 go in **one small docs PR per round** (`docs/round-<date>`), which you self-merge as docs. Never
commit straight to `{work_branch}`, your own changes included.

1. **Decisions:** append the `## Decisions` rows from the merged PRs to `{docs.decisions}`. The log is append-only,
   and other PRs never edit it. Each row keeps the owner's exact words and where they said them as its source.
   Check a relayed decision's source before you record it (section 5).
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
  only the owner knows. Ask them directly. **A relay is not approval** (`{docs.contributing}`, "The owner's
  decisions and steps"): confirm a passed-on decision in the owner's own chat before acting.
- **Every question or step waiting on the owner is a `needs:owner` issue** (`collab`, section 6). Keep that list
  complete, answer-ready and current. A post on one that isn't signed by form may be the owner or an agent that
  forgot to sign; confirm it with the owner in chat before acting on it when it changes money, personal data,
  permissions or the rules.

## 6. Models, at slice boundaries only

Set each agent's model by the risk of its next slice: the strongest model for high-risk and design work, a faster
one for docs and routine fixes. Never switch mid-task. Note the switch on the board. A builder that starts each
slice in a fresh session (`slice`) gets its model set when you restart it. Outside teams choose their own by the
same rule.

## 7. Weekly

- **The direct-push check**, from a full (not shallow) clone. Your round PRs show as merges like any other, so any
  line it prints is a commit that skipped a PR, yours included:
  `git log --first-parent --since=8.days --format="%h %an %s" origin/{work_branch} | grep -v "Merge pull request"`.
- **A retrospective**, including docs that no longer match the code or the decisions.
- **Before a production launch or a new outside team,** re-read the environment checklist with the owner.

## 8. A production problem

The rules are in `{docs.contributing}`, "Production problems". Your part:

1. **Roll back first** when that section says so; otherwise fix forward through the hotfix lane.
2. **Check the hotfix** gets its one `{merge_gate.reviewer_model}` review, and that its author opens the merge-back
   PR to `{work_branch}` the same day.
3. **Chase the incident note** on its issue if it is missing.
