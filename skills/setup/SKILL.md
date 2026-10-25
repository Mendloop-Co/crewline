---
name: setup
description: Set up the crewline team workflow in a repository so a crew of AI coding agents can work on it together: a small crew by default, and the full team model once other teams or Claude accounts join. For a small crew it creates the settings file, a rulebook section that tells every agent who it is, the contributing guide, the definition of done, the board, a PR template and two labels; turning on the team model adds the team files, the collaboration rules and the pinned index issue. Use it when starting a multi-agent project, when another team or account is about to join, or when any other crewline skill reports that `.claude/crewline.yml` is missing.
---

# Setting up crewline in a repository

The ideas behind each step, and the failure each one fixes, are in the README's "The ideas" table.

## Steps

The templates are in `../../templates/` relative to this skill's base directory. Show the owner each file before
writing it. Never overwrite existing content: merge into it, and ask where it conflicts.

**Which `<...>` to fill.** Fill only the values that name a setting or a doc: `<repo>`, `<owner>`, `<home_team>`,
`<work_branch>`, `<production_branch>`, `<coordinator.name>`, and every `<docs.…>`, `<merge_gate.…>` and
`<watcher.…>`. Leave every other `<...>` exactly as written (`<team>`, `<name>`, `<agent name>`, `<N>`, `<Role>`,
`<folder>`, …): an agent fills those in each time it uses the line. The one exception is the board's lanes and its
"Next up" items, which you fill in for the agents you start.

0. **Start small.** Ask the owner one question: will another team or Claude account work here now? Usually not:
   that is a small crew (`team_model: false`), a coordinator, its builders and the board, and you skip every step
   marked "team model only". If yes, set up the small crew first, then do "Turning on the team model" below in the
   same PR.
1. **Settings.** Copy `templates/crewline.yml` to `.claude/crewline.yml`. Ask the owner only for:
   - the repository, and the branch agents work on (`work_branch`; if it doesn't exist yet, create it from
     `production_branch`);
   - the owner's name, and the GitHub logins the agents post from. **The usual case:** the agents post from the
     owner's own login, so that login goes in `shared_accounts` and `owner_accounts` is `[]`. A login the owner keeps
     for themselves, which the agents never use, goes in `owner_accounts`;
   - the coordinator's name and its chat's name, and how the agents sign (`agent_names`, e.g.
     `["Agent {N}", "Lead"]`);
   - how many builders to start.

   Keep the defaults for everything else (doc paths, `usage_stop`, `merge_gate`, `watcher`) and show them to the owner
   as one list to change if they want. Delete the `planner:` block if there's no planner, and `agents:` if the agents
   don't run side by side on one machine.
2. **"Who you are" goes at the top of the rulebook** (`docs.rules`, usually `CLAUDE.md`), from
   `templates/who-you-are.md`, without its team-model lines. This is the most important step. Without it, an agent
   from another team that reads your docs takes itself for one of yours.
3. **The core docs.** For each doc the repository doesn't have yet, start from the template:
   - `templates/contributing-core.md` becomes `docs.contributing`;
   - `templates/definition-of-done.md` becomes `docs.definition_of_done`, with a heading that matches the `#section`
     part of the setting;
   - `templates/board.md` becomes `docs.board`, with a lane for the coordinator and one for every starting builder,
     each with its folder, database and test ports picked as the `add-agent` skill's step 1 says;
   - `docs.decisions` gets a title, a line saying it is append-only, and the table header
     `Date | Decision | Notes | Source`. Source holds the owner's exact words and where they said them. PRs never edit
     it: they carry their rows in the body and the coordinator appends them;
   - `docs.areas` gets one `path-prefix area` line per top-level folder;
   - `docs.status_dir` and `docs.specs` each get a `README.md`, since git can't hold an empty folder.

   If a doc exists, merge the missing parts into it.
4. **GitHub templates:** `templates/pull_request_template.md` goes to `.github/pull_request_template.md`, and
   `templates/issue-owner-task.md` to `.github/ISSUE_TEMPLATE/owner-task.md`.
