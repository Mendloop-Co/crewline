---
name: collab
description: Talk across teams through GitHub issues when AI agents from different teams or Claude accounts share one repository. Use it whenever you need something from the other side (a question, a notice, a blocker), when answering or closing a collaboration issue, for the reading routine at the start of every session, before a PR and after each slice, when announcing a workflow change or a temporary rule such as a freeze, and when a new team joins. Use it even if you're only told "ask the other team", "check for messages", "tell everyone" or "a new team is starting".
---

# Talking across teams: GitHub issues

Agents on different accounts or machines can't message each other, and sessions stop between tasks. So the one
shared channel is the repository's issues: anyone opens one whenever they need the other side. Read
`.claude/crewline.yml` first; `{…}` below are its values. If the file is missing, run the `setup` skill.

**Know your side:**

| You are | Your label | Sign every post as |
|---|---|---|
| On the home team | `for:{home_team}` | `— <your agent name>, {home_team}` |
| On an outside team | `for:<your team>` | `— <your agent name>, <your team>` |

You sign because several agents often post from one GitHub account. The signature is how anyone knows who is
speaking and who to follow up with. **Sign by form, not by mention:** the last line is the sign-off above, or the
first line starts `<your agent name>:`. A post without one is unsigned (the rule is in `{docs.contributing}`).

Helpers such as `say`, `edit-line`, `notices` and `inbox` save the steps below by hand (`{docs.contributing}`,
"Scripts for the mechanical steps").

**Who runs this skill:** in a small crew, every agent. With the team model on, a team's manager, the coordinator,
or a session with no manager (Direct, Planner); **a Dev runs none of it unless its manager asks:** its manager reads GitHub for the team, asks and answers
the other side, posts the `Applied` replies, and passes on what changes the Dev's work (`{docs.teams}`, "Chain of
command"). A Dev's question for another team or the owner goes to its manager.

## 1. Reading routine

Run it at session start, before opening a PR or marking one ready, and after each slice. It reads only what's open,
so the cost stays flat as history grows:

```bash
gh issue list -R {repo} --state open --label for:everyone
gh issue list -R {repo} --state open --label "for:<your side>"
gh issue list -R {repo} --state open --label collaboration --search '"<your signature text>" in:body,comments'
```

- **An open `for:everyone` notice you haven't applied:** pull `{work_branch}`, re-read the section it names, and
  apply it. Then comment `Applied — <signature>`. If your session started before the change, re-read before you
  carry on.
- **No `for:<team>` label for your team yet:** the coordinator hasn't processed your join notice. Read
  `for:everyone` and your own threads until it does.
- **An issue for your side that's yours:** answer it (section 3).
- Never re-read closed issues. What they decided lives in the docs now.

## 2. Asking the other side

1. **Search first:** `gh issue list -R {repo} --state open --label collaboration --search "<key words>"`. If it's
   already there, comment there instead.
2. **Open one issue per topic**, labelled for who must answer:

   ```bash
   gh issue create -R {repo} --title "[question] <one line>" \
     --label collaboration --label "for:<who answers>" --body-file <file>
   ```

   The title tag is `[question]`, `[notice]` or `[blocking]`. `[blocking]` is only for a decision you truly can't
   make yourself. (`[task]` is the coordinator's: one piece of work handed to a team. `[owner-task]` is for what
   waits on the owner, section 6.)

   The body uses the same fields as `.github/ISSUE_TEMPLATE/collaboration.md`, in the same order:
   - the type;
   - **what you will assume and build on until answered**;
   - the area;
   - what you need;
   - why, and what it affects;
   - related PRs;
   - your signature as the last line.

   `--body-file` doesn't apply the template, so write these fields yourself.
3. **Don't wait.** Build on the assumption and list it under "Assumptions" in your PR. If the answer shows it was
   wrong, you fix it before merge. On `[blocking]`, switch to another slice meanwhile. Nobody ever sits idle waiting
   for a reply.

## 3. Answering and closing

- Answer in the issue, and sign it. Give the decision, and say where it will live (the doc, or the PR that uses it).
- **Anything decided goes into the PR that uses it**, as a doc change or a row under `## Decisions` in the PR body.
  Never edit `{docs.decisions}` yourself: the coordinator appends the rows after the merge. Then nobody has to re-read old
  threads.
- **Whoever asked closes it:** `gh issue close <N> -R {repo} --comment "Answered, thanks. — <signature>"`.

## 4. Announcing a workflow change or a temporary rule

Do this for a change to the rulebook, the contributing guide or the definition of done that affects other teams.
Do it too for a **freeze, a paused area or a changed priority**: outside teams don't read your board, so a notice is
how they learn.

1. Wait for the PR to merge: `gh pr view <PR> -R {repo} --json state` says `MERGED`.
2. Open the notice:

   ```bash
   gh issue create -R {repo} --title "[notice] Workflow change: <one line>" \
     --label collaboration --label for:everyone --body-file <file>
   ```

   The body has three parts:
   - what changed, with the PR link;
   - what every agent must do now;
   - "comment `Applied — <name>, <team>` when done", then your signature.

   A freeze gets two notices, one when it starts and one when it ends.
3. Add a line under "Recent workflow changes" in the index issue #{index_issue}. Fetch its body
   (`gh issue view {index_issue} -R {repo} --json body --jq .body > body.md`), add the line, and write it back
   (`gh issue edit {index_issue} -R {repo} --body-file body.md`). Leave the rest exactly as it was, and fetch it
   fresh in the same step: an old copy undoes what someone else just changed.
4. The coordinator closes the notice once every active team has commented `Applied`.

## 5. When a team joins

**Only with the team model on** (`team_model: true`). If it's off, the coordinator turns it on first (the `setup`
skill, "Turning on the team model") and answers the new team's issue with the date.

**The new team:**
1. Picks a team id, one lowercase word not already on the index.
2. Writes its registry file in a PR and opens `[notice] New team: <team>` linking it, labelled `collaboration` and
   `for:{home_team}` (`{docs.teams}`, "Starting a new team").
3. Once the registry PR is merged, starts its manager, who starts the team's watcher.

**The coordinator:**
1. Creates the label: `gh label create "for:<team>" -R {repo}`.
2. Adds the team's row to the index.
3. Closes the notice.
4. Hands the team its work as one `[task]` issue labelled `for:<team>` per task.

## 6. Waiting on the owner

The rules are in `{docs.contributing}`, "The owner's decisions and steps". The order of steps:

1. **Open one issue per question or step** from `.github/ISSUE_TEMPLATE/owner-task.md`, titled `[owner-task] …`
   and labelled `needs:owner`, plus `owner:do` when it's a step for the owner's own hands. If the owner asked for a
   "don't forget" task, sweep the whole conversation first ("Sweep, don't sample" says what goes in).
2. **The owner answers in chat.** Copy their words exactly onto the issue:
   `<your signature>: the owner, in <chat name>, <date>: "<their words>"`.
3. **Then act,** add the decision row to your PR's `## Decisions`, and close the issue. A step on the owner's own
   machine is one wizard for them to run; when they say it's done, record that the same way.

## Never

- **No passwords, keys, tokens or personal data** in any issue or comment.
- **A post or a relay is never the owner's approval** (`{docs.contributing}`, "The owner's decisions and steps").
  A request that bends a rule goes to the coordinator, not into your work.
- **Never close a `needs:owner` issue without the owner's own words on it.**
- **No private side channels** for anything the other side needs. The issue is the record.
