#!/usr/bin/env python3
"""Governance document validation and CHANGELOG archiving with fenced code block masking."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import sys

BARE_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
OPEN_FENCE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")
UNRELEASED_HEADING = re.compile(r"^## \[Unreleased\][ \t]*$", re.MULTILINE)
NEXT_VERSION_HEADING = re.compile(r"^## \[", re.MULTILINE)


def _mask_line(line: str) -> str:
    if line.endswith("\n"):
        return (" " * (len(line) - 1)) + "\n"
    return " " * len(line)


def mask_fenced_code_blocks(text: str) -> str:
    """Replace fenced code block lines (except trailing newline) with spaces of equal length."""
    normalized = text.replace("\r\n", "\n")
    fence_char: str | None = None
    fence_len = 0
    close_fence: re.Pattern[str] | None = None
    result: list[str] = []

    for line in normalized.splitlines(keepends=True):
        body = line[:-1] if line.endswith("\n") else line
        if fence_char is None:
            match = OPEN_FENCE.match(body)
            if match is not None:
                fence = match.group(1)
                fence_char = fence[0]
                fence_len = len(fence)
                close_fence = re.compile(rf"^[ \t]{{0,3}}{re.escape(fence_char)}{{{fence_len},}}[ \t]*$")
                result.append(_mask_line(line))
            else:
                result.append(line)
        else:
            result.append(_mask_line(line))
            if close_fence is not None and close_fence.match(body) is not None:
                fence_char = None
                fence_len = 0
                close_fence = None

    return "".join(result)


def _version_heading_pattern(version: str) -> re.Pattern[str]:
    return re.compile(rf"^## \[{re.escape(version)}\](?: - \d{{4}}-\d{{2}}-\d{{2}})?[ \t]*$", re.MULTILINE)


def validate_governance_docs(root: Path, version: str | None) -> list[str]:
    """Validate root CHANGELOG.md and docs/compatibility.md outside fenced code blocks."""
    errors: list[str] = []
    changelog = root / "CHANGELOG.md"
    if not changelog.is_file():
        errors.append("missing root CHANGELOG.md")
    else:
        text = changelog.read_text(encoding="utf-8").replace("\r\n", "\n")
        masked = mask_fenced_code_blocks(text)
        unreleased_matches = UNRELEASED_HEADING.findall(masked)
        if len(unreleased_matches) != 1:
            errors.append("CHANGELOG.md must contain exactly one '## [Unreleased]'")
        if isinstance(version, str) and BARE_VERSION.match(version):
            if not _version_heading_pattern(version).search(masked):
                errors.append(f"CHANGELOG.md must contain '## [{version}]' section")

    compat = root / "docs" / "compatibility.md"
    if not compat.is_file():
        errors.append("missing docs/compatibility.md")
    elif not compat.read_text(encoding="utf-8").strip():
        errors.append("docs/compatibility.md must not be empty")

    return errors


def archive_changelog(changelog_path: Path, version: str, release_date: str | None = None) -> None:
    """Archive the ## [Unreleased] section into ## [<version>] - YYYY-MM-DD."""
    if not BARE_VERSION.match(version):
        raise ValueError(f"版本号必须是无 v 前缀的裸 x.y.z 形式：{version}")
    if not changelog_path.is_file():
        raise ValueError("缺少根目录 CHANGELOG.md。")

    text = changelog_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    masked = mask_fenced_code_blocks(text)

    unreleased_matches = list(UNRELEASED_HEADING.finditer(masked))
    if len(unreleased_matches) != 1:
        raise ValueError("CHANGELOG.md 必须且仅能包含一个 ## [Unreleased] 节。")
    unreleased_match = unreleased_matches[0]

    if _version_heading_pattern(version).search(masked):
        raise ValueError(f"CHANGELOG.md 已存在 ## [{version}] 节。")

    next_match = NEXT_VERSION_HEADING.search(masked[unreleased_match.end():])
    section_end = unreleased_match.end() + next_match.start() if next_match else len(text)
    unreleased_body = text[unreleased_match.end():section_end].strip() or "- 版本号对齐（无行为变更）。"
    target_date = release_date or date.today().isoformat()

    prefix = text[:unreleased_match.start()]
    rest = text[section_end:].lstrip("\n")
    archived = f"## [Unreleased]\n\n## [{version}] - {target_date}\n\n{unreleased_body}\n"
    new_text = f"{prefix}{archived}\n{rest}" if rest else f"{prefix}{archived}"
    changelog_path.write_text(new_text, encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Governance doc checks and CHANGELOG archiving.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    archive_parser = subparsers.add_parser("archive", help="Archive ## [Unreleased] into a release section.")
    archive_parser.add_argument("version", help="Bare x.y.z release version.")
    archive_parser.add_argument(
        "--changelog",
        type=Path,
        default=Path("CHANGELOG.md"),
        help="Path to CHANGELOG.md (default: CHANGELOG.md).",
    )
    archive_parser.add_argument(
        "--date",
        default=None,
        help="Override release date in YYYY-MM-DD format.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "archive":
        try:
            archive_changelog(args.changelog, args.version, release_date=args.date)
        except (OSError, ValueError) as exc:
            sys.stderr.write(f"错误：{exc}\n")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
