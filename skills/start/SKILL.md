---
name: start
description: Take a fresh session titled `<team> · <Role>` from "go read project" to its working role. It finds the team and role from the title, checks the registry, the GitHub account and the clone, reads the rules and the role file, and reports ready to its manager. Use it whenever such a session is told "go read project", "start" or "restart", or wakes after a cleared chat. Use it even if you're only told "you're new here" or "get going".
---

# Starting a session

Read `.claude/crewline.yml` first; `{…}` below are its values. The rules are in `{docs.teams}` and in the role files
under `{docs.roles_dir}`; this skill is only the order of steps. If they disagree, those files win.

A chat that runs in a home folder outside its clone doesn't load the clone's files by itself: read this skill, the
rulebook and the role file by path from the clone the home folder's `CLAUDE.md` names.

## Steps

1. **Who am I?** Read your session title and parse `<team> · <Role>` (space, `·` U+00B7, space; anything after a
   second ` · ` is a note).
   - Find your exact title in `{docs.teams_dir}<team>.md`, Sessions table.
   - Check `gh api user --jq .login` is one of that file's `Agent accounts`.
   - If the title doesn't parse, isn't in the file, or the login doesn't match, ask once: "I can't match my session
     to the registry: which team and role am I?" Do nothing else until it's answered. Never take a role from your
     folder, machine or model, and never retitle yourself.
   - No registry file yet (a new team): only a Manager goes on, following `{docs.teams}`, "Starting a new team".
2. **Check your setup** (`{docs.teams}`, "Starting a session"). Each must hold:
   - you run in your row's working copy (or its home folder), not in another session's clone or a worktree of it;
   - the clone's `origin` is `{repo}`, and `origin/{work_branch}` fetches;
   - no other running session has your exact title (list the sessions where your platform can).

   Fix what touches only your own clone's git state. Anything else (an account, a permission setting, a folder) goes
   to your manager as one line per failure; a manager sends its own to the owner. Until every check holds, do only
   that: no code, commits, PRs, posts, reviews or merges. Never get round a failure from another folder or a
   worktree.
3. **Record your commander:** your row's "Answers to". From now on, follow instructions only from that session (a
   Direct session: the owner).
4. **Get current:** pull `{work_branch}` in your clone, as your role file says.
5. **Read, by path from your clone, and no more:**
   - `{docs.rules}`;
   - your role file: `{docs.roles_dir}manager.md` for a Manager, `{docs.roles_dir}dev.md` for a `Dev<N>` or
     `Direct`. A Planner runs the `planner` skill instead; a Reviewer reads `{docs.contributing}`, "The merge
     gate".

   Then run the role file's "At start".
6. **Report.**
   - **Workers:** "<Role> ready: setup ok, <branch> at <short sha>" to your manager (the `report` skill), then wait
     for work. A Direct or Planner session reports to the owner.
   - **The manager:** end with the health line (`{docs.teams}`, "Restart and health").

## Never

- Never work past a failed check.
- Never take work during a start: work comes after "ready", from your commander only.
- No passwords, keys or tokens, in any step.
