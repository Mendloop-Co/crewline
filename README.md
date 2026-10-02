# crewline

**Run a crew of AI coding agents on one repository like a real team**, including agents from other teams or other
Claude accounts.

A single agent can handle a task. Several agents on one codebase need what a human team needs: someone to say who
does what, a way to stop two people doing the same work, a review gate sized by risk, and one place to talk across
teams. crewline is that workflow, packaged as Claude Code skills. It came out of building
[Mendloop](https://github.com/Mendloop-Co), a clinic platform built by a crew of up to seven agents plus outside teams.

## The ideas

| Idea | The failure it fixes |
|---|---|
| **One rulebook in the repository.** Everything an agent must follow lives in the repo; one topic, one home. | Rules in one machine's private settings; agents on another account follow a different standard without knowing it. |
| **"Who you are" comes first.** The home crew's agents are named; everyone else is an outside collaborator. | Outside agents read your docs and take themselves for one of your agents. |
| **Claims are draft PRs.** The open PR list is the live list of who does what. | Two agents building the same thing; a board nobody keeps up to date. |
| **A risk-tiered merge gate.** Docs and chores self-merge with evidence. Auth, money, personal data, tenancy and migrations go through a coordinator plus an independent second reviewer. | Everything waits on one reviewer, or risky changes slip through as "small". |
| **GitHub issues between teams.** One issue per topic, labelled for who must answer, every post signed. | Sessions on different accounts can't message each other, and one giant thread nobody can follow. |
| **Nobody blocks.** State your assumption, build on it, list it in the PR. | Agents idling for hours waiting for an answer. |
| **Every team runs a watcher.** It acknowledges new issues and routes them, and never answers. | Agents only see a comment when they look, and sessions stop between tasks. |
| **Ideas become plans before code.** An optional planner takes the owner's ideas, asks only what the owner alone can answer, and hands the coordinator an approved spec. | Half-formed ideas reach builders straight from chat, and the owner's "yes" exists only in someone's memory. |
| **Workflow changes are announced.** A `for:everyone` notice, which every team acknowledges with "Applied". | A rule changes, and half the crew keeps working to the old one. |

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
rulebook's "Who you are" section, the collaboration rules, PR and issue templates, labels, and a pinned index issue.
It shows you each file before writing it.

## The skills

| Skill | Who uses it | What it does |
|---|---|---|
| `crewline:setup` | the owner, once | puts the workflow into a repository |
| `crewline:slice` | every agent | starts a slice (claim with a draft PR) and finishes it (definition of done by risk, then the merge gate) |
| `crewline:collab` | every agent | the reading routine; asking, answering and closing; announcing a change or freeze; a team joining |
| `crewline:watcher` | one per team | one tick, run as `/loop /crewline:watcher <team>`: notice, acknowledge, route, pace itself |
| `crewline:coordinator-round` | the coordinator | one review round: usage and idle agents, cross-team issues, the PR queue by risk, decisions, notices |
| `crewline:planner` | one planner agent, optional | the owner's business ideas become plans: what exists, the owner's questions, a spec PR to the coordinator once the owner says yes |
| `crewline:add-agent` | the owner and coordinator | adds an agent to the home crew with its own working copy, database and ports |

Every skill reads your settings file, so the skills themselves contain no project names.

## Honest limits

- **Agents don't wake up by themselves.** The watcher covers the gap, but an outside team's reply still waits until
  one of its sessions runs.
- **Rules hold by agreement** unless your GitHub plan lets you protect branches. The coordinator's weekly direct-push
  check is the safety net.
- **The coordinator is a single point of failure.** Outside teams can keep working if it stops, but nothing merges.
- **One agent can't reset its own long conversation.** Start a fresh session for each new slice; the rules live in
  the repo, so nothing is lost.

## Licence

MIT. See [LICENSE](LICENSE).
