---
name: setup
description: Set up the crewline team workflow in a repository so a crew of AI coding agents, including agents from other teams or Claude accounts, can work on it together. It creates the settings file, a rulebook section that tells every agent who it is, the collaboration rules, PR and issue templates, labels, and the pinned index issue. Use it when starting a multi-agent project, when another team or account is about to join, or when any other crewline skill reports that `.claude/crewline.yml` is missing.
---

# Setting up crewline in a repository

Crewline rests on five ideas. Each one fixes a failure we saw in practice:

1. **One rulebook in the repository.** Everything an agent must follow lives in the repo, not in one machine's
   private settings, so every agent on any account gets the same standard. One topic has one home, and other files
   link to it.
2. **Claims are draft PRs.** The open PR list is the live list of who does what. There's nothing to keep in sync.
3. **A risk-tiered merge gate.** Low-risk work self-merges with evidence. High-risk work goes through a coordinator
   and an independent second reviewer.
4. **Issues are the channel between teams.** Agents on different accounts can't message each other, so one issue per
   topic, labelled for who must answer and signed by who wrote it.
5. **Nobody blocks, and every team runs a watcher.** Agents state an assumption and keep building. Watchers notice
   new posts, because agents only see a comment when they look.

## Steps

The templates are in `../../templates/` relative to this skill's base directory. Show the owner each file before
writing it. Never overwrite existing content: merge into it, and ask where it
conflicts.

1. **Settings.** Copy `templates/crewline.yml` to `.claude/crewline.yml` and fill it with the owner.
   - The key values are the branches, the home team's name and the GitHub accounts its agents post from, the
     coordinator's name and session, and where each doc lives.
   - Show the owner the `merge_gate` lists; they're examples to adapt.
   - Leave `index_issue` for step 7.
2. **"Who you are" goes at the top of the rulebook** (`docs.rules`, usually `CLAUDE.md`), from
   `templates/who-you-are.md`. This is the most important step. Without it, an agent from another team that reads
   your docs takes itself for one of yours.
3. **The core docs.** For each doc the repository doesn't have yet, start from the template and fill in the
   `<...>` values:
   - `templates/contributing-core.md` plus `templates/contributing-collaboration.md` become `docs.contributing`;
   - `templates/definition-of-done.md` becomes `docs.definition_of_done`, with a heading that matches the `#section`
     part of the setting;
   - `templates/board.md` becomes `docs.board`, with a real lane for every agent the home team has now;
   - `docs.decisions` gets a title and a line saying it is append-only;
   - `docs.areas` gets one `path-prefix area` line per top-level folder;
   - `docs.status_dir` gets a `README.md`, since git can't hold an empty folder.

   If a doc exists, merge the missing parts into it.
4. **Templates:**
   - `templates/pull_request_template.md` goes to `.github/pull_request_template.md`;
   - `templates/issue-collaboration.md` goes to `.github/ISSUE_TEMPLATE/collaboration.md`.
5. **Open one PR with all of it** and merge it into `work_branch`. The index issue points at these docs, so they
   must exist first.
6. **Labels.** Only with the owner's go-ahead, since they're visible in the repository:

   ```bash
   gh label create collaboration -R <repo>
   gh label create for:everyone -R <repo> --description "Notice for every team; comment Applied when done"
   gh label create "for:<home_team>" -R <repo> --description "The home team must answer"
   ```
7. **The index issue.** Copy `templates/index-issue.md` to a scratch file outside the repository, and fill in
   `<home_team>` and today's date. Then:

   ```bash
   gh issue create -R <repo> --title "Collaboration index: start here" --label collaboration --body-file <scratch file>
   gh issue pin <N> -R <repo>
   ```

   Put `<N>` in `index_issue` in `.claude/crewline.yml`, and commit that one-line change by a small PR.
8. **The starter prompt for outside agents** is `templates/starter-prompt.md`. Give it to the owner; every outside
   agent's first message is this prompt, with its team name filled in.
9. **Start the home team's watcher:** a session inside a clone, running `/loop /crewline:watcher <home_team>`.

## Branch protection

If your GitHub plan allows it, protect `production_branch` and `work_branch`: require a PR, and block force pushes
and deletion. On plans where private repositories can't be protected, the rules hold by agreement. The
coordinator's weekly direct-push check is then the safety net.
