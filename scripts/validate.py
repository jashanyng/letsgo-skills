#!/usr/bin/env python3
"""Structural validation for the letsgo plugin; release.sh refuses to publish when it fails."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import changelog_guard
except ImportError:  # pragma: no cover
    from scripts import changelog_guard

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "letsgo"
SKILLS = PLUGIN / "skills"

# 唯一的隐式技能，承载基础规则、共用规则、用户级规则与私人资料流程。
RULES_SKILL = "letsgo"
EXPECTED_SKILLS = {
    RULES_SKILL,
    "stepping-begin",
    "stepping-doit",
    "stepping-finish",
    "write-an-article",
    "matt-flow",
    "prove-it",
    "guide",
    "try-swarm",
    "git-wrap",
}
EXPLICIT_ROUTES = ("../letsgo/references/language.md",)
MATT_ROUTES = (
    "../letsgo/references/language.md",
    "../letsgo/references/matt-route.md",
)
STEPPING_ROUTES = (
    "../letsgo/references/language.md",
    "../letsgo/references/stepping/workflow.md",
    "../letsgo/references/stepping/instruction-format.md",
)
# Paths and names that existed before the plugin migration and must not come back.
LEGACY_PATTERNS = (
    re.compile(r"~/\.agents/contexts"),
    re.compile(r"\.agents/datum|\"datum\""),
    re.compile(r"\bletsgo-(?!skills\b)[a-z]+(?:-[a-z]+)*"),
    re.compile(r"tool-parity|routing-contract|common-rules\.md|terminology\.md"),
    re.compile(r"_rules/|skills-codex|letsgo:personal|letsgo:conventions"),
    re.compile(r"letsgo:skill-walk|grill-gate\.md"),
)
# ADR-0017 废除的流程概念，不得重新进入插件包。
RETIRED_TERMS = (
    "任务流程", "流程阶段", "流程环节", "需求类型", "类型分组", "交付方式", "分类行", "技能登记表",
    "验证深度", "验证选定", "开始实施", "实施申请", "开工清障", "目标定位", "需求审议", "方案共定",
    "方案先行", "插件设计原则",
)
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
INLINE_CODE = re.compile(r"(`+)(?!`)(.*?)(?<!`)\1(?!`)")
REQUIRED_REPO_DOCS = ("README.md", "AGENTS.md", "GLOSSARY.md", "CHANGELOG.md")
SKILL_DOC_FILES = ("README.md", "docs/authoring.md", "docs/compatibility.md", "GLOSSARY.md")
SKILL_MENTION_PATTERNS = tuple(
    (skill, re.compile(rf"(?<![A-Za-z0-9_:-]){re.escape(skill)}(?![A-Za-z0-9_:-])"))
    for skill in sorted(EXPECTED_SKILLS)
)
ANTIGRAVITY_FIELDS = {
    "name", "displayName", "description", "version", "author",
    "homepage", "repository", "logo", "suggestedPrompts", "disabled",
}
BARE_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}


def _parse_double_quoted(raw: str, lineno: int) -> tuple[str, int]:
    idx = 1
    while idx < len(raw):
        ch = raw[idx]
        if ch == "\\":
            if idx + 1 >= len(raw):
                raise ValueError(f"line {lineno}: unterminated escape in double-quoted string")
            idx += 2
            continue
        if ch == '"':
            literal = raw[: idx + 1]
            try:
                value = json.loads(literal)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {lineno}: invalid double-quoted string: {exc}") from exc
            return value, idx
        idx += 1
    raise ValueError(f"line {lineno}: unterminated double-quoted string")


def _parse_single_quoted(raw: str, lineno: int) -> tuple[str, int]:
    chars: list[str] = []
    idx = 1
    while idx < len(raw):
        ch = raw[idx]
        if ch == "'":
            if idx + 1 < len(raw) and raw[idx + 1] == "'":
                chars.append("'")
                idx += 2
                continue
            return "".join(chars), idx
        chars.append(ch)
        idx += 1
    raise ValueError(f"line {lineno}: unterminated single-quoted string")


def _check_trailing_comment(trailing: str, lineno: int) -> None:
    if trailing.strip(" \t") == "":
        return
    if re.match(r"^[ \t]+#", trailing):
        return
    raise ValueError(f"line {lineno}: unexpected trailing characters after quoted string")


def _split_key_value(content: str, lineno: int) -> tuple[str, str]:
    if content[0] in ('"', "'"):
        parser = _parse_double_quoted if content[0] == '"' else _parse_single_quoted
        key, end_idx = parser(content, lineno)
        rest = content[end_idx + 1 :].lstrip(" \t")
        if not rest.startswith(":") or (len(rest) > 1 and rest[1] not in (" ", "\t")):
            raise ValueError(f"line {lineno}: expected ':' after quoted key")
        return key, rest[1:].lstrip(" \t")

    colon_idx = -1
    for idx, ch in enumerate(content):
        if ch == "#" and idx > 0 and content[idx - 1] in (" ", "\t"):
            break
        if ch == ":" and (idx + 1 == len(content) or content[idx + 1] in (" ", "\t")):
            colon_idx = idx
            break
    if colon_idx <= 0:
        raise ValueError(f"line {lineno}: expected 'key: value' mapping entry")
    key = content[:colon_idx].rstrip(" \t")
    raw_val = content[colon_idx + 1 :].lstrip(" \t")
    return key, raw_val


def _parse_block_scalar(lines: list[str], start_idx: int, key_indent: int, header: str) -> tuple[str, int]:
    match = re.match(r"^([|>])(-?)(?:[ \t]+(?:#.*)?)?$", header)
    if not match:
        raise ValueError(f"line {start_idx}: invalid block scalar header {header!r}")
    style, chomp = match.group(1), match.group(2)

    block_indent: int | None = None
    raw_lines: list[str] = []
    idx = start_idx

    while idx < len(lines):
        line = lines[idx]
        if line.strip(" \t") == "":
            if "\t" in (line if block_indent is None else line[:block_indent]):
                raise ValueError(f"line {idx + 1}: tab indentation is not allowed")
            if block_indent is not None and len(line) > block_indent:
                raw_lines.append(line[block_indent:])
            else:
                raw_lines.append("")
            idx += 1
            continue

        leading = line[: len(line) - len(line.lstrip(" \t"))]
        indent = len(leading)
        if block_indent is None:
            if "\t" in leading:
                raise ValueError(f"line {idx + 1}: tab indentation is not allowed")
            if indent <= key_indent:
                break
            block_indent = indent
        else:
            if indent < block_indent:
                if "\t" in leading:
                    raise ValueError(f"line {idx + 1}: tab indentation is not allowed")
                if indent <= key_indent:
                    break
                raise ValueError(f"line {idx + 1}: misaligned indentation inside block scalar")
            if "\t" in line[:block_indent]:
                raise ValueError(f"line {idx + 1}: tab indentation is not allowed")

        raw_lines.append(line[block_indent:])
        idx += 1

    while raw_lines and raw_lines[-1] == "":
        raw_lines.pop()
    if not raw_lines:
        return "", idx

    if style == "|":
        body = "\n".join(raw_lines)
    else:
        parts: list[str] = []
        for pos, rline in enumerate(raw_lines):
            if rline == "":
                parts.append("\n")
                continue
            parts.append(rline)
            if pos + 1 < len(raw_lines):
                nxt = raw_lines[pos + 1]
                if nxt == "":
                    if rline.startswith(" "):
                        parts.append("\n")
                elif rline.startswith(" ") or nxt.startswith(" "):
                    parts.append("\n")
                else:
                    parts.append(" ")
        body = "".join(parts)

    return (body if chomp == "-" else body + "\n"), idx


def _parse_inline_scalar(raw_val: str, lineno: int) -> object:
    if raw_val.startswith('"'):
        value, end_idx = _parse_double_quoted(raw_val, lineno)
        _check_trailing_comment(raw_val[end_idx + 1 :], lineno)
        return value
    if raw_val.startswith("'"):
        value, end_idx = _parse_single_quoted(raw_val, lineno)
        _check_trailing_comment(raw_val[end_idx + 1 :], lineno)
        return value

    comment_match = re.search(r"[ \t]+#", raw_val)
    scalar = (raw_val[: comment_match.start()] if comment_match else raw_val).rstrip(" \t")
    if scalar == "true":
        return True
    if scalar == "false":
        return False
    if scalar in {"null", "~"}:
        return None
    if scalar == "{}":
        return {}
    if scalar == "[]":
        return []
    return scalar


def _pop_stack_to(stack: list[tuple[int, dict]], indent: int, lineno: int) -> None:
    while len(stack) > 1 and stack[-1][0] > indent:
        stack.pop()
    if stack[-1][0] != indent:
        raise ValueError(f"line {lineno}: misaligned indentation")


def parse_simple_yaml(text: str) -> dict:
    """Parse the restricted YAML subset used by SKILL.md frontmatter and agents/openai.yaml."""
    normalized = text.replace("\r\n", "\n")
    lines = normalized.split("\n")
    root: dict = {}
    stack: list[tuple[int, dict]] = [(0, root)]
    pending: tuple[dict, str, int] | None = None

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        lineno = idx + 1
        leading = line[: len(line) - len(line.lstrip(" \t"))]
        if "\t" in leading:
            raise ValueError(f"line {lineno}: tab indentation is not allowed")

        stripped = line.lstrip(" ")
        if stripped == "" or stripped.startswith("#"):
            idx += 1
            continue

        indent = len(leading)
        if pending is not None:
            parent_dict, pending_key, key_indent = pending
            pending = None
            if indent > key_indent:
                child: dict = {}
                parent_dict[pending_key] = child
                stack.append((indent, child))
            else:
                _pop_stack_to(stack, indent, lineno)
        elif indent > stack[-1][0]:
            raise ValueError(f"line {lineno}: unexpected indentation")
        elif indent < stack[-1][0]:
            _pop_stack_to(stack, indent, lineno)

        current_map = stack[-1][1]
        key, raw_val = _split_key_value(stripped, lineno)
        idx += 1

        if raw_val == "" or raw_val.startswith("#"):
            current_map[key] = None
            pending = (current_map, key, indent)
            continue

        if raw_val.startswith(("|", ">")):
            block_value, idx = _parse_block_scalar(lines, idx, indent, raw_val)
            current_map[key] = block_value
            continue

        current_map[key] = _parse_inline_scalar(raw_val, lineno)

    return root


def frontmatter(path: Path, errors: list[str] | None = None) -> dict:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    match = re.match(r"^---[ \t]*\n(.*?)\n---[ \t]*(?:\n|$)", text, re.S)
    if not match:
        return {}
    try:
        return parse_simple_yaml(match.group(1))
    except ValueError as exc:
        if errors is not None:
            errors.append(f"invalid YAML frontmatter in {path}: {exc}")
        return {}


def load_yaml_file(path: Path, errors: list[str]) -> dict:
    if not path.is_file():
        return {}
    try:
        return parse_simple_yaml(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"invalid YAML {path}: {exc}")
        return {}


def expected_name(skill: str) -> str:
    # Codex 总在 name 前加插件名，Antigravity 从不加；name 带 letsgo: 使 Claude Code 与 Antigravity 都显示 letsgo:<名称>。
    return RULES_SKILL if skill == RULES_SKILL else f"letsgo:{skill}"


def expected_display(skill: str) -> str:
    return RULES_SKILL if skill == RULES_SKILL else f"letsgo: {skill.replace('-', ' ')}"


def check_manifests(errors: list[str]) -> None:
    claude = load_json(PLUGIN / ".claude-plugin" / "plugin.json", errors)
    codex = load_json(PLUGIN / ".codex-plugin" / "plugin.json", errors)
    antigravity = load_json(PLUGIN / ".antigravity-plugin" / "plugin.json", errors)
    version = claude.get("version")
    if version != codex.get("version") or version != antigravity.get("version"):
        errors.append(
            f"plugin versions differ: claude={version} codex={codex.get('version')} antigravity={antigravity.get('version')}"
        )
    if not isinstance(version, str) or not BARE_VERSION.match(version):
        errors.append(f"plugin version must be bare x.y.z (no 'v' prefix), found {version!r}")
    for name, data in (("claude", claude), ("codex", codex), ("antigravity", antigravity)):
        if data.get("name") != "letsgo":
            errors.append(f"{name} plugin name must be letsgo")
    unknown = sorted(set(antigravity) - ANTIGRAVITY_FIELDS)
    if unknown:
        errors.append(f"antigravity plugin.json has unsupported fields: {unknown}")
    if codex.get("skills") != "./skills/":
        errors.append(f"codex plugin.json skills must be ./skills/, found {codex.get('skills')}")
    listed = {Path(p).name for p in claude.get("skills", [])}
    actual = {p.parent.name for p in SKILLS.glob("*/SKILL.md")}
    if listed != actual:
        errors.append(f"claude plugin.json skills {sorted(listed)} != skill dirs {sorted(actual)}")
    for market in (ROOT / ".claude-plugin" / "marketplace.json", ROOT / ".agents" / "plugins" / "marketplace.json"):
        data = load_json(market, errors)
        refs = [p["source"].get("ref") for p in data.get("plugins", []) if p.get("name") == "letsgo"]
        if refs != [version]:
            errors.append(f"{market.relative_to(ROOT)} must pin letsgo to {version}, found {refs}")


def _mapping_section(meta: dict, section: str, skill: str, errors: list[str]) -> dict:
    raw = meta.get(section)
    if raw is not None and not isinstance(raw, dict):
        errors.append(f"{skill}: openai.yaml {section} must be a mapping")
        return {}
    return raw or {}


def check_skills(errors: list[str]) -> None:
    for retired in ("skills-codex", "skills/_rules"):
        if (PLUGIN / retired).exists():
            errors.append(f"retired directory must not exist: plugins/letsgo/{retired}")
    dirs = {p.name for p in SKILLS.iterdir() if p.is_dir()}
    if dirs != EXPECTED_SKILLS:
        errors.append(f"skills must be exactly {sorted(EXPECTED_SKILLS)}, found {sorted(dirs)}")
    for path in SKILLS.rglob("*"):
        rel = path.relative_to(SKILLS).parts
        allowed = (path.name == "SKILL.md" and len(rel) == 2) or (rel[1:] == ("agents", "openai.yaml"))
        if path.name in {"SKILL.md", "openai.yaml"} and not allowed:
            errors.append(f"nested discoverable metadata: {path.relative_to(ROOT)}")
    for skill_md in sorted(SKILLS.glob("*/SKILL.md")):
        skill = skill_md.parent.name
        fm = frontmatter(skill_md, errors)
        if fm.get("name") != expected_name(skill):
            errors.append(f"{skill}: name must be {expected_name(skill)!r}, found {fm.get('name')!r}")
        if not fm.get("description"):
            errors.append(f"{skill}: missing description")
        meta_file = skill_md.parent / "agents" / "openai.yaml"
        meta = load_yaml_file(meta_file, errors)
        policy = _mapping_section(meta, "policy", skill, errors).get("allow_implicit_invocation")
        if skill == RULES_SKILL:
            if "disable-model-invocation" in fm or fm.get("user-invocable") is not False or policy is not True:
                errors.append(f"{skill}: must be implicit and hidden (no disable-model-invocation, user-invocable: false, allow_implicit_invocation: true)")
        elif fm.get("disable-model-invocation") is not True or policy is not False:
            errors.append(f"{skill}: must be explicit-only (disable-model-invocation: true, allow_implicit_invocation: false)")
        display = _mapping_section(meta, "interface", skill, errors).get("display_name", "")
        if display != expected_display(skill):
            errors.append(f"{skill}: display_name must be {expected_display(skill)!r}, found {display!r}")
        links = set(LINK.findall(skill_md.read_text(encoding="utf-8")))
        if skill == RULES_SKILL:
            routes = ("references/language.md",)
        elif skill.startswith("stepping-"):
            routes = STEPPING_ROUTES
        elif skill == "matt-flow":
            routes = MATT_ROUTES
        else:
            routes = EXPLICIT_ROUTES
        for route in routes:
            if route not in links:
                errors.append(f"{skill}: missing route {route}")


def check_markdown_links(path: Path, errors: list[str], text: str | None = None) -> None:
    content = path.read_text(encoding="utf-8") if text is None else text
    masked = changelog_guard.mask_fenced_code_blocks(content)
    masked = INLINE_CODE.sub("", masked)
    for target in LINK.findall(masked):
        if "://" in target or target.startswith(("mailto:", "tel:", "~")):
            continue
        if not (path.parent / target).resolve().exists():
            errors.append(f"broken link in {path.relative_to(ROOT)}: {target}")


def check_text(errors: list[str]) -> None:
    for path in sorted(SKILLS.rglob("*")):
        if path.is_symlink():
            errors.append(f"symlink in plugin payload (Codex ignores symlinks): {path.relative_to(ROOT)}")
            continue
        if not path.is_file() or path.suffix not in {".md", ".yaml", ".py", ".sh"}:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in LEGACY_PATTERNS:
            for match in pattern.finditer(text):
                errors.append(f"legacy reference in {path.relative_to(ROOT)}: {match.group(0)}")
        for term in RETIRED_TERMS:
            if term in text:
                errors.append(f"retired process term in {path.relative_to(ROOT)}: {term}")
        if path.suffix == ".md":
            check_markdown_links(path, errors, text=text)


def check_repo_docs(errors: list[str]) -> None:
    for rel in REQUIRED_REPO_DOCS:
        doc_path = ROOT / rel
        if not doc_path.is_file():
            errors.append(f"missing repo doc: {rel}")
        else:
            check_markdown_links(doc_path, errors)
    docs_dir = ROOT / "docs"
    if docs_dir.is_dir():
        for doc_path in sorted(docs_dir.rglob("*.md")):
            check_markdown_links(doc_path, errors)
    for rel in SKILL_DOC_FILES:
        doc_path = ROOT / rel
        if not doc_path.is_file():
            continue
        text = doc_path.read_text(encoding="utf-8")
        missing = [skill for skill, pattern in SKILL_MENTION_PATTERNS if not pattern.search(text)]
        if missing:
            errors.append(f"{rel} is missing expected skills: {missing}")


def check_no_hooks(errors: list[str]) -> None:
    """项目硬性规定：插件任何功能都不得用事件钩子实现。"""
    if (PLUGIN / "hooks").exists():
        errors.append("plugin must not contain hooks/: implement behaviour with skills")
    if (PLUGIN / "rules").exists():
        errors.append("plugin must not contain rules/: use the letsgo skill across all three hosts")
    for path in PLUGIN.rglob("*.json"):
        if path.name.startswith("hooks") or path.name.endswith("hooks.json"):
            errors.append(f"plugin must not ship hook configuration: {path.relative_to(ROOT)}")
    for manifest in (
        PLUGIN / ".claude-plugin" / "plugin.json",
        PLUGIN / ".codex-plugin" / "plugin.json",
        PLUGIN / ".antigravity-plugin" / "plugin.json",
    ):
        if "hooks" in load_json(manifest, errors):
            errors.append(f"{manifest.relative_to(ROOT)} must not declare hooks")
    for skill_md in SKILLS.glob("*/SKILL.md"):
        if "hooks" in frontmatter(skill_md):
            errors.append(f"{skill_md.relative_to(ROOT)} must not declare hooks")


def check_private_payload(errors: list[str]) -> None:
    forbidden = (
        "/Users/", "~/.agents/generated", "~/project/letsgo-skills", "本机快照", "候选快照",
        "generated/backups", "generated/tmp", "~/data/", "letsgo:setup",
    )
    for path in PLUGIN.rglob("*"):
        if path.name in {".DS_Store", "__pycache__"} or path.suffix == ".pyc":
            errors.append(f"unwanted file in plugin payload: {path.relative_to(ROOT)}")
            continue
        if not path.is_file() or path.suffix not in {".md", ".sh", ".py", ".json", ".yaml"}:
            continue
        content = path.read_text(encoding="utf-8")
        for needle in forbidden:
            if needle in content:
                errors.append(f"private or retired runtime reference in {path.relative_to(ROOT)}")
                break


def check_governance_docs(errors: list[str]) -> None:
    version: str | None = None
    claude_path = PLUGIN / ".claude-plugin" / "plugin.json"
    if claude_path.is_file():
        try:
            raw_version = json.loads(claude_path.read_text(encoding="utf-8")).get("version")
        except (OSError, json.JSONDecodeError):
            raw_version = None
        if isinstance(raw_version, str) and BARE_VERSION.match(raw_version):
            version = raw_version
    errors.extend(changelog_guard.validate_governance_docs(ROOT, version))


def main() -> int:
    errors: list[str] = []
    check_manifests(errors)
    check_skills(errors)
    check_text(errors)
    check_no_hooks(errors)
    check_private_payload(errors)
    check_governance_docs(errors)
    check_repo_docs(errors)
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        return 1
    print("VALIDATION_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
