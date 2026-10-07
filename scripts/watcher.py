"""crewline's GitHub watcher as a script: notice and route, never answer.

    python3 watcher.py                    # the home team's watcher: poll, one line per new item
    python3 watcher.py --side <team>      # an outside team's watcher
    python3 watcher.py --once             # one pass, then exit ("nothing new" when empty)
    python3 watcher.py --once --since 2026-10-05T12:00:00Z   # look back; changes no state

Run it from a clone of the repository (or pass --repo-dir); every project setting comes from that
clone's `.claude/crewline.yml`. A watcher session runs it under its Monitor tool: stdout stays
silent until something arrives, each line is one item to route, and only then does the model wake.

Lines, most urgent first, one per item:
    [alert]          an open issue labelled `watcher.alert_label`, if set (new, or still open an
                     hour later)
    [owner]          a post by `owner_accounts`, or an unsigned `shared_accounts` comment on an
                     issue labelled one of `watcher.owner_labels`
    [blocking]       a new issue titled "[blocking] ..."
    [watcher-down]   (home) a `for:<team>` issue open `watcher.ack_hours` with no "Seen" (once)
    [review-request] (home) new commits on a ready PR, or a draft marked ready, even with no comment
    [ack]            (outside team) a new `for:<team>` issue: comment "Seen — watcher, <team>" once
    [unsigned]       (home) a `shared_accounts` comment that isn't signed (once)
    [issue] [comment] [review] [pr]   anything else new for this side
    [watcher-error]  GitHub or the settings could not be read, or the clone could not be pulled
    [watcher-updated]  this script changed on disk: it exits, and the session arms it again

Self-update, every `watcher.update_minutes`: it pulls the clone, only when the checkout is clean and
on `work_branch`, then re-reads crewline.yml (new settings apply at once, silently). If this script
file changed or vanished (a copy in the repository was pulled, or the plugin was updated), it prints
[watcher-updated] and exits. One watcher per repository and side: the newest takes over, and an
older one exits at its next pass. State lives in ~/.crewline-watcher/<owner>-<name>/<side>/, all in
lower case, outside the repository. Team names and labels compare case-insensitively. Python 3.9+,
standard library only; GitHub through the `gh` CLI and its login.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

UTC = timezone.utc  # datetime.UTC is 3.11+
OVERLAP = timedelta(seconds=30)  # each pass looks a little further back; `said` drops repeats
ALERT_AGAIN = timedelta(hours=1)
ERROR_AGAIN = timedelta(minutes=10)
UPDATE_ERROR_AGAIN = timedelta(hours=6)
GH = os.environ.get("GH") or shutil.which("gh") or "gh"
SCRIPT = Path(__file__).resolve()


# --- crewline.yml: the subset the template uses -------------------------------------------------
# Scalars, inline lists, one nesting level, comments. A `#` starts a comment only at the start of a
# line or after whitespace, so `docs/DONE.md#done` stays a value.


def _uncomment(line: str) -> str:
    quote = None
    for i, ch in enumerate(line):
        if quote:
            quote = None if ch == quote else quote
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i]
    return line


def _scalar(text: str):
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    if text in ("true", "false"):
        return text == "true"
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def _value(text: str):
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        items = re.findall(r"\s*(\"[^\"]*\"|'[^']*'|[^,]+)", text[1:-1])  # "a, b" stays one item
        return [_scalar(item) for item in items if item.strip()]
    return _scalar(text)


def read_settings(text: str) -> dict:
    data: dict = {}
    parent = None  # the top-level key whose nested keys follow
    for number, raw in enumerate(text.splitlines(), 1):
        line = _uncomment(raw).rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key, sep, rest = line.strip().partition(":")
        if not sep or not key:
            raise ValueError(f"line {number}: expected `key: value`")
        if indent == 0:
            if rest.strip():
                data[key], parent = _value(rest), None
            else:
                data[key], parent = {}, key
        elif parent is not None:
            data[parent][key] = _value(rest)
        else:
            raise ValueError(f"line {number}: indented, but not under a `key:` line")
    return data


def _list(value) -> list:
    if value in (None, "", {}):
        return []
    return [str(v) for v in value] if isinstance(value, list) else [str(value)]


class Settings:
    """What the watcher needs from crewline.yml, checked."""

    def __init__(self, data: dict):
        def need(name: str, value):
            text = str(value or "")
            if not text or "<" in text:
                raise ValueError(f"crewline.yml: fill in `{name}` (now {text or 'empty'!r})")
            return text

        watch = data.get("watcher") if isinstance(data.get("watcher"), dict) else {}
        self.repo = need("repo", data.get("repo"))
        if not re.fullmatch(r"[\w.-]+/[\w.-]+", self.repo):
            raise ValueError(f"crewline.yml: `repo` must be owner/name (now {self.repo!r})")
        self.work_branch = need("work_branch", data.get("work_branch", "develop"))
        self.home_team = need("home_team", data.get("home_team")).lower()  # "Acme" is "acme"
        self.shared = {need("shared_accounts", a) for a in _list(data.get("shared_accounts"))}
        owners = {need("owner_accounts", a) for a in _list(data.get("owner_accounts"))}
        self.both = sorted(owners & self.shared)  # a login the agents post from is never the owner
        self.owners = owners - self.shared
        self.agent_names = _list(data.get("agent_names")) or ["Agent {N}"]
        self.alert_label = str(watch.get("alert_label", "") or "")  # unset = no alerts
        owner_labels = watch.get("owner_labels", ["needs:owner", "owner:do"])
        self.owner_labels = {label.lower() for label in _list(owner_labels)}
        self.poll_seconds = max(30, int(watch.get("poll_seconds", 60)))
        self.update_minutes = max(1, int(watch.get("update_minutes", 15)))
        self.ack_hours = float(watch.get("ack_hours", 2))


def find_config(config: str | None, repo_dir: str | None) -> Path:
    if config:
        return Path(config).resolve()
    here = Path(repo_dir or os.getcwd()).resolve()
    for folder in (here, *here.parents):
        if (folder / ".claude" / "crewline.yml").exists():
            return folder / ".claude" / "crewline.yml"
    raise FileNotFoundError(
        f"no .claude/crewline.yml in {here} or above: run the watcher from a clone that has one"
    )


def load(path: Path) -> tuple[str, Settings]:
    text = path.read_text(encoding="utf-8")
    return text, Settings(read_settings(text))


# --- GitHub ----------------------------------------------------------------------------------


def iso(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(stamp: str) -> datetime:
    return datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def gh(path: str):
    out = subprocess.run(
        [GH, "api", "-H", "Accept: application/vnd.github+json", path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    if out.returncode != 0:
        err = out.stderr.strip()
        raise RuntimeError(err.splitlines()[-1] if err else "gh failed")
    return json.loads(out.stdout or "null")


# --- Signatures --------------------------------------------------------------------------------
# A post is signed by its form, not by a mention: the first line starts "<name>:" (bold allowed,
# "**Agent 2:**") or "Applied — <name>", or the last line is a sign-off ("— Agent 2, <team>").
# A first line that only mentions an agent ("Re-review by Agent 2", "Lead is away") is not signed.

DASH = "[—–-]"


def _names(names: list[str]) -> str:
    return "|".join(re.escape(n).replace(re.escape("{N}"), r"\d+") for n in names)


def _lines(body: str | None) -> list[str]:
    return [line.strip() for line in (body or "").strip().splitlines() if line.strip()]


def team_signed(body: str | None, team: str) -> bool:
    """Signed with the team's name: the first line starts "Applied — <name>, <team>" or "Seen —
    watcher, <team>", or the last line ends with the sign-off "— <name>, <team>"."""
    lines = _lines(body)
    if not lines:
        return False
    team_ = re.escape(team)
    first = re.compile(rf"^(?:Applied|Seen)\s+{DASH}\s+[^,\n]{{1,60}},\s*{team_}\b", re.IGNORECASE)
    last = re.compile(rf"(?:^|\s){DASH}+\s*[^,—–\n]{{1,60}},\s*{team_}\s*$", re.IGNORECASE)
    return bool(first.match(lines[0]) or last.search(lines[-1]))


