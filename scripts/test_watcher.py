"""watcher.py's rules against made-up GitHub answers; no network.

python3 scripts/test_watcher.py
"""

import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import watcher  # noqa: E402

NOW = datetime(2026, 10, 7, 12, 0, tzinfo=timezone.utc)
SINCE = NOW - timedelta(minutes=5)
URL = "https://github.com/x"
REPO = "acme/app"
BOT = "acme-agents"  # the account the home agents share
BOSS = "acme-owner"  # the owner's own account

CONFIG = f"""\
# a comment line
repo: {REPO}                 # trailing comment
work_branch: develop
owner: Pat
owner_accounts: [{BOSS}]
home_team: acme
shared_accounts: [{BOT}, "other-bot"]
agent_names: ["Agent {{N}}", Lead]
coordinator:
  name: Lead
  session: Acme lead
docs:
  definition_of_done: docs/DONE.md#done   # the # inside the value stays
merge_gate:
  high_risk: [auth, personal data, money]
  max_review_cycles: 2
watcher:
  active_seconds: 900
  ack_hours: 2
  alert_label: alert
  owner_labels: [needs:owner, owner:do]
"""
SETTINGS = watcher.Settings(watcher.read_settings(CONFIG))


def at(minutes_ago: float) -> str:
    return watcher.iso(NOW - timedelta(minutes=minutes_ago))


def issue(number, author="someone", labels=(), created=1, pr=False, title=None):
    item = {
        "number": number,
        "id": number * 10,
        "title": title or f"issue {number}",
        "user": {"login": author},
        "labels": [{"name": n} for n in labels],
        "created_at": at(created),
        "html_url": URL,
    }
    if pr:
        item["pull_request"] = {}
    return item


def comment(cid, number, author, body, created=1, review=False):
    key = "pull_request_url" if review else "issue_url"
    kind = "pulls" if review else "issues"
    return {
        "id": cid,
        key: f"https://api.github.com/repos/{REPO}/{kind}/{number}",
        "user": {"login": author},
        "body": body,
        "created_at": at(created),
        "html_url": URL,
    }


class Fake:
    """Answers `gh api <path>` by the first key found in the path."""

    def __init__(self, **answers):
        self.answers = answers
        self.paths = []

    def __call__(self, path):
        self.paths.append(path)
        for key, value in self.answers.items():
            if key in path:
                return value
        if "/issues/" in path and "/comments" not in path:
            return self.answers.get("by_number", {}).get(int(path.rsplit("/", 1)[1]), issue(0))
        return []


def tags(lines):
    return [" ".join(line.split()[:2]) for line in lines]


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.real_gh = watcher.gh
        self.w = self.make(Path(self.dir.name))

    def make(self, state):
        return watcher.Watcher(state, SETTINGS)

    def tearDown(self):
        watcher.gh = self.real_gh
        self.dir.cleanup()

    def run_once(self, fake, now=NOW):
        watcher.gh = fake
        return self.w.once(now, SINCE)


