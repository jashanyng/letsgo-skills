"""在隔离的本地裸远端与克隆仓库中端到端验证 release.sh 的裸标签与 x/y 升版门禁。"""

from __future__ import annotations

from datetime import date
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_MANIFESTS = (
    "plugins/letsgo/.claude-plugin/plugin.json",
    "plugins/letsgo/.codex-plugin/plugin.json",
    "plugins/letsgo/.antigravity-plugin/plugin.json",
)
MARKETPLACES = (
    ".claude-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
)


class ReleaseScriptTests(unittest.TestCase):
    def _git(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=True,
        )

    def _create_repo(self, initial_version: str, initial_tag: str | None) -> tuple[Path, Path]:
        temp = tempfile.TemporaryDirectory(prefix="letsgo-release-test-")
        self.addCleanup(temp.cleanup)
        base = Path(temp.name)
        origin = base / "origin.git"
        work = base / "work"
        subprocess.run(["git", "init", "--bare", "-b", "main", str(origin)], check=True, capture_output=True, text=True)

        seed = base / "seed"
        seed.mkdir()
        for name in ("plugins", "scripts", "docs", ".agents", ".claude-plugin"):
            shutil.copytree(
                ROOT / name,
                seed / name,
                symlinks=True,
                ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", "*.pyc"),
            )
        for name in ("GLOSSARY.md", "README.md", "AGENTS.md", ".gitignore"):
            shutil.copy2(ROOT / name, seed / name)
        changelog_path = seed / "CHANGELOG.md"
        changelog_path.write_text(
            f"# 变更日志（Changelog）\n\n## [Unreleased]\n\n## [{initial_version}]\n\n- 种子版本基线。\n",
            encoding="utf-8",
        )

        self._set_manifests(seed, initial_version, initial_version)
        self._git(seed, "init", "-b", "main")
        self._git(seed, "config", "user.name", "Test User")
        self._git(seed, "config", "user.email", "test@example.com")
        self._git(seed, "add", "-A")
        self._git(seed, "commit", "-m", "initial")
        if initial_tag:
            self._git(seed, "tag", "-a", initial_tag, "-m", f"letsgo {initial_tag}")
        self._git(seed, "remote", "add", "origin", str(origin))
        self._git(seed, "push", "-u", "origin", "main")
        if initial_tag:
            self._git(seed, "push", "origin", initial_tag)

        subprocess.run(["git", "clone", str(origin), str(work)], check=True, capture_output=True, text=True)
        self._git(work, "config", "user.name", "Test User")
        self._git(work, "config", "user.email", "test@example.com")
        return origin, work

    def _set_manifests(self, repo: Path, version: str, ref: str) -> None:
        for relative in PLUGIN_MANIFESTS:
            path = repo / relative
            data = json.loads(path.read_text(encoding="utf-8"))
            data["version"] = version
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for relative in MARKETPLACES:
            path = repo / relative
            data = json.loads(path.read_text(encoding="utf-8"))
            for plugin in data["plugins"]:
                if plugin["name"] == "letsgo":
                    plugin["source"]["ref"] = ref
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _run_release(self, work: Path, *args: str, skip_tests: bool = True) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        if skip_tests:
            env["LETSGO_RELEASE_SKIP_TESTS"] = "1"
        else:
            env.pop("LETSGO_RELEASE_SKIP_TESTS", None)
        return subprocess.run(
            ["sh", "scripts/release.sh", *args],
            cwd=work,
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

    def _assert_clean(self, work: Path) -> None:
        status = self._git(work, "status", "--porcelain").stdout.strip()
        self.assertEqual(status, "", f"working tree should stay clean, got:\n{status}")

    def test_rejects_v_prefix(self) -> None:
        _, work = self._create_repo("0.0.10", "0.0.10")
        result = self._run_release(work, "v0.0.11")
        self.assertNotEqual(result.returncode, 0)
        self._assert_clean(work)

    def test_pure_z_bump_succeeds_with_bare_tag(self) -> None:
        origin, work = self._create_repo("0.0.10", "0.0.10")
        result = self._run_release(work, "0.0.11")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        for relative in PLUGIN_MANIFESTS:
            data = json.loads((work / relative).read_text(encoding="utf-8"))
            self.assertEqual(data["version"], "0.0.11")
        for relative in MARKETPLACES:
            data = json.loads((work / relative).read_text(encoding="utf-8"))
            refs = [p["source"]["ref"] for p in data["plugins"] if p["name"] == "letsgo"]
            self.assertEqual(refs, ["0.0.11"])

        local_tags = self._git(work, "tag", "-l").stdout.splitlines()
        self.assertIn("0.0.11", local_tags)
        self.assertNotIn("v0.0.11", local_tags)

        remote_tags = self._git(origin, "tag", "-l").stdout.splitlines()
        self.assertIn("0.0.11", remote_tags)
        self.assertNotIn("v0.0.11", remote_tags)

        last_msg = self._git(work, "log", "-n", "1", "--format=%s").stdout.strip()
        self.assertEqual(last_msg, "release: 0.0.11")

    def test_xy_bump_is_blocked_without_flag(self) -> None:
        _, work = self._create_repo("0.0.10", "0.0.10")
        for target in ("0.1.0", "1.0.0"):
            result = self._run_release(work, target)
            self.assertNotEqual(result.returncode, 0, f"{target} must be rejected without --allow-xy-bump")
            self.assertIn("--allow-xy-bump", result.stderr)
            self._assert_clean(work)

    def test_non_increasing_z_is_blocked(self) -> None:
        _, work = self._create_repo("0.0.10", "0.0.10")
        for target in ("0.0.10", "0.0.9"):
            result = self._run_release(work, target)
            self.assertNotEqual(result.returncode, 0)
            self._assert_clean(work)

    def test_allow_xy_bump_permits_forward_and_initial_reset_but_blocks_bare_downgrade(self) -> None:
        origin, work = self._create_repo("0.0.10", "0.0.10")
        ok = self._run_release(work, "--allow-xy-bump", "0.1.0")
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertIn("0.1.0", self._git(origin, "tag", "-l").stdout.splitlines())

        downgrade = self._run_release(work, "--allow-xy-bump", "0.0.12")
        self.assertNotEqual(downgrade.returncode, 0)
        self._assert_clean(work)

        origin2, work2 = self._create_repo("3.6.1", "v3.6.1")
        blocked = self._run_release(work2, "0.0.10")
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("--allow-xy-bump", blocked.stderr)
        self._assert_clean(work2)

        reset_ok = self._run_release(work2, "--allow-xy-bump", "0.0.10")
        self.assertEqual(reset_ok.returncode, 0, reset_ok.stdout + reset_ok.stderr)
        self.assertIn("0.0.10", self._git(origin2, "tag", "-l").stdout.splitlines())

    def test_release_archives_non_empty_unreleased_changelog(self) -> None:
        _, work = self._create_repo("0.0.10", "0.0.10")
        changelog = work / "CHANGELOG.md"
        text = changelog.read_text(encoding="utf-8")
        changelog.write_text(
            text.replace("\n## [Unreleased]\n", "\n## [Unreleased]\n\n### 新增\n\n- 新增测试条目。\n", 1),
            encoding="utf-8",
        )
        self._git(work, "add", "CHANGELOG.md")
        self._git(work, "commit", "-m", "docs: add unreleased note")

        result = self._run_release(work, "0.0.11")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        updated = changelog.read_text(encoding="utf-8")
        today = date.today().isoformat()
        match = re.search(
            rf"^## \[Unreleased\]\s*\n+## \[0\.0\.11\] - {re.escape(today)}\n+(.*?)\n+## \[0\.0\.10\]",
            updated,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, f"unexpected CHANGELOG.md layout:\n{updated}")
        assert match is not None
        self.assertIn("- 新增测试条目。", match.group(1))

        check = subprocess.run(
            [sys.executable, "scripts/validate.py"], cwd=work, text=True, capture_output=True, check=False
        )
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_release_archives_empty_unreleased_changelog(self) -> None:
        _, work = self._create_repo("0.0.10", "0.0.10")
        changelog = work / "CHANGELOG.md"
        changelog.write_text(
            "# 变更日志（Changelog）\n\n## [Unreleased]\n\n## [0.0.10]\n\n- 基线版本。\n",
            encoding="utf-8",
        )
        self._git(work, "add", "CHANGELOG.md")
        self._git(work, "commit", "-m", "docs: reset unreleased to empty")

        result = self._run_release(work, "0.0.11")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        updated = changelog.read_text(encoding="utf-8")
        today = date.today().isoformat()
        match = re.search(
            rf"^## \[Unreleased\]\s*\n+## \[0\.0\.11\] - {re.escape(today)}\n+(.+?)\n+## \[0\.0\.10\]",
            updated,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, f"unexpected CHANGELOG.md layout:\n{updated}")
        assert match is not None
        self.assertTrue(match.group(1).strip())

        check = subprocess.run(
            [sys.executable, "scripts/validate.py"], cwd=work, text=True, capture_output=True, check=False
        )
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_release_archives_preserving_fenced_code_block_headings(self) -> None:
        _, work = self._create_repo("0.0.10", "0.0.10")
        changelog = work / "CHANGELOG.md"
        fenced_example = (
            "### 示例\n\n"
            "- 保留围栏代码块内的标题示例：\n\n"
            "```markdown\n"
            "## [Unreleased]\n\n"
            "## [0.0.11]\n"
            "- 示例条目\n"
            "```\n\n"
            "~~~markdown\n"
            "## [0.0.11]\n"
            "~~~\n"
        )
        text = changelog.read_text(encoding="utf-8")
        changelog.write_text(
            text.replace("\n## [Unreleased]\n", f"\n## [Unreleased]\n\n{fenced_example}", 1),
            encoding="utf-8",
        )
        self._git(work, "add", "CHANGELOG.md")
        self._git(work, "commit", "-m", "docs: add fenced example in unreleased")

        result = self._run_release(work, "0.0.11")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        updated = changelog.read_text(encoding="utf-8")
        today = date.today().isoformat()
        match = re.search(
            rf"^## \[Unreleased\]\s*\n+## \[0\.0\.11\] - {re.escape(today)}\n+(.*?)\n+## \[0\.0\.10\]",
            updated,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, f"unexpected CHANGELOG.md layout:\n{updated}")
        assert match is not None
        self.assertIn(fenced_example.strip(), match.group(1))

        check = subprocess.run(
            [sys.executable, "scripts/validate.py"], cwd=work, text=True, capture_output=True, check=False
        )
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_release_blocks_and_rolls_back_when_unit_tests_fail(self) -> None:
        _, work = self._create_repo("0.0.10", "0.0.10")
        tests_dir = work / "scripts" / "tests"
        for test_file in tests_dir.glob("test_*.py"):
            test_file.unlink()
        (tests_dir / "test_failing_gate.py").write_text(
            "import unittest\n\n\nclass FailingGateTest(unittest.TestCase):\n    def test_boom(self) -> None:\n        self.fail('boom')\n",
            encoding="utf-8",
        )
        self._git(work, "add", "-A")
        self._git(work, "commit", "-m", "test: add failing gate")

        result = self._run_release(work, "0.0.11", skip_tests=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("单元测试未通过", result.stderr)
        self._assert_clean(work)


if __name__ == "__main__":
    unittest.main()