def signed(body: str | None, names: list[str], team: str) -> bool:
    """A home agent's post: signed with an agent's name (`agent_names`) or the home team's."""
    lines = _lines(body)
    if not lines:
        return False
    who = _names(names)
    first = re.compile(rf"^(?:\*\*)?(?:{who})(?:\*\*)?:|^Applied\s+{DASH}\s+(?:{who})(?!\w)")
    last = re.compile(rf"^{DASH}+\s*(?:{who})(?!\w)")
    return bool(first.match(lines[0]) or last.match(lines[-1])) or team_signed(body, team)


ACK = re.compile(rf"^Seen\s+(?:{DASH}\s+watcher\b|by the \S+ watcher\b)", re.IGNORECASE)


def acknowledgement(body: str | None) -> bool:
    """A watcher saying it saw a post ("Seen — watcher, <team>", or the home watcher's "Seen by
    the <team> watcher; routed to ..."): nothing to route."""
    return bool(ACK.match((body or "").lstrip()))


def confirmation(body: str | None) -> bool:
    """An agent confirming a notice ("Applied — <name>, <team>")."""
    return (body or "").lstrip().startswith("Applied")


def labels_of(issue: dict) -> set[str]:
    """Lower case: team names and labels compare case-insensitively."""
    return {label["name"].lower() for label in issue.get("labels", [])}