class SettingsReader(unittest.TestCase):
    def test_the_template_subset_is_read(self):
        data = watcher.read_settings(CONFIG)
        self.assertEqual(data["repo"], REPO)
        self.assertEqual(data["shared_accounts"], [BOT, "other-bot"])
        self.assertEqual(data["coordinator"], {"name": "Lead", "session": "Acme lead"})
        self.assertEqual(data["docs"]["definition_of_done"], "docs/DONE.md#done")
        self.assertEqual(data["merge_gate"]["high_risk"], ["auth", "personal data", "money"])
        self.assertEqual(data["merge_gate"]["max_review_cycles"], 2)
        self.assertEqual(data["watcher"]["owner_labels"], ["needs:owner", "owner:do"])

    def test_quoted_list_items(self):
        data = watcher.read_settings('a: ["Agent {N}", "Lead"]\nb: ["x, y", z]\nc: []\n')
        self.assertEqual(data["a"], ["Agent {N}", "Lead"])
        self.assertEqual(data["b"], ["x, y", "z"])
        self.assertEqual(data["c"], [])

    def test_the_shipped_template_parses(self):
        template = Path(__file__).resolve().parent.parent / "templates" / "crewline.yml"
        data = watcher.read_settings(template.read_text(encoding="utf-8"))
        self.assertIn("watcher", data)
        self.assertIsInstance(data["watcher"], dict)
        self.assertEqual(data["agent_names"], ["Agent {N}"])
        with self.assertRaises(ValueError):  # placeholders left in
            watcher.Settings(data)

    def test_defaults_and_checks(self):
        s = watcher.Settings(watcher.read_settings(f"repo: {REPO}\nhome_team: acme\n"))
        self.assertEqual(s.work_branch, "develop")
        self.assertEqual(s.agent_names, ["Agent {N}"])
        self.assertEqual((s.alert_label, s.poll_seconds, s.update_minutes), ("", 60, 15))
        self.assertEqual(s.owner_labels, {"needs:owner", "owner:do"})
        self.assertEqual(s.owners, set())
        with self.assertRaises(ValueError):
            watcher.Settings(watcher.read_settings("repo: not-a-repo\nhome_team: acme\n"))
        with self.assertRaises(ValueError):
            watcher.read_settings("  indented: first\n")
        off = watcher.Settings(
            watcher.read_settings(f'repo: {REPO}\nhome_team: acme\nwatcher:\n  alert_label: ""\n')
        )
        self.assertEqual(off.alert_label, "")


class Signing(unittest.TestCase):
    names = ["Agent {N}", "Lead"]

    def test_a_signature_is_a_form_not_a_mention(self):
        def ok(body):
            return watcher.signed(body, self.names, "acme")

        self.assertTrue(ok("Agent 4: done"))
        self.assertTrue(ok("Applied — Agent 1, acme"))
        self.assertTrue(ok("Lead: merged"))
        self.assertTrue(ok("Review\n\nbody\n\n— Agent 4 (coordinator), acme"))
        self.assertTrue(ok("text\n\n— Planner, acme"))  # the team's own sign-off
        self.assertFalse(ok("watcher test: should reach Agent 4 as unsigned"))
        self.assertFalse(ok("Re-review by Agent 4 with the second pass"))
        self.assertFalse(ok("Leader of the pack"))  # a name must end where it ends
        self.assertFalse(ok(""))

    def test_a_team_signature_is_a_form_not_a_mention(self):
        self.assertTrue(watcher.team_signed("Applied — Builder, beta (now runs…)", "beta"))
        self.assertTrue(watcher.team_signed("Seen — watcher, beta", "beta"))
        self.assertTrue(watcher.team_signed("text\n\n— Builder, beta", "beta"))
        self.assertTrue(watcher.team_signed("fixed it — Builder, beta", "beta"))
        self.assertFalse(
            watcher.team_signed(
                "Agent 4: your watcher only needs its usual `Seen — watcher, beta`.\n\n"
                "— Agent 4 (coordinator), acme",
                "beta",
            )
        )
        self.assertFalse(watcher.team_signed("Applied — Builder, betax", "beta"))


