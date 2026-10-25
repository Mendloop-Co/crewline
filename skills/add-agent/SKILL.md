---
name: add-agent
description: Add another agent to the home crew working on one machine. It gives the agent its name (with the team model, its registry title and row), its own working copy, local database and test ports so it never clashes with another agent, a lane on the board, and a model, and its first message. Use it whenever the owner wants another agent, a lane is split, or an agent needs a clean re-setup. Use it even if you're only told "add an agent", "we need another builder" or "set up another agent". This is not for outside teams; they follow the "Start here" section of the contributing guide.
---

# Adding an agent to the home crew

Read `.claude/crewline.yml` first; `{…}` below are its values. The owner runs anything on their own machine and
opens the chat. The coordinator prepares the values and updates the board.

**Every value must be unique.** Agents that share a database or a port kill each other's servers and corrupt each
other's test runs. That includes the test-database name, so derive it from the working copy's path. And no agent
ever kills a server on a port it doesn't own: it finds the owner first.

## 1. Pick the values (the coordinator)

| Value | Rule | Example (agent 3) |
|---|---|---|
| Number `N` | the next unused number in the board's lanes | `3` |
| Name | how your crew names chats, including the number (with the team model: the title `<home_team> · <Role>`) | `Agent 3 BUILD` (`{home_team} · Dev3`) |
| Signs as | a name in `agent_names`, so the watcher knows its posts as signed; it is also the name on its board lane | `Agent 3` |
| Working copy | a new folder in `{agents.root}`, never another agent's | `repo-3` |
| Local database | its own instance and port, e.g. `{agents.db_port_pattern}` | `54333` |
| Test ports | `{agents.api_port_pattern}` / `{agents.web_port_pattern}` | `8003` / `5176` |
| Focus | a lane that doesn't overlap an existing one | "reports and exports" |

**Check each value against the machine itself**, not only the docs, because docs lag behind:
- **the folder:** list `{agents.root}`, without going inside anyone's folder;
- **each port:** `netstat -ano | findstr :<port>` on Windows, or `lsof -i :<port>` elsewhere. Empty means free;
- **the board:** add any agent that's running but missing from it, in the same board PR as step 3.

## 2. The owner sets up the working copy (once)

**The owner runs one wizard, never a list of commands to paste.** It's a short interactive script that asks for the
values from step 1 and calls one-job scripts for each step below (clone, identity, database, port check); agents
use and test those same scripts. Until you have one, the owner runs the commands below once, and an agent turns them
into the wizard afterwards. What the wizard does:

```bash
git clone https://github.com/{repo}.git {agents.root}/<folder>
cd {agents.root}/<folder> && git switch {work_branch}
```

Set this copy's git identity if it isn't set globally. Install dependencies as the README says. Start the local
database on the agent's own instance and port, and always run end-to-end tests on its own ports.

## 3. The coordinator updates the board (one PR)

- **With the team model, the registry row** in `{docs.teams_dir}{home_team}.md`, Sessions table: the title
  `{home_team} · Dev<N>` (or the role), its model, who it answers to, its working copy, and how it signs.
- **The lane** on `{docs.board}`: number, working copy, focus, and what isn't theirs.
- **The database instance and test ports**, on the lane (with the team model, also the registry's machine notes).
- **A first queue of work**, so the agent never starts idle.

## 4. The owner opens the chat

Open it only once the step-3 PR is merged, so its lane (with the team model, its registry row) is on
`{work_branch}`: without it, the agent would take itself for another team. Open it in the new working copy, named
as in step 1. Choose the model by the risk of its first slice.

**A small crew:** the first message is

```text
You are <name> on {repo}, working only in {agents.root}/<folder> on branch {work_branch}. Your local database runs on port <db port>; your test ports are <api>/<web>. Never run anything in another agent's folder, never use git stash, and never kill a server you don't own. Read {docs.rules}, {docs.contributing} and {docs.definition_of_done}, then your lane and queue on {docs.board}. Start your first item with the slice skill, and run the collab reading routine at every session start.
```

`<name>` is the name from step 1. Leave out the database and port sentence for an agent that runs neither.

**The coordinator's own first message** (a small crew):

```text
You are <coordinator name>, the coordinator on {repo}, working only in {agents.root}/<folder> on branch {work_branch}. Read {docs.rules}, {docs.contributing}, {docs.definition_of_done} and {docs.board}, then run the coordinator-round skill. Follow the watcher if this crew runs one (the watcher skill).
```

**With the team model:** the `start` skill reads the row from the work branch; the chat is titled exactly as its registry row (`{home_team} · Dev<N>`). The first message is "go read project": the
`start` skill takes it from the title to "ready", and its manager gives it its first item.

Each new slice starts in a fresh session, or after the agent clears its chat; the coordinator (with the team model,
its manager) sends the first message again with the next item.

## An agent that doesn't build

A planner (the planner skill) runs no app and no tests. It needs no local database or test ports. The
owner only opens the chat, and the agent makes its own working copy:

Its working copy is in its lane (with the team model, its registry row); if that folder doesn't exist, it clones
`https://github.com/{repo}.git` there and switches to `{work_branch}`. Its first message names its role and that
folder and says to read `{docs.rules}`, `{docs.contributing}` and its skill (with the team model: "go read project").

Before each new task it switches to `{work_branch}` and pulls, so the skills and plans it reads are current.

## Removing an agent

Merge or save its open work as PRs first. Then:
- the coordinator removes its lane and queue (and, with the team model, its registry row);
- the owner closes the chat;
- the owner deletes its database instance and folder, only after these three are all empty in that folder:
  `git status --porcelain`, `git log --branches --not --remotes --oneline` (commits on any branch that were never
  pushed), and `git worktree list` beyond its first line. Otherwise the agent pushes or saves that work first.
