---
name: setup
description: Set up the crewline team workflow in a repository so a crew of AI coding agents can work on it together: a small crew by default, and the full team model once other teams or Claude accounts join. It creates the settings file, a rulebook section that tells every agent who it is, the collaboration rules, PR and issue templates, labels, and the pinned index issue. Use it when starting a multi-agent project, when another team or account is about to join, or when any other crewline skill reports that `.claude/crewline.yml` is missing.
---

# Setting up crewline in a repository

The ideas behind each step, and the failure each one fixes, are in the README's "The ideas" table.

## Steps

The templates are in `../../templates/` relative to this skill's base directory. Show the owner each file before
writing it. Never overwrite existing content: merge into it, and ask where it
conflicts.

0. **Start small.** Ask the owner one question: will another team or Claude account work here now? If not, set
   `team_model: false`: a coordinator, its agents and the board, and nothing about managers, titles or registry
   files. That is the default and the quickest start; turn the team model on later ("Turning on the team model"
   below) when another team joins or the crew outgrows one coordinator. Every step below marked "team model only" is
   skipped for a small crew.
1. **Settings.** Copy `templates/crewline.yml` to `.claude/crewline.yml` and fill it with the owner.
   - The key values are the branches, the home team's name and the GitHub accounts its agents post from, the
     coordinator's name and session, and where each doc lives.
   - For the watcher: the owner's own GitHub accounts (`owner_accounts`, or `[]`). These are only logins the
     agents never post from; a login the agents share goes in `shared_accounts` only.
   - `agent_names`: how the agents sign, the coordinator's name included (e.g. `["Agent {N}", "Lead"]`).
   - `usage_stop`: the hard usage limit at which the coordinator stops the crew (for example `weekly 90%`).
   - Whether to turn on `watcher.alert_label` for live incidents.
   - Show the owner the `merge_gate` lists; they're examples to adapt.
   - Delete the `planner:` and `agents:` blocks if the crew has no planner or no agents side by side on one machine.
   - Leave `index_issue` for step 7.
2. **"Who you are" goes at the top of the rulebook** (`docs.rules`, usually `CLAUDE.md`), from
   `templates/who-you-are.md`. This is the most important step. Without it, an agent from another team that reads
   your docs takes itself for one of yours.
3. **The core docs.** For each doc the repository doesn't have yet, start from the template and fill in the
   `<...>` values:
   - `templates/contributing-core.md` plus `templates/contributing-collaboration.md` become `docs.contributing`;
   - team model only: `templates/teams.md` becomes `docs.teams`; `templates/roles/manager.md` and
     `templates/roles/dev.md` go into `docs.roles_dir`; `templates/team-registry.md` becomes
     `docs.teams_dir`/`<home_team>.md`, with a Sessions row for every agent the home team has now (an outside team
     writes its own file when it joins);
   - `templates/definition-of-done.md` becomes `docs.definition_of_done`, with a heading that matches the `#section`
     part of the setting;
   - `templates/board.md` becomes `docs.board`, with a real lane for every agent the home team has now, each with its
     folder, database and test ports picked as the `add-agent` skill's step 1 says;
   - `docs.decisions` gets a title, a line saying it is append-only, and the table header
     `Date | Decision | Notes | Source`. Source holds the owner's exact words and where they said them. PRs never edit
     it: they carry their rows in the body and the coordinator appends them;
   - `docs.areas` gets one `path-prefix area` line per top-level folder;
   - `docs.status_dir` and `docs.specs` each get a `README.md`, since git can't hold an empty folder.

   If a doc exists, merge the missing parts into it. **A small crew:** a few lines of these templates name the team
   model's files (`<docs.teams>`, `<docs.teams_dir>`); each sits in a sentence that applies only once the team model
   is on, so fill them with the names the files will have (`TEAMS.md`, `teams/`) and leave them.
4. **Templates:**
   - `templates/pull_request_template.md` goes to `.github/pull_request_template.md`;
   - `templates/issue-collaboration.md` goes to `.github/ISSUE_TEMPLATE/collaboration.md`;
   - `templates/issue-owner-task.md` goes to `.github/ISSUE_TEMPLATE/owner-task.md`.