class HomeSide(Base):
    def test_an_alert_comes_first_and_again_only_after_an_hour(self):
        fake = Fake(
            **{
                "labels=alert": [issue(7, BOSS, ["alert"])],
                "issues?since": [issue(8, "outsider", ["for:acme"])],
            }
        )
        lines = self.run_once(fake)
        self.assertEqual(tags(lines), ["[alert] #7", "[issue] #8"])
        self.assertEqual(self.run_once(fake, NOW + timedelta(minutes=30)), [])
        self.assertEqual(tags(self.run_once(fake, NOW + timedelta(minutes=61))), ["[alert] #7"])

    def test_no_alert_label_no_alert_query(self):
        self.w.s = watcher.Settings(
            watcher.read_settings(f'repo: {REPO}\nhome_team: acme\nwatcher:\n  alert_label: ""\n')
        )
        fake = Fake()
        self.run_once(fake)
        self.assertFalse(any("labels=" in p for p in fake.paths))

    def test_comments_are_sorted_by_who_wrote_them(self):
        fake = Fake(
            **{
                "issues/comments?since": [
                    comment(1, 5, BOT, "Agent 4: done"),
                    comment(2, 5, BOT, "Applied — Agent 1, acme"),
                    comment(3, 5, BOT, "forgot to sign"),
                    comment(4, 6, BOT, "no sign on an owner issue"),
                    comment(5, 5, BOSS, "my answer"),
                    comment(6, 5, "outsider", "Seen — watcher, beta"),
                    comment(7, 5, "outsider", "a question"),
                    comment(8, 5, "outsider", "Applied — Builder, beta"),
                    comment(9, 7, BOT, "done, paid"),
                    comment(10, 7, BOT, "Agent 2: noted"),
                ],
                "by_number": {
                    5: issue(5),
                    6: issue(6, labels=["needs:owner"]),
                    7: issue(7, labels=["owner:do"]),
                },
            }
        )
        self.assertEqual(
            tags(self.run_once(fake)),
            [
                "[owner] #6",
                "[owner] #5",
                "[owner] #7",
                "[unsigned] #5",
                "[comment] #5",
                "[comment] #5",
            ],
        )

    def test_a_ready_pr_with_new_commits_is_a_review_request(self):
        def pulls(*prs):
            return Fake(
                **{
                    "pulls?state=open": [
                        {
                            "number": n,
                            "head": {"sha": sha},
                            "draft": draft,
                            "title": f"pr {n}",
                            "user": {"login": BOT},
                            "html_url": URL,
                        }
                        for n, sha, draft in prs
                    ]
                }
            )

        self.assertEqual(self.run_once(pulls((1, "aaa", False), (2, "bbb", True))), [])  # records
        lines = self.run_once(pulls((1, "ccc", False), (2, "bbb", False), (3, "ddd", False)))
        self.assertEqual(tags(lines), ["[review-request] #1", "[review-request] #2"])
        self.assertIn("new commits", lines[0])
        self.assertIn("marked ready", lines[1])
        self.assertEqual(self.run_once(pulls((1, "ccc", False), (2, "bbb", False))), [])
        self.assertEqual(self.run_once(pulls((1, "eee", True))), [])  # back to draft: quiet

    def test_a_comment_on_an_alert_issue_is_an_alert(self):
        fake = Fake(
            **{
                "issues/comments?since": [comment(1, 9, BOSS, "Resolved at 13:00")],
                "by_number": {9: issue(9, labels=["alert"])},
            }
        )
        self.assertEqual(tags(self.run_once(fake)), ["[alert] #9"])

    def test_issues_by_kind(self):
        fake = Fake(
            **{
                "issues?since": [
                    issue(10, "outsider", pr=True),
                    issue(11, "outsider"),
                    issue(12, "outsider", ["for:acme"], title="[blocking] need a decision"),
                    issue(13, BOSS),
                ],
                "pulls/comments?since": [
                    comment(1, 10, "outsider", "nit", review=True),
                    comment(2, 10, BOT, "Agent 2: fixed", review=True),
                ],
            }
        )
        lines = self.run_once(fake)
        self.assertEqual(
            tags(lines),
            ["[owner] #13", "[blocking] #12", "[issue] #11", "[review] #10", "[pr] #10"],
        )
        self.assertIn("(no for: label)", lines[2])

    def test_each_item_is_said_once(self):
        fake = Fake(**{"issues?since": [issue(8, "outsider", pr=True)]})
        self.assertEqual(len(self.run_once(fake)), 1)
        self.assertEqual(self.run_once(fake), [])

    def test_agents_issues_and_old_comments_are_not_routed(self):
        fake = Fake(
            **{
                "issues?since": [issue(8, BOT), issue(9, "other-bot")],
                "issues/comments?since": [comment(1, 5, "outsider", "edited", created=60)],
                "by_number": {5: issue(5)},
            }
        )
        self.assertEqual(self.run_once(fake), [])

    def test_a_team_issue_unseen_for_ack_hours_is_said_once(self):
        fake = Fake(
            **{
                "issues?state=open": [
                    issue(3, labels=["for:beta"], created=150),
                    issue(4, labels=["for:beta"], created=30),  # too young
                    issue(5, labels=["for:acme"], created=150),  # ours
                ],
                "issues/3/comments": [comment(1, 3, "x", "a note")],
            }
        )
        lines = self.run_once(fake)
        self.assertEqual(tags(lines), ["[watcher-down] #3"])
        self.assertIn("for:beta", lines[0])
        self.assertEqual(self.run_once(fake), [])

    def test_a_seen_team_issue_is_not_asked_again(self):
        fake = Fake(
            **{
                "issues?state=open": [issue(3, labels=["for:beta"], created=150)],
                "issues/3/comments": [comment(1, 3, "beta-bot", "Seen — watcher, beta")],
            }
        )
        self.assertEqual(self.run_once(fake), [])
        self.run_once(fake)
        self.assertEqual(sum("issues/3/comments" in p for p in fake.paths), 1)


