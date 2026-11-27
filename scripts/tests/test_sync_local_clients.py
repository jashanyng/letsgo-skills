"""使用隔离桩命令测试本机三端同步与核验脚本 sync-local-clients.sh。"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "sync-local-clients.sh"


class SyncLocalClientsTests(unittest.TestCase):
    def _create_fixture(self, version: str = "0.0.13") -> tuple[Path, Path, Path]:
        temp = tempfile.TemporaryDirectory(prefix="letsgo-sync-test-")
        self.addCleanup(temp.cleanup)
        base = Path(temp.name)

        repo = base / "repo"
        claude_dir = repo / "plugins" / "letsgo" / ".claude-plugin"
        claude_dir.mkdir(parents=True)
        (claude_dir / "plugin.json").write_text(
            json.dumps({"name": "letsgo", "version": version}),
            encoding="utf-8",
        )

        bin_dir = base / "bin"
        bin_dir.mkdir()
        log_file = base / "calls.log"
        log_file.write_text("", encoding="utf-8")
        return repo, bin_dir, log_file

    def _write_stub(self, bin_dir: Path, name: str, body: str) -> Path:
        path = bin_dir / name
        path.write_text(f"#!/bin/sh\nset -eu\n{body}\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def _run_sync(
        self,
        repo: Path,
        codex_bin: Path | str,
        claude_bin: Path | str,
        agy_bin: Path | str,
        *args: str,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["LETSGO_REPO_ROOT"] = str(repo)
        env["CODEX_BIN"] = str(codex_bin)
        env["CLAUDE_BIN"] = str(claude_bin)
        env["AGY_BIN"] = str(agy_bin)
        return subprocess.run(
            ["sh", str(SCRIPT), *args],
            cwd=repo,
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

    def test_sync_updates_and_verifies_all_installed_clients(self) -> None:
        repo, bin_dir, log_file = self._create_fixture("0.0.13")
        state_dir = repo.parent / "state"
        state_dir.mkdir()
        for client in ("codex", "claude", "agy"):
            (state_dir / client).write_text("0.0.12", encoding="utf-8")

        codex = self._write_stub(
            bin_dir,
            "codex",
            f'''printf 'codex %s\\n' "$*" >> {str(log_file)!r}
ver=$(cat {str(state_dir / "codex")!r})
if [ "$1" = "plugin" ] && [ "$2" = "add" ]; then
  printf '0.0.13' > {str(state_dir / "codex")!r}
  exit 0
fi
if [ "$1" = "plugin" ] && [ "$2" = "list" ]; then
  cat <<EOF
Marketplace \\`letsgo-skills\\`

PLUGIN                STATUS              VERSION  SOURCE
letsgo@letsgo-skills  installed, enabled  $ver   git@example/repo.git, ref \\`$ver\\`
EOF
  exit 0
fi''',
        )
        claude = self._write_stub(
            bin_dir,
            "claude",
            f'''printf 'claude %s\\n' "$*" >> {str(log_file)!r}
ver=$(cat {str(state_dir / "claude")!r})
if [ "$1" = "plugin" ] && [ "$2" = "update" ]; then
  printf '0.0.13' > {str(state_dir / "claude")!r}
  exit 0
fi
if [ "$1" = "plugin" ] && [ "$2" = "list" ]; then
  cat <<EOF
  ❯ letsgo@letsgo-skills
    Version: $ver
    Scope: user
    Status: ✔ enabled
EOF
  exit 0
fi''',
        )
        agy = self._write_stub(
            bin_dir,
            "agy",
            f'''printf 'agy %s\\n' "$*" >> {str(log_file)!r}
ver=$(cat {str(state_dir / "agy")!r})
if [ "$1" = "plugin" ] && [ "$2" = "install" ]; then
  printf '0.0.13' > {str(state_dir / "agy")!r}
  exit 0
fi
if [ "$1" = "plugin" ] && [ "$2" = "list" ]; then
  printf -- '- letsgo (enabled, %s)\\n' "$ver"
  exit 0
fi''',
        )

        res = self._run_sync(repo, codex, claude, agy)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0.0.13", res.stdout)
        self.assertIn("新会话", res.stdout)
        calls = log_file.read_text(encoding="utf-8")
        self.assertIn("codex plugin marketplace upgrade letsgo-skills", calls)
        self.assertIn("codex plugin add letsgo@letsgo-skills", calls)
        self.assertIn("claude plugin marketplace update letsgo-skills", calls)
        self.assertIn("claude plugin update letsgo@letsgo-skills", calls)
        self.assertIn(f"agy plugin install {repo / 'plugins' / 'letsgo'}", calls)

    def test_sync_skips_missing_cli_and_uninstalled_plugin(self) -> None:
        repo, bin_dir, log_file = self._create_fixture("0.0.13")
        claude = self._write_stub(
            bin_dir,
            "claude",
            f'''printf 'claude %s\\n' "$*" >> {str(log_file)!r}
if [ "$1" = "plugin" ] && [ "$2" = "list" ]; then
  echo "  ❯ other@market"
  echo "    Version: 1.0.0"
  exit 0
fi''',
        )
        agy = self._write_stub(
            bin_dir,
            "agy",
            f'''printf 'agy %s\\n' "$*" >> {str(log_file)!r}
if [ "$1" = "plugin" ] && [ "$2" = "list" ]; then
  echo "- letsgo (enabled, 0.0.13)"
fi''',
        )

        res = self._run_sync(repo, "", claude, agy)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("跳过", res.stdout)
        self.assertNotIn("claude plugin update", log_file.read_text(encoding="utf-8"))

    def test_sync_fails_when_verified_version_mismatches(self) -> None:
        repo, bin_dir, _ = self._create_fixture("0.0.13")
        agy = self._write_stub(
            bin_dir,
            "agy",
            '''if [ "$1" = "plugin" ] && [ "$2" = "list" ]; then
  echo "- letsgo (enabled, 0.0.12)"
fi''',
        )
        res = self._run_sync(repo, "", "", agy)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Antigravity", res.stdout + res.stderr)

    def test_check_only_verifies_without_running_updates(self) -> None:
        repo, bin_dir, log_file = self._create_fixture("0.0.13")
        codex = self._write_stub(
            bin_dir,
            "codex",
            f'''printf 'codex %s\\n' "$*" >> {str(log_file)!r}
echo "letsgo@letsgo-skills  installed, enabled  0.0.13   src"''',
        )
        claude = self._write_stub(
            bin_dir,
            "claude",
            f'''printf 'claude %s\\n' "$*" >> {str(log_file)!r}
echo "  ❯ letsgo@letsgo-skills"
echo "    Version: 0.0.13"''',
        )
        agy = self._write_stub(
            bin_dir,
            "agy",
            f'''printf 'agy %s\\n' "$*" >> {str(log_file)!r}
echo "- letsgo (enabled, 0.0.13)"''',
        )

        res = self._run_sync(repo, codex, claude, agy, "--check-only")
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        calls = log_file.read_text(encoding="utf-8")
        self.assertNotIn("upgrade", calls)
        self.assertNotIn("update", calls)
        self.assertNotIn("install", calls)
        self.assertNotIn("add", calls)


if __name__ == "__main__":
    unittest.main()