5. **Labels**, only with the owner's go-ahead, since they're visible in the repository:

   ```bash
   gh label create needs:owner -R <repo> --description "Waiting on the owner's own answer"
   gh label create owner:do -R <repo> --description "A step only the owner can do"
   ```

   If `watcher.alert_label` is set, create that label too: `gh label create "<alert_label>" -R <repo>
   --description "A live incident; the watcher routes it first"`.
6. **Open one PR with all of it**, `.claude/crewline.yml` included, against `work_branch`. The owner merges it before
   step 7, because every agent reads these files from `work_branch`.
7. **Start the crew.** For each working copy, the coordinator's included, the owner runs the `add-agent` skill's step
   2, then opens the session with its first message from step 4. A small crew needs no watcher; run one only if the
   owner wants posts noticed between rounds (the `watcher` skill: its own clone, and the coordinator follows it).

That's the whole setup for a small crew.

## Turning on the team model

When another team or Claude account is about to join, or the crew outgrows one coordinator. Once, in one PR:
1. **Settings:** set `team_model: true`; uncomment `index_issue`, `docs.teams`, `docs.teams_dir` and
   `docs.roles_dir`; and set `coordinator.session` to `<home_team> · Manager`, the coordinator's new title.
2. **Team docs:** `templates/teams.md` becomes `docs.teams`; `templates/roles/manager.md` and
   `templates/roles/dev.md` go into `docs.roles_dir`; `templates/team-registry.md` becomes
   `<docs.teams_dir><home_team>.md`, with a Sessions row for every agent that runs today (write `pending` in the
   `Health issue` row), and is also copied unchanged to `<docs.teams_dir>_template.md`, which new teams copy. Keep the
   home registry's `Agent accounts` equal to `shared_accounts` and every "Signs as" covered by `agent_names`: the
   watcher reads those two settings.
3. **Rules for outside teams:** append `templates/contributing-collaboration.md` to `docs.contributing` (replacing an
   older collaboration section), in `docs.rules`, replace the "doesn't take outside teams yet" bullet of "Who you are" with the team-model lines of
   `templates/who-you-are.md` and add the paragraph after them, and copy
   `templates/issue-collaboration.md` to `.github/ISSUE_TEMPLATE/collaboration.md`.
4. **Labels and the index issue**, with the owner's go-ahead:

   ```bash
   gh label create collaboration -R <repo>
   gh label create for:everyone -R <repo> --description "Notice for every team; comment Applied when done"
   gh label create "for:<home_team>" -R <repo> --description "The home team must answer"
   ```

   Copy `templates/index-issue.md` to a scratch file outside the repository, fill in `<home_team>`, `<docs.teams_dir>` and today's date,
   then `gh issue create -R <repo> --title "Collaboration index: start here" --label collaboration --body-file
   <scratch file>` and `gh issue pin <N> -R <repo>`, where `<N>` is the number at the end of the URL it prints. Put
   `<N>` in `index_issue`.
5. **After the merge:** stop any watcher session started the old way (`/loop /crewline:watcher …`) first, so two
   watchers never share a side. Then the owner retitles each running session to its registry title, the coordinator
   first, and each one runs the `start` skill. The home manager follows the watcher from its own clone (record it in
   the registry's `Watcher clone` row), opens the home team's health issue, and puts its number in the `Health issue`
   row by a one-line PR.
6. **Tell everyone:** open a `for:everyone` workflow-change notice (the `collab` skill, section 4) that names the
   team model and asks each active outside team for its registry PR, which the coordinator merges first. Give the
   owner `templates/starter-prompt.md` for any team about to join.

## Upgrading from 0.2

One small PR: add "The principle" and the "Clear at 50% of your context" bullet from `templates/contributing-core.md`
to `docs.contributing`. Nothing else changes: a 0.2 repository has no `team_model` setting, so it runs as a small
crew. **Outside teams that already work here** keep working as they did under 0.2, with their own watcher routing to
their own agents; turn the team model on before the next team joins.

## Branch protection

If your GitHub plan allows it, protect `production_branch` and `work_branch`: require a PR, and block force pushes
and deletion. On plans where private repositories can't be protected, the rules hold by agreement. The
coordinator's weekly direct-push check is then the safety net.
