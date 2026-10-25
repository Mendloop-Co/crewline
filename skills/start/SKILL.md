---
name: start
description: Take a fresh session from "go read project" to its working role: in a small crew, from the rules and its lane on the board; with the team model, from its `<team> · <Role>` title, the registry, the GitHub account and the clone, reporting ready to its manager. Use it whenever such a session is told "go read project", "start" or "restart", or wakes after a cleared chat. Use it even if you're only told "you're new here" or "get going".
---

# Starting a session

Read `.claude/crewline.yml` first; `{…}` below are its values. This skill is only the order of steps; the rules are
in `{docs.rules}` and `{docs.contributing}` (with the team model, also `{docs.teams}` and the role files under
`{docs.roles_dir}`). If they disagree, those files win.

A chat that runs in a home folder outside its clone doesn't load the clone's files by itself: read this skill, the
rulebook and the role file by path from the clone the home folder's `CLAUDE.md` names.

**A small crew** (`team_model` false or unset) has no titles or registry. There, "go read project" means: pull
`{work_branch}` in your working copy; read `{docs.rules}`, `{docs.contributing}` and `{docs.definition_of_done}`; find
your lane on `{docs.board}`; then take your first item with the `slice` skill (the coordinator runs
`coordinator-round` instead). A session with no lane there is from another team: it follows "Collaborating from
another team or account" in `{docs.contributing}` instead, and asks in a `for:{home_team}` issue when unsure. The steps below are for the team
model.

## Steps

1. **Who am I?** Read your session title and parse `<team> · <Role>` (space, `·` U+00B7, space; anything after a
   second ` · ` is a note).
   - `git fetch origin` in your clone, then find your exact title in the registry as it is on the work branch:
     `git show origin/{work_branch}:{docs.teams_dir}<team>.md`, Sessions table. (Your checkout may predate your
     row.)
   - Check `gh api user --jq .login` is one of that file's `Agent accounts`.
   - No row for you on `origin/{work_branch}`: if your team's registry PR is still open, stop and say so (the
     coordinator merges registry PRs first; `{docs.teams}`, "Starting a new team"), and wait to be restarted.
   - Otherwise, if the title doesn't parse, isn't in the file, or the login doesn't match, ask once: "I can't match
     my session to the registry: which team and role am I?" Do nothing else until it's answered. Never take a role
     from your folder, machine or model, and never retitle yourself.
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
4. **Get current** in your clone: `git fetch origin`, then with no open task `git switch {work_branch} && git pull
   --ff-only`, or on your own task branch `git merge origin/{work_branch}`.
5. **Read, by path from your clone, and no more:**
   - `{docs.rules}`;
   - your role file: `{docs.roles_dir}manager.md` for a Manager, `{docs.roles_dir}dev.md` for a `Dev<N>` or
     `Direct`. A Planner runs the `planner` skill instead; a Reviewer reads `{docs.contributing}`, "The merge
     gate".

   Then do the role file's "At start" (it never calls this skill again).
6. **Report.** Workers send "<Role> ready: setup ok, <branch> at <short sha>" to their manager (the `report` skill)
   and wait for work; a Direct or Planner session tells the owner. The manager's report is its health line, the
   last step of its role file's "At start".

## Never

- Never work past a failed check.
- Never take work during a start: work comes after "ready", from your commander only.
- No passwords, keys or tokens, in any step.
