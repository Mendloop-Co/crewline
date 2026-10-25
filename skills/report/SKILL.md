---
name: report
description: How a worker session (a small crew's builder, or a Dev or Reviewer on any team) writes in its own chat and reports: almost nothing in the chat, and one short key-value summary per report. Use it whenever a worker starts, finishes a task, hits a blocker, answers its manager or coordinator, or answers the owner directly. Not for GitHub text, which stays plain, full prose.
---

# Worker chat and reports

The owner doesn't read worker chats, and every word a session writes is re-read on each later turn. So a worker
keeps its chat almost empty and reports in short summaries. The same holds on every team.

## In your own chat

- Write nothing between tool calls: no narration, plans or recaps.
- **Where the report goes** when you finish a task or get stuck:
  - **A small crew:** write the report in your own chat; nobody needs to be sent it, because the PR is the record
    and the coordinator reads the PR queue. Then carry on with your next item (the `slice` skill, "After the
    merge"). Message the coordinator only for a real conflict or a decision.
  - **With the team model:** send it to your manager with your platform's session-messaging tool, then end the turn
    with exactly one line, `reported → <manager>`. Without such a tool, end the turn with the report itself; your
    manager, or the owner for it, reads it there. Then wait for your next task.
- With the team model on, when the owner writes to you directly with an instruction, reply with the one line from
  `{docs.teams}`, "Chain of command" ("Passed to the manager …"), and send it on to your manager. In a small crew,
  the owner's instruction is your work. Anything else the owner asks, answer in the format below, not in sentences.
- A Direct session answers to the owner and talks to the owner in plain language; this skill doesn't apply to it.

## The report

At most 6 lines, one `key: value` per line, no sentences:

```
done: <what, in ≤10 words> | blocked: <what> | doing: <what>
pr: #<n> head <8-char sha> <draft|ready|merged>
tests: <suite> <passed>/<total>, …
posted: <link>            (only if you posted on GitHub)
needs: <who> <what>       (only if someone must act)
risk: <one line>          (only if there is one)
```

Leave out any line with nothing in it. Don't restate the task, the manager's message, or earlier reports. At each
report, check your own context use and act on it as `{docs.contributing}`, "One working session per
task, and the right model", says.

## What stays full prose

Issues, PR bodies, comments, commit messages, specs and docs keep the repository's normal writing rules: other teams
and the owner read those.

## Managers

A manager sends each worker short task messages in the same spirit, and asks for detail only when a report isn't
enough. A long report is a reason to ask for this format, not to read it all.