5. **Open one PR with all of it**, `.claude/crewline.yml` included (the watcher's clone pulls it from there), and
   merge it into `work_branch`. The index issue points at these docs, so they must exist first.
6. **Labels.** Only with the owner's go-ahead, since they're visible in the repository:

   ```bash
   gh label create collaboration -R <repo>
   gh label create for:everyone -R <repo> --description "Notice for every team; comment Applied when done"
   gh label create "for:<home_team>" -R <repo> --description "The home team must answer"
   gh label create needs:owner -R <repo> --description "Waiting on the owner's own answer"
   gh label create owner:do -R <repo> --description "A step only the owner can do"
   ```

   If `watcher.alert_label` is set, create that label too: `gh label create "<alert_label>" -R <repo>
   --description "A live incident; the watcher routes it first"`.
7. **The index issue.** Copy `templates/index-issue.md` to a scratch file outside the repository, and fill in
   `<home_team>` and today's date. Then:

   ```bash
   gh issue create -R <repo> --title "Collaboration index: start here" --label collaboration --body-file <scratch file>
   gh issue pin <N> -R <repo>
   ```

   `<N>` is the number at the end of the issue URL that `gh issue create` prints. Put it in `index_issue` in
   `.claude/crewline.yml`, and commit that one-line change by a small PR.
8. **Team model only: the starter prompt for outside teams** is `templates/starter-prompt.md`. Give it to the owner: its first part goes
   to an untitled session that writes the team's registry PR; the team's manager opens only after that merges.
9. **Start the crew.**
   - **A small crew:** each starting agent's folder, database and ports were picked in step 3 (the `add-agent`
     skill's step 1) and are on its board lane in the setup PR; the owner runs `add-agent` step 2 for each, then opens
     each session, coordinator included, with its first message from `add-agent` step 4. The watcher is optional while no outside team works here; if you run it, give it a clone
     of its own and the coordinator follows it (the `watcher` skill).
   - **Team model:** give the watcher a clone of its own on `work_branch`, which nobody else edits, and record
     it in the home registry's `Watcher clone` row. The owner opens the home manager's session, titled
     `<home_team> · Manager`, and says "go read project": the manager follows the watcher (the `watcher` skill),
     opens the home team's health issue, and starts the devs.

   The watcher needs Python 3.9+ and `gh` signed in; without them it falls back to a manual tick.

## Upgrading from 0.2

Nothing is required: a 0.2 repository has no `team_model` setting, so it runs as a small crew, as before. Add the
principle and the context rule to `docs.contributing` from the template when convenient. **Outside teams that already
work here** keep working as they did under 0.2 until you turn the team model on; turn it on before the next team
joins.

## Turning on the team model

When another team or Claude account is about to join, or the crew outgrows one coordinator. Once, in one PR:
1. Set `team_model: true`, and add `docs.teams`, `docs.teams_dir` and `docs.roles_dir` to `.claude/crewline.yml`.
2. Add `templates/teams.md`, the two role files, and the home team's registry file (step 3 above), with a Sessions
   row for every agent that runs today. Keep the registry's `Agent accounts` equal to `shared_accounts`, and every
   "Signs as" covered by `agent_names`: the watcher still reads those two settings.
3. Make sure `docs.contributing` has the principle and `docs.rules` has the current "Who you are", from the
   templates.
4. After the merge, the owner retitles each running session to its registry title, and each one runs the `start`
   skill. Until it's retitled, a session that already ran keeps its role (the note in "Who you are").
5. Give the watcher its own clone if the crew had none, record it in the registry's `Watcher clone` row, and have
   the home manager follow it; the manager opens the home team's health issue (`{docs.teams}`, "Restart and
   health"). Give the owner `templates/starter-prompt.md` for any team about to join.
6. Open a `for:everyone` workflow-change notice (the `collab` skill, section 4): it names the new team model and
   asks each active outside team for its registry PR, which the coordinator merges first. Until its row is merged,
   an outside team's existing sessions keep working under the same note.

## Branch protection

If your GitHub plan allows it, protect `production_branch` and `work_branch`: require a PR, and block force pushes
and deletion. On plans where private repositories can't be protected, the rules hold by agreement. The
coordinator's weekly direct-push check is then the safety net.