def short(text: str | None, most: int = 90) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= most else text[: most - 1] + "…"


def blocking(issue: dict) -> bool:
    return "pull_request" not in issue and issue["title"].lstrip().lower().startswith("[blocking]")


def number_of(url: str) -> int:
    return int(url.rsplit("/", 1)[1])


# --- The two sides -----------------------------------------------------------------------------

RANK = {
    "alert": 0,
    "owner": 1,
    "blocking": 2,
    "watcher-down": 3,
    "review-request": 4,
    "unsigned": 5,
    "issue": 6,
    "comment": 7,
    "review": 8,
    "pr": 9,
}


class Watcher:
    """The home team's side: everything new from outside its own agents, owner first."""

    def __init__(self, state_dir: Path, settings: Settings):
        self.s = settings
        self.path = state_dir / "state.json"
        self.state = {
            "last_check": None,
            "said": [],
            "alerts": {},
            "down": [],
            "acked": [],
            "heads": None,  # open PR number -> [head sha, draft]; None until the first pass
        }
        if self.path.exists():
            self.state.update(json.loads(self.path.read_text(encoding="utf-8")))
        self._issues: dict[int, dict] = {}

    def save(self) -> None:
        self.state["said"] = self.state["said"][-500:]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.state, indent=1), encoding="utf-8")

    def api(self, path: str):
        return gh(f"repos/{self.s.repo}/{path}")

    def issue(self, number: int) -> dict:
        if number not in self._issues:
            self._issues[number] = self.api(f"issues/{number}")
        return self._issues[number]

    def seen(self, number: int, prefix: str = "Seen — watcher") -> bool:
        comments = self.api(f"issues/{number}/comments?per_page=100")
        return any((c.get("body") or "").lstrip().startswith(prefix) for c in comments)

    def emit(self, found: list[tuple[int, str, str]]) -> list[str]:
        """The lines in order of urgency, each keyed item said once."""
        lines = []
        for _, key, line in sorted(found, key=lambda item: item[0]):
            if key and key in self.state["said"]:
                continue
            if key:
                self.state["said"].append(key)
            lines.append(line)
        return lines

    def kind_of_issue(self, issue: dict) -> str:
        if issue["user"]["login"] in self.s.owners:
            return "owner"
        if blocking(issue):
            return "blocking"
        return "pr" if "pull_request" in issue else "issue"

    def alerts(self, now: datetime, found: list) -> None:
        if not self.s.alert_label:
            return
        label = urllib.parse.quote(self.s.alert_label)
        for issue in self.api(f"issues?labels={label}&state=open&per_page=100"):
            last = self.state["alerts"].get(str(issue["number"]))
            if last is None or now - parse(last) >= ALERT_AGAIN:
                self.state["alerts"][str(issue["number"])] = iso(now)
                found.append(
                    (
                        0,
                        "",
                        f"[alert] #{issue['number']} {short(issue['title'])} {issue['html_url']}",
                    )
                )

    def watchers_down(self, now: datetime, found: list) -> None:
        """A `for:<team>` issue (another team's) open `ack_hours` with no "Seen": that team's
        watcher may be down. Said once per issue; issues already seen aren't asked again."""
        mine = {f"for:{self.s.home_team}", "for:everyone"}
        for issue in self.api("issues?state=open&per_page=100"):
            number = issue["number"]
            teams = sorted(n for n in labels_of(issue) if n.startswith("for:") and n not in mine)
            if (
                not teams
                or "pull_request" in issue
                or number in self.state["down"]
                or number in self.state["acked"]
                or now - parse(issue["created_at"]) < timedelta(hours=self.s.ack_hours)
            ):
                continue
            if self.seen(number):
                self.state["acked"].append(number)
                continue
            self.state["down"].append(number)
            found.append(
                (
                    RANK["watcher-down"],
                    "",
                    f"[watcher-down] #{number} {', '.join(teams)}: open {self.s.ack_hours:g} h with"
                    f" no Seen, that team's watcher may be down {issue['html_url']}",
                )
            )

    def review_requests(self, found: list) -> None:
        """New commits on a ready PR, or a draft marked ready: it wants a review, even when nobody
        commented. The first pass only records what is open; a new PR is said as [pr]."""
        before = self.state["heads"]
        heads = {}
        for pr in self.api("pulls?state=open&per_page=100"):
            number, sha, draft = str(pr["number"]), pr["head"]["sha"], bool(pr.get("draft"))
            heads[number] = [sha, draft]
            if before is None or number not in before or draft:
                continue
            old_sha, was_draft = before[number]
            if sha == old_sha and not was_draft:
                continue
            why = "marked ready" if was_draft else f"new commits (head {sha[:7]})"
            found.append(
                (
                    RANK["review-request"],
                    f"h{number}-{sha}",
                    f"[review-request] #{number} by {pr['user']['login']}: {why}:"
                    f" {short(pr['title'])} {pr['html_url']}",
                )
            )
        self.state["heads"] = heads

    def once(self, now: datetime, since: datetime) -> list[str]:
        """Every item to route since `since`, most urgent first, each said once."""
        self._issues = {}
        found: list[tuple[int, str, str]] = []
        after = iso(since - OVERLAP)
        self.alerts(now, found)
        self.watchers_down(now, found)
        self.review_requests(found)
        alert = self.s.alert_label.lower()

        for issue in self.api(f"issues?since={after}&state=all&per_page=100"):
            self._issues[issue["number"]] = issue
            author = issue["user"]["login"]
            if author in self.s.shared or parse(issue["created_at"]) < since - OVERLAP:
                continue
            if alert and alert in labels_of(issue):
                continue  # said above, while it is open
            kind = self.kind_of_issue(issue)
            note = (
                ""
                if "pull_request" in issue or any(n.startswith("for:") for n in labels_of(issue))
                else " (no for: label)"
            )
            found.append(
                (
                    RANK[kind],
                    f"i{issue['id']}",
                    f"[{kind}] #{issue['number']} by {author}: {short(issue['title'])}{note}"
                    f" {issue['html_url']}",
                )
            )

        for comment in self.api(f"issues/comments?since={after}&per_page=100"):
            if parse(comment["created_at"]) < since - OVERLAP:
                continue  # an older comment edited since
            number = number_of(comment["issue_url"])
            author, body = comment["user"]["login"], comment.get("body")
            labels = labels_of(self.issue(number))
            if alert and alert in labels:
                kind = "alert"
            elif author in self.s.owners:
                kind = "owner"
            elif author in self.s.shared:
                if signed(body, self.s.agent_names, self.s.home_team) or acknowledgement(body):
                    continue  # an agent's signed post, or this watcher's own "Seen by ..."
                kind = "owner" if labels & self.s.owner_labels else "unsigned"
            elif acknowledgement(body):
                continue
            else:
                kind = "comment"
            found.append(
                (
                    RANK[kind],
                    f"c{comment['id']}",
                    f"[{kind}] #{number} by {author}: {short(body)} {comment['html_url']}",
                )
            )

        for comment in self.api(f"pulls/comments?since={after}&per_page=100"):
            author = comment["user"]["login"]
            if author in self.s.shared or parse(comment["created_at"]) < since - OVERLAP:
                continue
            kind = "owner" if author in self.s.owners else "review"
            found.append(
                (
                    RANK[kind],
                    f"r{comment['id']}",
                    f"[{kind}] #{number_of(comment['pull_request_url'])} by {author}:"
                    f" {short(comment.get('body'))} {comment['html_url']}",
                )
            )
        return self.emit(found)