NOTICE = {"items": [{"title": "[notice] New team: beta", "user": {"login": "beta-bot"}}]}


class TeamSide(Base):
    def make(self, state):
        return watcher.TeamWatcher(state, SETTINGS, "beta")

    def test_a_new_issue_for_the_team_is_routed_and_acknowledged_once(self):
        fake = Fake(
            **{
                "search/issues": NOTICE,
                "issues?since": [issue(20, BOT, ["for:beta"])],
                "issues/20/comments": [],
            }
        )
        self.assertEqual([line.split()[0] for line in self.run_once(fake)], ["[ack]", "[issue]"])
        self.assertEqual(self.run_once(fake), [])

    def test_an_issue_already_seen_needs_no_ack(self):
        fake = Fake(
            **{
                "search/issues": NOTICE,
                "issues?since": [issue(20, BOT, ["for:beta"], title="[blocking] which table?")],
                "issues/20/comments": [comment(1, 20, "beta-bot", "Seen — watcher, beta")],
            }
        )
        self.assertEqual(tags(self.run_once(fake)), ["[blocking] #20"])

    def test_notices_for_everyone_reach_the_team_but_not_others_confirmations(self):
        fake = Fake(
            **{
                "search/issues": NOTICE,
                "issues?since": [issue(21, BOT, ["for:everyone"])],
                "issues/comments?since": [comment(1, 21, BOT, "Applied — Agent 1, acme")],
                "by_number": {21: issue(21, BOT, ["for:everyone"])},
            }
        )
        self.assertEqual([line.split()[0] for line in self.run_once(fake)], ["[issue]"])

    def test_replies_on_what_the_team_opened_are_routed_its_own_posts_are_not(self):
        fake = Fake(
            **{
                "search/issues": NOTICE,
                "issues/comments?since": [
                    comment(1, 30, BOT, "Agent 4: reviewed"),
                    comment(2, 30, "beta-bot", "thanks"),
                    comment(3, 30, "someone", "fixed it — Builder, beta"),
                    comment(4, 31, BOT, "Agent 4: elsewhere"),
                ],
                "by_number": {30: issue(30, "beta-bot"), 31: issue(31)},
            }
        )
        self.assertEqual(tags(self.run_once(fake)), ["[comment] #30"])

    def test_other_issues_are_not_the_teams(self):
        fake = Fake(
            **{
                "search/issues": NOTICE,
                "issues?since": [issue(40, "other", ["for:acme"]), issue(41, "beta-bot")],
            }
        )
        self.assertEqual(self.run_once(fake), [])

    def test_the_side_picks_the_watcher(self):
        state = Path(self.dir.name)
        self.assertIs(type(watcher.make_watcher(state, SETTINGS, "acme")), watcher.Watcher)
        self.assertIs(type(watcher.make_watcher(state, SETTINGS, "beta")), watcher.TeamWatcher)


