An outside team starts in two steps. A titled session does no work until its registry row is merged (`<docs.teams>`,
"Starting a new team"), so the registry is written first, by a person or by an untitled first session.

**1. The registry.** Paste this into an untitled session (or follow it yourself). Fill in the `<…>` parts.

```text
You are helping outside team <team id> join <repo> (branch <work_branch>). You are NOT one of the home team's agents, and you take no role yet. If the crewline skills (e.g. /crewline:start) aren't available, ask your human to type these two lines in Claude Code first: "/plugin marketplace add Mendloop-Co/crewline", then "/plugin install crewline@crewline". Then pull the latest <work_branch>, read the rulebook ("Who you are" first), the contributing guide's collaboration section and <docs.teams>, and write <docs.teams_dir><team id>.md from the registry template with your human: the sessions and their titles (<team id> · Manager, <team id> · Dev1, …), the team's agent accounts, its machine and its limits. Send it as a PR, open "[notice] New team: <team id>" labelled collaboration and for:<home_team> linking it, signed "— <your human's name>, <team id>", and stop. You never merge.
```

**2. The manager.** Once the coordinator has merged that PR, open a session titled `<team id> · Manager` and send it
"go read project". The `start` skill takes it from there: it reads the rules and its role file, follows the team's
watcher, and starts the team's devs, each titled from the registry and started with "go read project" too. Its work
is only what is agreed with the home team in `for:<team id>` issues; its team never merges, and never touches
production, secrets or real personal data.
