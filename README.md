# crewline

**Run a crew of AI coding agents on one repository like a real team**, including agents from other teams or other
Claude accounts.

A single agent can handle a task. Several agents on one codebase need what a human team needs: someone to say who
does what, a way to stop two people doing the same work, a review gate sized by risk, and one place to talk across
teams. crewline is that workflow, packaged as Claude Code skills. It came out of building
[Mendloop](https://github.com/Mendloop-Co), built by a crew of up to seven agents plus outside teams.

## The ideas

| Idea | The failure it fixes |
|---|---|
| **Goals and hard limits, not recipes.** Agents judge the real risk inside a short list of hard limits, and ask the owner only for cost, access, real data, legal, outward-facing and irreversible steps, and product calls. A "can't" always comes with the part that can be done. | Rulebooks that grow a rule per incident until agents follow the letter and miss the goal, or stop dead at the first limit. |
| **One rulebook in the repository.** Everything an agent must follow lives in the repo; one topic, one home. | Rules in one machine's private settings; agents on another account follow a different standard without knowing it. |
| **"Who you are" comes first, from the session title.** A session is `<team> · <Role>`, matched against its team's registry file; a title that doesn't match is no role. | Outside agents read your docs and take themselves for one of your agents; a session guesses its role from its folder. |
| **Every team is a manager and its devs.** One manager per team takes the work, assigns it, reads GitHub for the team and answers for it; devs build and report. The owner's word to a dev goes through its manager, except "stop". | Several agents taking instructions from anyone who writes to them, and the plan living in five chats. |
| **Workers report in six lines.** A dev's chat stays almost empty: a key-value report to its manager, then one closing line. | Long recaps that every later turn re-reads, and a manager reading prose to find the PR number. |
| **Context and usage are measured.** A worker saves its state and clears at 50% of its context; each team paces its weekly budget by its burn rate and has a hard stop. | A chat that compacts itself mid-task, and a crew that runs out of usage on a Tuesday. |
| **Claims are draft PRs.** The open PR list is the live list of who does what. | Two agents building the same thing; a board nobody keeps up to date. |
| **A risk-tiered merge gate.** Docs and chores self-merge with evidence. Auth, money, personal data, tenancy and migrations go through a coordinator plus an independent second reviewer. | Everything waits on one reviewer, or risky changes slip through as "small". |
| **GitHub issues between teams.** One issue per topic, labelled for who must answer, every post signed. | Sessions on different accounts can't message each other, and one giant thread nobody can follow. |
| **Nobody blocks.** State your assumption, build on it, list it in the PR. | Agents idling for hours waiting for an answer. |
| **Every team runs a watcher.** It acknowledges new issues and routes them, and never answers. | Agents only see a comment when they look, and sessions stop between tasks. |
| **Ideas become plans before code.** An optional planner takes the owner's ideas, asks only what the owner alone can answer, and hands the coordinator an approved spec. | Half-formed ideas reach builders straight from chat, and the owner's "yes" exists only in someone's memory. |
| **Workflow changes are announced.** A `for:everyone` notice, which every team acknowledges with "Applied". | A rule changes, and half the crew keeps working to the old one. |
| **A relay is not approval, and posts are signed by form.** A decision is the owner's own words, copied exactly with where they said them. A post is signed on its first or last line, not by mention. | A coordinator's "the owner said yes" stands in for the owner. An unsigned comment from a shared account is taken for the owner's. |
| **The owner runs one wizard, and owner tasks sweep everything.** Anything waiting on the owner is a `needs:owner` issue; a "don't forget" task lists every pending item with its steps. | The owner pastes a list of commands, and forgets what else was waiting. |
| **A script for the mechanical, an agent for judgement.** crewline ships the watcher script, and the contributing guide lists the small scripts worth writing for your repo: queue, PR checks, merge, release cut, signed posts. | Hand-run steps that cost tokens every time and slip every time: a PR closed for good, a stale body write-back. |
| **Fresh session per task, model by risk.** The strongest model for high-risk work, a faster one for docs. | A long chat re-read on every call; an expensive model on a docs change. |
| **Roll back first; a hotfix lane.** A release under an hour old that caused the problem is rolled back. A production fix skips a freeze with one strongest-model review. | Hours spent diagnosing while production stays broken, or a fix waiting behind a freeze. |
| **Shared machine, no shared state.** No `git stash`, a test database per worktree, never another agent's server. | A stash pop that applies someone else's changes; two suites on one database. |

## Install

In Claude Code:

```text
/plugin marketplace add Mendloop-Co/crewline
/plugin install crewline@crewline
```

Then, in your repository:

```text
/crewline:setup
```

Setup walks you through the settings file (`.claude/crewline.yml`) and adds the pieces your repository lacks: the
rulebook's "Who you are" section, the collaboration rules, the team model (roles, the registry file, role files), PR
and issue templates, labels, and a pinned index issue.
It shows you each file before writing it.

## The skills

| Skill | Who uses it | What it does |
|---|---|---|
| `crewline:setup` | the owner, once | puts the workflow into a repository |
| `crewline:start` | every session titled `<team> · <Role>` | from "go read project" to ready: the role from the title and the registry, the account and clone checked, the rules and role file read, "ready" reported to the manager |
| `crewline:report` | every dev and reviewer | the six-line report to the manager, and an almost empty chat |
| `crewline:slice` | every agent | starts a slice (claim with a draft PR) and finishes it (definition of done by risk, then the merge gate) |
| `crewline:collab` | every agent | the reading routine; asking, answering and closing; announcing a change or freeze; a team joining |
| `crewline:watcher` | each team's manager | a bundled script polls GitHub and wakes the manager only when something arrived, to acknowledge and route it; a manual tick where the script can't run |
| `crewline:coordinator-round` | the coordinator | one review round: usage and idle agents, cross-team issues, the PR queue by risk, decisions, notices |
| `crewline:planner` | one planner agent, optional | the owner's business ideas become plans: what exists, the owner's questions, a spec PR to the coordinator once the owner says yes |
| `crewline:add-agent` | the owner and coordinator | adds an agent to the home crew with its own working copy, database and ports |

Every skill reads your settings file, so the skills themselves contain no project names.

## Honest limits

- **Agents don't wake up by themselves.** The watcher covers the gap, but an outside team's reply still waits until
  one of its sessions runs.
- **The watcher script needs Python 3.9+ and `gh`** on the watcher's machine, and a clone of its own. Without them
  the watcher falls back to a manual tick, which costs a model turn every time. Each pass reads one page (100) of
  each list, so a bigger burst inside one minute can be missed.
- **Rules hold by agreement** unless your GitHub plan lets you protect branches. The coordinator's weekly direct-push
  check is the safety net.
- **The coordinator is a single point of failure.** Outside teams can keep working if it stops, but nothing merges.
- **Clearing a chat may need a person.** Where an agent can't clear its own conversation or see its context use, it
  saves its state and asks for a clear, and every merged slice counts as the 50% mark; the owner or a session tool
  does the clear. The rules live in the repo, so nothing is lost.
- **Two lists of accounts until 0.4.** The watcher still reads `shared_accounts` and `agent_names` from
  `crewline.yml`; the team registry's `Agent accounts` and "Signs as" must match them.

## Licence

MIT. See [LICENSE](LICENSE).