TEAM_RANK = {"ack": 0, "blocking": 1, "issue": 2, "pr": 3, "comment": 4, "review": 5}


class TeamWatcher(Watcher):
    """An outside team's side: issues labelled `for:<team>` or `for:everyone`, and replies on what
    the team opened; never its own posts. The team's accounts are the ones that opened its
    "[notice] New team: <team>" issue."""

    def __init__(self, state_dir: Path, settings: Settings, team: str):
        super().__init__(state_dir, settings)
        self.team = team = team.lower()
        self.labels = {f"for:{team}", "for:everyone"}
        self._accounts: set[str] | None = None

    def accounts(self) -> set[str]:
        if self._accounts is None:
            query = urllib.parse.quote(f'repo:{self.s.repo} in:title "New team: {self.team}"')
            found = gh(f"search/issues?q={query}&per_page=20").get("items", [])
            title = f"new team: {self.team}"
            self._accounts = {
                item["user"]["login"] for item in found if item["title"].lower().endswith(title)
            }
        return self._accounts

    def ours(self, author: str, body: str | None) -> bool:
        return author in self.accounts() or team_signed(body, self.team)

    def addressed(self, issue: dict) -> bool:
        return bool(labels_of(issue) & self.labels) or self.ours(
            issue["user"]["login"], issue.get("body")
        )

    def once(self, now: datetime, since: datetime) -> list[str]:
        self._issues = {}
        found: list[tuple[int, str, str]] = []
        after = iso(since - OVERLAP)
        ack = f"Seen — watcher, {self.team}"

        for issue in self.api(f"issues?since={after}&state=all&per_page=100"):
            self._issues[issue["number"]] = issue
            if not self.addressed(issue) or self.ours(issue["user"]["login"], issue.get("body")):
                continue
            number = issue["number"]
            kind = "blocking" if blocking(issue) else "pr" if "pull_request" in issue else "issue"
            found.append(
                (
                    TEAM_RANK[kind],
                    f"i{issue['id']}",
                    f"[{kind}] #{number} by {issue['user']['login']}: {short(issue['title'])}"
                    f" {issue['html_url']}",
                )
            )
            new = parse(issue["created_at"]) >= since - OVERLAP
            if new and f"for:{self.team}" in labels_of(issue) and not self.seen(number, ack):
                found.append(
                    (
                        TEAM_RANK["ack"],
                        f"a{issue['id']}",
                        f'[ack] #{number}: comment "{ack}" on it once {issue["html_url"]}',
                    )
                )

        for path, kind, url_key in (
            (f"issues/comments?since={after}&per_page=100", "comment", "issue_url"),
            (f"pulls/comments?since={after}&per_page=100", "review", "pull_request_url"),
        ):
            for comment in self.api(path):
                if parse(comment["created_at"]) < since - OVERLAP:
                    continue
                author, body = comment["user"]["login"], comment.get("body")
                if self.ours(author, body) or acknowledgement(body) or confirmation(body):
                    continue
                number = number_of(comment[url_key])
                if not self.addressed(self.issue(number)):
                    continue
                found.append(
                    (
                        TEAM_RANK[kind],
                        f"{kind[0]}{comment['id']}",
                        f"[{kind}] #{number} by {author}: {short(body)} {comment['html_url']}",
                    )
                )
        return self.emit(found)


