# Team <team id>

<!--
One file per team, at <docs.teams_dir><team id>.md, kept by the team's manager through a PR (a team without write
access asks the coordinator in an issue). It never holds secrets, tokens, passwords or personal data: accounts are
handles, and e-mail addresses are role accounts only. The rules it fills in are in <docs.teams>.
-->

| Field | Value |
|---|---|
| Display name | <what the team does; unique> |
| Team id | `<id>` (unique, never reused; this file's name) |
| Label | `for:<id>` |
| Since | <date>, announced in #<New team notice> |
| Works on | <the scope agreed with the coordinator, with the issue> |
| Machine | <name>, <OS and version> |
| Agent accounts | <GitHub handles the team's agents post from; their signed posts are never routed back to the team> |
| People | <the team's humans' handles, or —; their word is the lead's, never the owner's> |
| Former accounts | <retired handles, or —; never reused> |
| Plan | <the AI plan the team runs on; the manager sizes the work to it> |
| Usage stop | <the hard stop the account's owner set (the limit, who stops what, how it restarts), or "none"> |
| Health issue | #<N> (`[notice] Team <id>: health`) |
| Watcher clone | <path of the watcher's own clean clone, or "none"> |

## Sessions

| Title | Role | Model, effort | Answers to | Working copy | Home folder | Signs as |
|---|---|---|---|---|---|---|
| `<id> · Manager` | Manager | <strongest model, high effort> | <the owner, or the coordinator through issues> | <path> | <path, or —> | `<name>` |
| `<id> · Dev1` | Dev | by risk | `<id> · Manager` | <path> | <path, or —> | `<name>` |

## Machine notes

<How many full test suites run at once, how many sessions, ports or databases per agent, anything the manager needs
to pace the team on this machine.>