class OneWatcher(unittest.TestCase):
    def test_the_newest_watcher_takes_over_and_the_older_one_steps_aside(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)
            older = watcher.claim(state)
            self.assertTrue(watcher.still_running(state, older))
            newer = watcher.claim(state)
            self.assertFalse(watcher.still_running(state, older))
            self.assertTrue(watcher.still_running(state, newer))


class Update(unittest.TestCase):
    def test_outside_a_clone_it_says_so(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertIn("not inside a clone", watcher.pull(Path(empty), "develop"))

    def pulls_on(self, branch, changed):
        """What pull() says on a clone in this state, and whether it ran `git pull`."""
        ran = []
        real = (watcher.checkout, watcher.git)
        watcher.checkout = lambda root: (branch, changed)

        def fake_git(root, *args, timeout=60):
            ran.append(args)
            return subprocess.CompletedProcess(args, 0, "", "")

        watcher.git = fake_git
        try:
            with tempfile.TemporaryDirectory() as tmp:
                (Path(tmp) / ".git").mkdir()
                return watcher.pull(Path(tmp), "develop"), any("pull" in a for a in ran)
        finally:
            watcher.checkout, watcher.git = real

    def test_only_a_clean_work_branch_checkout_is_pulled(self):
        said, pulled = self.pulls_on("feat/x", 0)
        self.assertIn("not pulled: the clone is on feat/x", said)
        self.assertFalse(pulled)
        said, pulled = self.pulls_on("develop", 2)
        self.assertIn("2 local change(s)", said)
        self.assertFalse(pulled)
        said, pulled = self.pulls_on("develop", 0)
        self.assertTrue(pulled)
        self.assertEqual(said, "pulled")

    def test_a_changed_or_missing_script_is_noticed(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "watcher.py"
            script.write_text("v1")
            before = watcher.fingerprint(script)
            script.write_text("v2")
            self.assertNotEqual(watcher.fingerprint(script), before)
            self.assertEqual(watcher.fingerprint(Path(tmp) / "gone.py"), b"")


class Main(unittest.TestCase):
    def setUp(self):
        self.real_gh = watcher.gh

    def tearDown(self):
        watcher.gh = self.real_gh

    def test_once_reads_the_settings_and_prints(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            (repo / ".claude").mkdir(parents=True)
            (repo / ".claude" / "crewline.yml").write_text(CONFIG, encoding="utf-8")
            (repo / "sub").mkdir()
            new = issue(8, "outsider", pr=True)
            new["created_at"] = watcher.iso(datetime.now(timezone.utc))  # main() uses the real clock
            watcher.gh = Fake(**{"issues?since": [new]})
            out = io.StringIO()
            with redirect_stdout(out):
                code = watcher.main(
                    ["--once", "--repo-dir", str(repo / "sub"), "--state-dir", str(Path(tmp) / "s")]
                )
            self.assertEqual(code, 0)
            self.assertTrue(out.getvalue().startswith("[pr] #8"))
            self.assertTrue((Path(tmp) / "s" / "state.json").exists())

    def test_missing_or_unfilled_settings_are_a_watcher_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(watcher.main(["--once", "--repo-dir", tmp]), 2)
            self.assertTrue(out.getvalue().startswith("[watcher-error] no .claude/crewline.yml"))
            (Path(tmp) / ".claude").mkdir()
            (Path(tmp) / ".claude" / "crewline.yml").write_text("repo: <owner>/<name>\n")
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(watcher.main(["--once", "--repo-dir", tmp]), 2)
            self.assertIn("fill in `repo`", out.getvalue())


if __name__ == "__main__":
    unittest.main()