def make_watcher(state_dir: Path, settings: Settings, side: str) -> Watcher:
    if side.lower() == settings.home_team:
        return Watcher(state_dir, settings)
    return TeamWatcher(state_dir, settings, side)


# --- Keeping current ---------------------------------------------------------------------------


def fingerprint(path: Path = SCRIPT) -> bytes:
    """This script's bytes; empty once it's gone (a plugin update can remove the old version)."""
    try:
        return path.read_bytes()
    except OSError:
        return b""


def git(root: Path, *args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, timeout=timeout
    )


def checkout(root: Path) -> tuple[str, int]:
    """The clone's branch and how many tracked files have local changes."""
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    changed = git(root, "status", "--porcelain", "--untracked-files=no").stdout.strip()
    return branch, len(changed.splitlines()) if changed else 0


def pull(root: Path, work_branch: str) -> str:
    """'pulled', or why it didn't. Only a clean checkout of `work_branch` is pulled: on a working
    clone, a pull would move a branch under a busy agent."""
    if not (root / ".git").exists():
        return "not inside a clone of the repository: run the watcher from one"
    branch, changed = checkout(root)
    if branch != work_branch or changed:
        return (
            f"not pulled: the clone is on {branch or 'no branch'} with {changed} local change(s);"
            f" run the watcher from its own clean clone on {work_branch}"
        )
    out = git(root, "pull", "-q", "--ff-only", timeout=120)
    if out.returncode != 0:
        lines = (out.stderr or out.stdout).strip().splitlines()
        return "git pull failed: " + (lines[-1] if lines else f"exit {out.returncode}")
    return "pulled"


