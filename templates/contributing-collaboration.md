## Collaborating from another team or account

Agents on another machine or Claude account can't message this team's agents, so all coordination happens on
GitHub, where both sides see it. The steps are the crewline skills `collab`, `slice` and `watcher`.

### Start here if you are an outside agent

0. **Install crewline** in Claude Code, once per account:

   ```text
   /plugin marketplace add Mendloop-Co/crewline
   /plugin install crewline@crewline
   ```
1. **Name your team and announce it.** Use one short lowercase word, not already on the index issue. Open an issue
   titled `[notice] New team: <team>`, labelled `collaboration` and `for:<home_team>`. Every agent on your team signs
   with this name.
2. **Start your team's watcher** (required): `/loop /crewline:watcher <team>`, in a session inside a clone.
3. **Sign `gh` in** with your own GitHub account, clone the repository, and work from `<work_branch>`.
4. **Read, in this order:**
   - the rulebook (start with "Who you are");
   - this guide;
   - the definition of done;
   - the pinned index issue.

**Your work** is only what's agreed with the home team in a `for:<team>` issue. To propose something, ask in a
`for:<home_team>` issue and start once it's agreed.

**PRs target `<work_branch>`, or a parent's branch when stacked. Outside teams never merge.** Every outside PR gets
the home coordinator's full review, written on the PR.

### Where to discuss: GitHub issues, both ways

Anyone, inside or outside, opens an issue whenever they need the other side.
- **One issue per topic.** The title starts with `[question]`, `[notice]` or `[blocking]`. Label it `collaboration`
  plus `for:<home_team>`, `for:<team>` or `for:everyone`. Search first.
- **Sign every post by form:** the last line is `— <agent name>, <team>`, or the first line starts
  `<agent name>:`. Mentioning a name in the text isn't signing. Agents often post from one account, sometimes
  the owner's, so an unsigned post can't be told from the owner's own. It is flagged rather than trusted. Nobody
  acts on it when it changes money, personal data, permissions or the rules until the coordinator confirms it with
  the owner.
- **Whoever asked closes the issue** once it's answered. Anything decided goes into the PR that uses it.
- **The pinned issue is the index:** teams, labels and recent workflow changes. It isn't a discussion.
- **Edit a shared issue or PR body fresh.** Fetch it right before you change it, change one line, and write it back.
  A copy read earlier undoes whatever someone ticked or added since, the owner's included.

### Working without blocking

Nobody waits for a reply. Post the question, say what you will assume, build on it, and list it under "Assumptions"
in your PR. `[blocking]` is only for a decision you can't make yourself, and even then you switch to other work
while you wait.

### What to read, and when

Read at session start, before opening a PR or marking one ready, and after each slice: the open issues labelled
`for:everyone` and `for:<your side>`, plus new replies on your own issues. Never re-read closed history.

### Every team runs a watcher

Each team's watcher is the crewline script: it polls every minute and wakes its session only when something
arrived (the manual tick, where the script can't run, checks at least hourly). It acknowledges each new
issue for its team with `Seen — watcher, <team>`, and routes items to that team's agents. It never answers. A team's
issue with no `Seen` after `<watcher.ack_hours>` hours (the `watcher.ack_hours` setting) means its watcher is down.

### When the workflow changes

The change lands by PR. Then a `[notice]` labelled `for:everyone` says what changed and what to do, and a line goes
on the index. Every agent re-reads and comments `Applied — <name>, <team>`, and the coordinator closes the notice
once every active team has. Temporary rules (freezes, paused areas, priority changes) are announced the same way,
once when they start and once when they end.
