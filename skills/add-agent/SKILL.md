---
name: add-agent
description: Add another agent to the home crew working on one machine. It gives the agent its own number and name, its own working copy, local database and test ports so it never clashes with another agent, a lane on the board, a model, and a first message. Use it whenever the owner wants another agent, a lane is split, or an agent needs a clean re-setup. Use it even if you're only told "add an agent", "we need another builder" or "set up agent 8". This is not for outside teams: they follow the "Start here" section of the contributing guide.
---

# Adding an agent to the home crew

Read `.claude/crewline.yml` first; `{…}` below are its values. The owner runs anything on their own machine and
opens the chat. The coordinator prepares the values and updates the board.

**Every value must be unique.** Agents that share a database or a port kill each other's servers and corrupt each
other's test runs.

## 1. Pick the values (the coordinator)

| Value | Rule | Example for agent 8 |
|---|---|---|
| Number `N` | the next unused number in the board's lanes | `8` |
| Name | how your crew names chats, including the number | `Agent 8 BUILD` |
| Working copy | a new folder in `{agents.root}`, never another agent's | `repo-8` |
| Local database | its own instance and port, e.g. `{agents.db_port_pattern}` | `54338` |
| Test ports | `{agents.api_port_pattern}` / `{agents.web_port_pattern}` | `8008` / `5181` |
| Focus | a lane that doesn't overlap an existing one | "reports and exports" |

**Check each value against the machine itself**, not only the docs, because docs lag behind:
- **the folder:** list `{agents.root}`, without going inside anyone's folder;
- **each port:** `netstat -ano | findstr :<port>` on Windows, or `lsof -i :<port>` elsewhere. Empty means free;
- **the board:** add any agent that's running but missing from it, in the same board PR as step 3.

## 2. The owner sets up the working copy (once)

```bash
git clone https://github.com/{repo}.git <agents.root>/<folder>
cd <agents.root>/<folder> && git switch {work_branch}
```

Set this copy's git identity if it isn't set globally. Install dependencies as the README says. Start the local
database on the agent's own instance and port, and always run end-to-end tests on its own ports.

## 3. The coordinator updates the board (one PR)

- **The lane:** number, working copy, focus, and what isn't theirs.
- **The database instance and test ports.**
- **A first queue of work**, so the agent never starts idle.

## 4. The owner opens the chat

Open it in the new working copy, named as in step 1. Choose the model by the risk of its first slice. The first
message:

```text
You are Agent <N> (<ROLE>) on {repo}, working only in <agents.root>/<folder> on branch {work_branch}. Your local database runs on port <db port>; your test ports are <api>/<web>. Never run anything in another agent's folder. Read {docs.rules}, {docs.contributing} and {docs.definition_of_done}, then your lane and queue on {docs.board}. Start your first item with the slice skill, and run the collab reading routine at every session start.
```

## Removing an agent

Merge or save its open work as PRs first. Then:
- the coordinator removes its lane and queue;
- the owner closes the chat;
- the owner deletes its database instance and folder, only after `git status` and
  `git log origin/{work_branch}..HEAD` are both empty.