# One watcher per side: a session that loses track of its monitor (context compaction) arms a
# second one; the newest takes over and the older exits quietly at its next pass.
def claim(state_dir: Path) -> str:
    token = f"{os.getpid()}-{time.time_ns()}"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "running").write_text(token, encoding="utf-8")
    return token


def still_running(state_dir: Path, token: str) -> bool:
    try:
        return (state_dir / "running").read_text(encoding="utf-8").strip() == token
    except OSError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--side", help="the home team (default) or an outside team's name")
    parser.add_argument("--once", action="store_true", help="one pass, then exit")
    parser.add_argument("--since", help="look back from this UTC time (with --once: no state)")
    parser.add_argument("--repo-dir", help="the clone to read settings from (default: here)")
    parser.add_argument(
        "--config", help="the settings file (default: <clone>/.claude/crewline.yml)"
    )
    parser.add_argument("--state-dir", help="default ~/.crewline-watcher/<owner>-<name>/<side>")
    parser.add_argument("--no-update", action="store_true", help="never pull or reload")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)  # each line is an event

    try:
        config = find_config(args.config, args.repo_dir)
        text, settings = load(config)
    except (OSError, ValueError) as caught:
        print(f"[watcher-error] {short(str(caught), 200)}")
        return 2
    side = (args.side or settings.home_team).lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", side):
        print("[watcher-error] --side: a team name, lower case letters, digits and hyphens")
        return 2
    try:
        since_arg = parse(args.since) if args.since else None
    except ValueError:
        print(f"[watcher-error] --since: a UTC time like 2026-10-05T12:00:00Z (got {args.since!r})")
        return 2
    if settings.both:
        print(
            f"[watcher-error] crewline.yml: {', '.join(settings.both)} in both owner_accounts and"
            " shared_accounts, treated as shared; owner_accounts holds only logins the agents"
            " never post from"
        )
    state_dir = Path(
        args.state_dir
        or Path.home() / ".crewline-watcher" / settings.repo.replace("/", "-").lower() / side
    )
    watcher = make_watcher(state_dir, settings, side)

    if args.once:
        now = datetime.now(UTC)
        since = since_arg or parse(watcher.state["last_check"] or iso(now - timedelta(hours=1)))
        try:
            lines = watcher.once(now, since)
        except Exception as caught:  # noqa: BLE001 (a line for the session, not a traceback)
            print(f"[watcher-error] GitHub could not be read: {short(str(caught), 160)}")
            return 1
        print("\n".join(lines) if lines else "nothing new")
        if not args.since:
            watcher.state["last_check"] = iso(now)
            watcher.save()
        return 0

    root, me = config.parent.parent, fingerprint()
    last_error = last_update_error = None
    last_update = datetime.now(UTC)
    token = claim(state_dir)
    while True:
        if not still_running(state_dir, token):
            return 0  # a newer watcher on this side took over
        now = datetime.now(UTC)
        if not args.no_update and now - last_update >= timedelta(minutes=settings.update_minutes):
            last_update, problem = now, pull(root, settings.work_branch)
            if fingerprint() != me:
                print("[watcher-updated] the watcher script changed: arm the monitor again")
                return 0
            try:
                fresh = config.read_text(encoding="utf-8")
                if fresh != text:
                    settings = Settings(read_settings(fresh))
                    text, watcher = fresh, make_watcher(state_dir, settings, side)
            except (OSError, ValueError) as caught:
                problem = f"settings not reloaded, the old ones stay: {caught}"
            if problem != "pulled" and (
                last_update_error is None or now - last_update_error >= UPDATE_ERROR_AGAIN
            ):
                print(f"[watcher-error] could not update: {short(problem, 200)}")
                last_update_error = now
        since = parse(watcher.state["last_check"] or iso(now - timedelta(hours=1)))
        before = json.dumps(watcher.state)  # a failed pass must not half-mark items as said
        try:
            lines = watcher.once(now, since)
            if not still_running(state_dir, token):
                return 0  # taken over during the pass: the newer one says these
            for line in lines:
                print(line)
            watcher.state["last_check"] = iso(now)
            watcher.save()
        except Exception as caught:  # noqa: BLE001 (one bad pass must not end the watch)
            watcher.state = json.loads(before)
            if last_error is None or now - last_error >= ERROR_AGAIN:
                print(f"[watcher-error] GitHub could not be read: {short(str(caught), 160)}")
                last_error = now
        time.sleep(settings.poll_seconds)


if __name__ == "__main__":
    sys.exit(main())
