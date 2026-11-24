#!/usr/bin/env python3
"""Structural validation for the letsgo plugin; release.sh refuses to publish when it fails."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

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
    "skill-walk",
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
)
# ADR-0017 废除的流程概念，不得重新进入插件包。
RETIRED_TERMS = (
    "任务流程", "流程阶段", "流程环节", "需求类型", "类型分组", "交付方式", "分类行", "技能登记表",
    "验证深度", "验证选定", "开始实施", "实施申请", "开工清障", "目标定位", "需求审议", "方案共定",
    "方案先行", "插件设计原则",
)
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
ANTIGRAVITY_FIELDS = {
    "name", "displayName", "description", "version", "author",
    "homepage", "repository", "logo", "suggestedPrompts", "disabled",
}


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}


def frontmatter(path: Path) -> dict:
    match = re.match(r"---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    data = yaml.safe_load(match.group(1)) if match else None
    return data if isinstance(data, dict) else {}


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
        if refs != [f"v{version}"]:
            errors.append(f"{market.relative_to(ROOT)} must pin letsgo to v{version}, found {refs}")


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
        fm = frontmatter(skill_md)
        if fm.get("name") != expected_name(skill):
            errors.append(f"{skill}: name must be {expected_name(skill)!r}, found {fm.get('name')!r}")
        if not fm.get("description"):
            errors.append(f"{skill}: missing description")
        meta_file = skill_md.parent / "agents" / "openai.yaml"
        meta = (yaml.safe_load(meta_file.read_text(encoding="utf-8")) if meta_file.is_file() else {}) or {}
        policy = meta.get("policy", {}).get("allow_implicit_invocation")
        if skill == RULES_SKILL:
            if "disable-model-invocation" in fm or fm.get("user-invocable") is not False or policy is not True:
                errors.append(f"{skill}: must be implicit and hidden (no disable-model-invocation, user-invocable: false, allow_implicit_invocation: true)")
        elif fm.get("disable-model-invocation") is not True or policy is not False:
            errors.append(f"{skill}: must be explicit-only (disable-model-invocation: true, allow_implicit_invocation: false)")
        display = meta.get("interface", {}).get("display_name", "")
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
            for target in LINK.findall(text):
                if "://" in target or target.startswith(("mailto:", "~")):
                    continue
                if not (path.parent / target).resolve().exists():
                    errors.append(f"broken link in {path.relative_to(ROOT)}: {target}")


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


def main() -> int:
    errors: list[str] = []
    check_manifests(errors)
    check_skills(errors)
    check_text(errors)
    check_no_hooks(errors)
    check_private_payload(errors)
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        return 1
    print("VALIDATION_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
