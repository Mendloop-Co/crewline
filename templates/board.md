# Board

Kept by the coordinator. It holds only what is live: who works where, what comes next. The home team's agents are
listed here; **outside teams aren't lanes and never take items from "Next up"**. Their work comes from `for:<team>`
issues.

## Lanes (the home team's agents)

| Agent | Working copy | Database / test ports | Focus | Not theirs |
|---|---|---|---|---|
| <coordinator.name> | <folder> | — | coordinator: the PR queue, the merge gate, this board, the decisions log | product code |
| <agent name> | <folder> | <port> / <api>, <web> | <focus> | — |

## Next up

In order. Each item names the agent whose queue it's in; an item with no name is for whoever is free first.

- <agent name>: <the next item>
