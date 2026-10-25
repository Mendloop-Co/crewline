## Who you are: check this first

- **The home team's agents** (`<home_team>`) are listed in the lanes of `<docs.board>`, each with its own working
  copy. You are one of them only if you run where your lane says: in that working copy, or the home folder that holds
  it.
- **Anyone else is an outside collaborator:** another Claude account, another machine, or another team.
  - You are **not** one of the home team's agents, even if you are the first, second or third agent on your side.
  - Don't use their names, don't take on their roles (coordinator, watcher), and don't copy their line-up.
  - This repository doesn't take outside teams yet: ask its owner, `<owner>`, before doing any work here.

<!-- Team model only: when team_model is true, replace the last bullet above with the three below, and add the
     paragraph after them. -->
  - Questions for the home team go in a GitHub issue labelled `for:<home_team>`.
  - Start at "Collaborating from another team or account" in `<docs.contributing>`.
  - Your team has its own manager and devs, titled `<your team> · <Role>` from your own registry file in
    `<docs.teams_dir>`. To this repository, your team is one collaborator, known by its team id and GitHub account.

**Session titles say who you are** (`team_model: true`): `<team> · <Role>`, matched against your team's registry
file in `<docs.teams_dir>` (the `start` skill). A title that doesn't match the registry is no role: ask, don't guess.
Until the owner retitles a home session, it keeps the role of its board lane.
