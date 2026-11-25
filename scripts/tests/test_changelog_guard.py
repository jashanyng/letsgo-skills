"""changelog_guard 模块的单元测试（围栏代码块遮蔽、文档校验与归档）。"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import changelog_guard  # noqa: E402


class ChangelogGuardTests(unittest.TestCase):
    def test_mask_preserves_length_and_newline_positions_with_crlf(self) -> None:
        raw = "# Title\r\n\r\n```markdown\r\n## [Unreleased]\r\n## [0.0.11]\r\n```\r\nEnd"
        normalized = raw.replace("\r\n", "\n")
        masked = changelog_guard.mask_fenced_code_blocks(raw)

        self.assertEqual(len(masked), len(normalized))
        self.assertEqual(
            [idx for idx, ch in enumerate(masked) if ch == "\n"],
            [idx for idx, ch in enumerate(normalized) if ch == "\n"],
        )
        self.assertNotIn("## [Unreleased]", masked)
        self.assertNotIn("## [0.0.11]", masked)
        self.assertTrue(masked.startswith("# Title\n\n"))
        self.assertTrue(masked.endswith("\nEnd"))

    def test_mask_requires_same_char_and_at_least_n_length_to_close(self) -> None:
        raw = (
            "   ````md\n"
            "```\n"
            "~~~~\n"
            "```` not-closing\n"
            "## [Unreleased]\n"
            "  ````   \n"
            "## [0.0.11]\n"
        )
        masked = changelog_guard.mask_fenced_code_blocks(raw)
        self.assertEqual(len(masked), len(raw))
        self.assertNotIn("## [Unreleased]", masked)
        self.assertIn("## [0.0.11]", masked)

    def test_mask_ignores_four_space_indented_fence_and_handles_unclosed_eof(self) -> None:
        raw = (
            "    ```\n"
            "## [Unreleased]\n"
            "    ```\n"
            "~~~\n"
            "## [0.0.11]"
        )
        masked = changelog_guard.mask_fenced_code_blocks(raw)
        self.assertEqual(len(masked), len(raw))
        self.assertIn("## [Unreleased]", masked)
        self.assertNotIn("## [0.0.11]", masked)

    def test_archive_changelog_cli_preserves_fenced_blocks_and_blocks_real_duplicates(self) -> None:
        with tempfile.TemporaryDirectory(prefix="letsgo-changelog-guard-") as tmp:
            root = Path(tmp)
            changelog = root / "CHANGELOG.md"
            changelog.write_text(
                "# 变更日志（Changelog）\n\n"
                "## [Unreleased]\n\n"
                "- 新功能说明：\n\n"
                "```markdown\n"
                "## [Unreleased]\n\n"
                "## [0.0.11]\n"
                "```\n\n"
                "## [0.0.10] - 2026-11-24\n\n"
                "~~~md\n"
                "## [0.0.11]\n"
                "~~~\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "changelog_guard.py"),
                    "archive",
                    "0.0.11",
                    "--changelog",
                    str(changelog),
                    "--date",
                    "2026-11-25",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            updated = changelog.read_text(encoding="utf-8")
            self.assertIn("## [0.0.11] - 2026-11-25", updated)
            self.assertIn("```markdown\n## [Unreleased]\n\n## [0.0.11]\n```", updated)
            self.assertIn("~~~md\n## [0.0.11]\n~~~", updated)

            dup = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "changelog_guard.py"),
                    "archive",
                    "0.0.11",
                    "--changelog",
                    str(changelog),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(dup.returncode, 0)
            self.assertIn("已存在 ## [0.0.11] 节", dup.stderr)


if __name__ == "__main__":
    unittest.main()
