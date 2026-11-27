"""在隔离副本中验证插件校验门。"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import validate  # noqa: E402

SKILLS = "plugins/letsgo/skills"


class PluginValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="letsgo-validator-test-")
        self.addCleanup(self.temp.cleanup)
        self.fixture = Path(self.temp.name)
        for name in ("plugins", "scripts", "docs", ".agents", ".claude-plugin"):
            shutil.copytree(
                ROOT / name,
                self.fixture / name,
                symlinks=True,
                ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", "*.pyc"),
            )
        for name in ("GLOSSARY.md", "README.md", "AGENTS.md", "CHANGELOG.md"):
            shutil.copy2(ROOT / name, self.fixture / name)

    def run_validation(self) -> list[str]:
        return validate.validate_repo(self.fixture)

    def run_cli_validate(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/validate.py"], cwd=self.fixture, text=True, capture_output=True, check=False
        )

    def assertRejected(self, message: str) -> None:
        errors = self.run_validation()
        self.assertTrue(errors, f"expected validation error containing {message!r}, but passed")
        self.assertIn(message, "\n".join(errors))

    def edit(self, relative: str, old: str, new: str) -> None:
        path = self.fixture / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def replace_all(self, relative: str, old: str, new: str) -> None:
        path = self.fixture / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def append(self, relative: str, text: str) -> None:
        with (self.fixture / relative).open("a", encoding="utf-8") as stream:
            stream.write(text)

    def test_valid_plugin_passes(self) -> None:
        self.assertEqual(self.run_validation(), [])

    def test_cli_entrypoint_reports_ok_and_errors(self) -> None:
        ok_res = self.run_cli_validate()
        self.assertEqual(ok_res.returncode, 0, ok_res.stdout + ok_res.stderr)
        self.assertEqual(ok_res.stdout.strip(), "VALIDATION_OK")

        self.append(f"{SKILLS}/letsgo/SKILL.md", "\n[缺失](references/missing.md)\n")
        err_res = self.run_cli_validate()
        self.assertNotEqual(err_res.returncode, 0)
        self.assertIn("ERROR: broken link", err_res.stdout)

    def test_unexpected_skill_is_rejected(self) -> None:
        shutil.copytree(self.fixture / SKILLS / "stepping-doit", self.fixture / SKILLS / "tell-me")
        self.assertRejected("skills must be exactly")

    def test_codex_copy_directory_is_rejected(self) -> None:
        shutil.copytree(self.fixture / SKILLS, self.fixture / "plugins/letsgo/skills-codex")
        self.assertRejected("retired directory must not exist: plugins/letsgo/skills-codex")

    def test_skill_name_prefix_is_checked(self) -> None:
        self.edit(f"{SKILLS}/stepping-begin/SKILL.md", 'name: "letsgo:stepping-begin"', "name: stepping-begin")
        self.assertRejected("name must be 'letsgo:stepping-begin'")

    def test_implicit_invocation_is_rejected(self) -> None:
        self.edit(f"{SKILLS}/stepping-doit/agents/openai.yaml", "allow_implicit_invocation: false", "allow_implicit_invocation: true")
        self.assertRejected("explicit-only")

    def test_rules_skill_must_stay_hidden_from_slash_menu(self) -> None:
        self.edit(f"{SKILLS}/letsgo/SKILL.md", "user-invocable: false\n", "")
        self.assertRejected("must be implicit and hidden")

    def test_display_name_is_checked(self) -> None:
        self.edit(f"{SKILLS}/stepping-finish/agents/openai.yaml", 'display_name: "letsgo: stepping finish"', 'display_name: "finish"')
        self.assertRejected("display_name must be 'letsgo: stepping finish'")

    def test_nested_skill_cannot_appear_in_menu(self) -> None:
        (self.fixture / SKILLS / "letsgo/references/SKILL.md").write_text("---\nname: hidden\ndescription: hidden\n---\n")
        self.assertRejected("nested discoverable metadata")

    def test_stepping_must_link_workflow(self) -> None:
        self.replace_all(f"{SKILLS}/stepping-begin/SKILL.md", "(../letsgo/references/stepping/workflow.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("missing route ../letsgo/references/stepping/workflow.md")

    def test_article_skill_must_link_language(self) -> None:
        self.replace_all(f"{SKILLS}/write-an-article/SKILL.md", "(../letsgo/references/language.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("write-an-article: missing route ../letsgo/references/language.md")

    def test_article_skill_must_be_explicit(self) -> None:
        self.edit(f"{SKILLS}/write-an-article/SKILL.md", "disable-model-invocation: true\n", "")
        self.assertRejected("write-an-article: must be explicit-only")

    def test_matt_flow_skill_must_link_matt_route(self) -> None:
        self.replace_all(f"{SKILLS}/matt-flow/SKILL.md", "(../letsgo/references/matt-route.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("matt-flow: missing route ../letsgo/references/matt-route.md")

    def test_matt_flow_skill_must_link_orchestration(self) -> None:
        self.replace_all(f"{SKILLS}/matt-flow/SKILL.md", "(../letsgo/references/orchestration.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("matt-flow: missing route ../letsgo/references/orchestration.md")

    def test_prove_it_skill_must_link_language(self) -> None:
        self.replace_all(f"{SKILLS}/prove-it/SKILL.md", "(../letsgo/references/language.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("prove-it: missing route ../letsgo/references/language.md")

    def test_prove_it_skill_must_be_explicit(self) -> None:
        self.edit(f"{SKILLS}/prove-it/SKILL.md", "disable-model-invocation: true\n", "")
        self.assertRejected("prove-it: must be explicit-only")

    def test_guide_skill_must_link_language(self) -> None:
        self.replace_all(f"{SKILLS}/guide/SKILL.md", "(../letsgo/references/language.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("guide: missing route ../letsgo/references/language.md")

    def test_guide_skill_must_be_explicit(self) -> None:
        self.edit(f"{SKILLS}/guide/SKILL.md", "disable-model-invocation: true\n", "")
        self.assertRejected("guide: must be explicit-only")

    def test_try_swarm_skill_must_link_language(self) -> None:
        self.replace_all(f"{SKILLS}/try-swarm/SKILL.md", "(../letsgo/references/language.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("try-swarm: missing route ../letsgo/references/language.md")

    def test_try_swarm_skill_must_link_orchestration(self) -> None:
        self.replace_all(f"{SKILLS}/try-swarm/SKILL.md", "(../letsgo/references/orchestration.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("try-swarm: missing route ../letsgo/references/orchestration.md")

    def test_try_swarm_skill_must_be_explicit(self) -> None:
        self.edit(f"{SKILLS}/try-swarm/SKILL.md", "disable-model-invocation: true\n", "")
        self.assertRejected("try-swarm: must be explicit-only")

    def test_git_wrap_skill_must_link_language(self) -> None:
        self.replace_all(f"{SKILLS}/git-wrap/SKILL.md", "(../letsgo/references/language.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("git-wrap: missing route ../letsgo/references/language.md")

    def test_git_wrap_skill_must_be_explicit(self) -> None:
        self.edit(f"{SKILLS}/git-wrap/SKILL.md", "disable-model-invocation: true\n", "")
        self.assertRejected("git-wrap: must be explicit-only")

    def test_broken_link_is_rejected(self) -> None:
        self.append(f"{SKILLS}/letsgo/SKILL.md", "\n[缺失](references/missing.md)\n")
        self.assertRejected("broken link")

    def test_retired_process_term_is_rejected(self) -> None:
        self.append(f"{SKILLS}/letsgo/references/output.md", "\n按任务流程处理。\n")
        self.assertRejected("retired process term")

    def test_old_skill_reference_is_rejected(self) -> None:
        self.append(f"{SKILLS}/letsgo/references/personal-context.md", "\n请调用 letsgo:personal。\n")
        self.assertRejected("legacy reference")

    def test_legacy_skill_walk_reference_is_rejected(self) -> None:
        self.append(f"{SKILLS}/letsgo/references/personal-context.md", "\n请调用 letsgo:skill-walk。\n")
        self.assertRejected(f"legacy reference in {SKILLS}/letsgo/references/personal-context.md: letsgo:skill-walk")

    def test_legacy_grill_gate_reference_is_rejected(self) -> None:
        self.append(f"{SKILLS}/letsgo/references/output.md", "\n详见 grill-gate.md。\n")
        self.assertRejected(f"legacy reference in {SKILLS}/letsgo/references/output.md: grill-gate.md")

    def test_private_absolute_home_path_is_rejected(self) -> None:
        self.append(f"{SKILLS}/letsgo/SKILL.md", "\n/Users/example/private-context\n")
        self.assertRejected("private or retired runtime reference")

    def test_plugin_hooks_are_rejected(self) -> None:
        hooks = self.fixture / "plugins/letsgo/hooks"
        hooks.mkdir()
        (hooks / "hooks.json").write_text('{"hooks": {}}', encoding="utf-8")
        self.assertRejected("plugin must not contain hooks/")

    def test_manifest_and_skill_hooks_are_rejected(self) -> None:
        manifest = self.fixture / "plugins/letsgo/.codex-plugin/plugin.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["hooks"] = "./hooks.json"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        self.edit(f"{SKILLS}/stepping-doit/SKILL.md", "---\n", "---\nhooks: {}\n")
        errors = "\n".join(self.run_validation())
        self.assertIn("plugin.json must not declare hooks", errors)
        self.assertIn("SKILL.md must not declare hooks", errors)

    def test_system_metadata_cannot_enter_plugin_payload(self) -> None:
        (self.fixture / SKILLS / "letsgo/.DS_Store").write_bytes(b"junk")
        self.assertRejected("unwanted file in plugin payload")

    def test_antigravity_manifest_version_and_fields_are_checked(self) -> None:
        manifest = self.fixture / "plugins/letsgo/.antigravity-plugin/plugin.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["version"] = "9.9.9"
        data["skills"] = "./skills/"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        errors = "\n".join(self.run_validation())
        self.assertIn("plugin versions differ", errors)
        self.assertIn("unsupported fields", errors)

    def test_codex_manifest_must_read_skills(self) -> None:
        self.edit("plugins/letsgo/.codex-plugin/plugin.json", '"./skills/"', '"./skills-codex/"')
        self.assertRejected("codex plugin.json skills must be ./skills/")

    def test_marketplace_ref_rejects_v_prefix(self) -> None:
        version = json.loads(
            (self.fixture / "plugins/letsgo/.claude-plugin/plugin.json").read_text(encoding="utf-8")
        )["version"]
        for relative in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
            path = self.fixture / relative
            data = json.loads(path.read_text(encoding="utf-8"))
            for plugin in data["plugins"]:
                if plugin["name"] == "letsgo":
                    plugin["source"]["ref"] = f"v{version}"
            path.write_text(json.dumps(data), encoding="utf-8")
        self.assertRejected(f"must pin letsgo to {version}")

    def test_manifest_version_rejects_v_prefix(self) -> None:
        for relative in (
            "plugins/letsgo/.claude-plugin/plugin.json",
            "plugins/letsgo/.codex-plugin/plugin.json",
            "plugins/letsgo/.antigravity-plugin/plugin.json",
        ):
            path = self.fixture / relative
            data = json.loads(path.read_text(encoding="utf-8"))
            data["version"] = "v0.0.10"
            path.write_text(json.dumps(data), encoding="utf-8")
        for relative in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
            path = self.fixture / relative
            data = json.loads(path.read_text(encoding="utf-8"))
            for plugin in data["plugins"]:
                if plugin["name"] == "letsgo":
                    plugin["source"]["ref"] = "v0.0.10"
            path.write_text(json.dumps(data), encoding="utf-8")
        self.assertRejected("plugin version must be bare x.y.z")

    def test_missing_changelog_is_rejected(self) -> None:
        (self.fixture / "CHANGELOG.md").unlink()
        self.assertRejected("CHANGELOG.md")

    def test_changelog_missing_unreleased_is_rejected(self) -> None:
        self.edit("CHANGELOG.md", "## [Unreleased]\n", "")
        self.assertRejected("## [Unreleased]")

    def test_changelog_missing_current_version_is_rejected(self) -> None:
        version = json.loads(
            (self.fixture / "plugins/letsgo/.claude-plugin/plugin.json").read_text(encoding="utf-8")
        )["version"]
        self.edit("CHANGELOG.md", f"## [{version}]", "## [0.0.0]")
        self.assertRejected(f"## [{version}]")

    def test_missing_or_empty_compatibility_doc_is_rejected(self) -> None:
        compat = self.fixture / "docs" / "compatibility.md"
        compat.unlink()
        self.assertRejected("docs/compatibility.md")

        compat.write_text("   \n\n", encoding="utf-8")
        self.assertRejected("docs/compatibility.md")

    def test_changelog_ignores_fenced_code_block_headings(self) -> None:
        version = json.loads(
            (self.fixture / "plugins/letsgo/.claude-plugin/plugin.json").read_text(encoding="utf-8")
        )["version"]
        self.append(
            "CHANGELOG.md",
            "\n### 示例说明\n\n"
            "```markdown\n"
            "## [Unreleased]\n\n"
            "## [0.0.11]\n"
            "```\n\n"
            "~~~\n"
            "## [Unreleased]\n"
            f"## [{version}]\n"
            "~~~\n",
        )
        self.assertEqual(self.run_validation(), [])

    def test_changelog_fenced_version_heading_does_not_satisfy_required_version(self) -> None:
        version = json.loads(
            (self.fixture / "plugins/letsgo/.claude-plugin/plugin.json").read_text(encoding="utf-8")
        )["version"]
        (self.fixture / "CHANGELOG.md").write_text(
            "# 变更日志（Changelog）\n\n"
            "## [Unreleased]\n\n"
            "```markdown\n"
            f"## [{version}]\n"
            "```\n",
            encoding="utf-8",
        )
        self.assertRejected(f"## [{version}]")

    def test_repo_doc_broken_link_is_rejected(self) -> None:
        targets = (
            ("README.md", "missing-readme.md"),
            ("AGENTS.md", "missing-agents.md"),
            ("GLOSSARY.md", "missing-glossary.md"),
            ("CHANGELOG.md", "missing-changelog.md"),
            ("docs/authoring.md", "missing-authoring.md"),
            ("docs/adr/0028-guide-skill-and-rules-update.md", "missing-adr.md"),
        )
        for rel, missing in targets:
            with self.subTest(doc=rel):
                path = self.fixture / rel
                original = path.read_text(encoding="utf-8")
                try:
                    path.write_text(f"{original}\n[断链]({missing})\n", encoding="utf-8")
                    self.assertRejected(f"broken link in {rel}: {missing}")
                finally:
                    path.write_text(original, encoding="utf-8")

    def test_repo_doc_ignores_links_in_fenced_and_inline_code(self) -> None:
        snippet = (
            "\n```markdown\n"
            "[围栏断链1](missing-fenced-1.md)\n"
            "```\n\n"
            "~~~\n"
            "[围栏断链2](missing-fenced-2.md)\n"
            "~~~\n\n"
            "行内示例 `[示例](missing.md)` 与 ``[双反引号示例](missing-inline.md)``。\n"
        )
        self.append("README.md", snippet)
        self.append("docs/authoring.md", snippet)
        self.assertEqual(self.run_validation(), [])

    def test_missing_required_repo_doc_is_rejected(self) -> None:
        for rel in ("AGENTS.md", "GLOSSARY.md"):
            with self.subTest(missing=rel):
                path = self.fixture / rel
                original = path.read_text(encoding="utf-8")
                try:
                    path.unlink()
                    self.assertRejected(f"missing repo doc: {rel}")
                finally:
                    path.write_text(original, encoding="utf-8")

    def test_skill_docs_must_mention_all_expected_skills(self) -> None:
        for rel in ("README.md", "docs/authoring.md", "docs/compatibility.md", "GLOSSARY.md"):
            with self.subTest(doc=rel):
                path = self.fixture / rel
                original = path.read_text(encoding="utf-8")
                updated = re.sub(r"(?<![A-Za-z0-9_:-])guide(?![A-Za-z0-9_:-])", "removed-item", original)
                self.assertNotEqual(updated, original)
                try:
                    path.write_text(updated, encoding="utf-8")
                    errors = "\n".join(self.run_validation())
                    self.assertIn(f"{rel} is missing expected skills:", errors)
                    self.assertIn("'guide'", errors)
                finally:
                    path.write_text(original, encoding="utf-8")

    def test_skill_doc_letsgo_check_ignores_repo_name_and_prefixed_commands(self) -> None:
        path = self.fixture / "GLOSSARY.md"
        original = path.read_text(encoding="utf-8")
        updated = re.sub(r"(?<![A-Za-z0-9_:-])letsgo(?![A-Za-z0-9_:-])", "other", original)
        updated += "\n示例命令：/letsgo:guide\n"
        self.assertIn("letsgo-skills", updated)
        self.assertIn("/letsgo:guide", updated)
        path.write_text(updated, encoding="utf-8")
        self.assertRejected("GLOSSARY.md is missing expected skills: ['letsgo']")

    def test_adr_must_start_with_h1_heading(self) -> None:
        adr = self.fixture / "docs/adr/0020-matt-flow-skill.md"
        original = adr.read_text(encoding="utf-8")
        adr.write_text(f"> 状态：前置注记。\n\n{original}", encoding="utf-8")
        self.assertRejected("ADR must start with '# ' heading: docs/adr/0020-matt-flow-skill.md")

    def test_orphan_reference_doc_is_rejected(self) -> None:
        orphan = self.fixture / SKILLS / "letsgo/references/orphan.md"
        orphan.write_text("# 孤儿规则\n\n未被引用的内容。\n", encoding="utf-8")
        self.assertRejected(f"orphan reference doc (unreachable from any SKILL.md): {SKILLS}/letsgo/references/orphan.md")

    def test_mutually_linked_unreachable_references_are_rejected(self) -> None:
        refs = self.fixture / SKILLS / "letsgo/references"
        (refs / "island-a.md").write_text("# 孤岛 A\n\n参见 [B](island-b.md)。\n", encoding="utf-8")
        (refs / "island-b.md").write_text("# 孤岛 B\n\n参见 [A](island-a.md)。\n", encoding="utf-8")
        errors = "\n".join(self.run_validation())
        self.assertIn(f"orphan reference doc (unreachable from any SKILL.md): {SKILLS}/letsgo/references/island-a.md", errors)
        self.assertIn(f"orphan reference doc (unreachable from any SKILL.md): {SKILLS}/letsgo/references/island-b.md", errors)


class SimpleYamlParserTests(unittest.TestCase):
    def test_top_level_scalars_and_inline_comments(self) -> None:
        raw = (
            "# leading comment\n"
            "plain: letsgo\n"
            "tag: foo#bar\n"
            "commented: value # inline comment\n"
            'double_colon: "letsgo:guide"\n'
            'double_escaped: "a\\"b\\\\c\\nd # keep" # trailing comment\n'
            "single_escaped: 'it''s # ok' # trailing comment\n"
            "bool_true: true\n"
            "bool_false: false\n"
            'quoted_bool: "true"\n'
            "null_word: null\n"
            "null_tilde: ~\n"
            "null_blank:\n"
            "empty_map: {}\n"
            "empty_list: []\n"
        )
        parsed = validate.parse_simple_yaml(raw)
        self.assertEqual(
            parsed,
            {
                "plain": "letsgo",
                "tag": "foo#bar",
                "commented": "value",
                "double_colon": "letsgo:guide",
                "double_escaped": 'a"b\\c\nd # keep',
                "single_escaped": "it's # ok",
                "bool_true": True,
                "bool_false": False,
                "quoted_bool": "true",
                "null_word": None,
                "null_tilde": None,
                "null_blank": None,
                "empty_map": {},
                "empty_list": [],
            },
        )

    def test_nested_mappings_and_dedent(self) -> None:
        raw = (
            "metadata:\n"
            '  short-description: "letsgo 基础规则、共用规则与私人资料"\n'
            "interface:\n"
            '  display_name: "letsgo: guide"\n'
            "  details:\n"
            "    enabled: true\n"
            "policy:\n"
            "  allow_implicit_invocation: false\n"
            "empty_section:\n"
            "top: done\n"
        )
        parsed = validate.parse_simple_yaml(raw)
        self.assertEqual(
            parsed,
            {
                "metadata": {"short-description": "letsgo 基础规则、共用规则与私人资料"},
                "interface": {
                    "display_name": "letsgo: guide",
                    "details": {"enabled": True},
                },
                "policy": {"allow_implicit_invocation": False},
                "empty_section": None,
                "top": "done",
            },
        )

    def test_block_scalars_and_crlf(self) -> None:
        raw = (
            "literal: |\r\n"
            "  line 1\r\n"
            "\r\n"
            "  line 2\r\n"
            "literal_strip: |-\r\n"
            "  line a\r\n"
            "  line b\r\n"
            "folded: >\r\n"
            "  hello\r\n"
            "  world\r\n"
            "\r\n"
            "  next para\r\n"
            "folded_strip: >-\r\n"
            "  one\r\n"
            "  two\r\n"
            "after: ok\r\n"
        )
        parsed = validate.parse_simple_yaml(raw)
        self.assertEqual(
            parsed,
            {
                "literal": "line 1\n\nline 2\n",
                "literal_strip": "line a\nline b",
                "folded": "hello world\nnext para\n",
                "folded_strip": "one two",
                "after": "ok",
            },
        )

    def test_malformed_inputs_raise_value_error(self) -> None:
        cases = (
            "a:\n\tb: 1\n",
            "a:\n    b: 1\n  c: 2\n",
            "  leading: bad\n",
            'name: "unclosed\n',
            "name: 'unclosed\n",
            'name: "closed" trailing\n',
            "name: letsgo\n  nested: bad\n",
            "empty: {}\n  nested: bad\n",
        )
        for bad in cases:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    validate.parse_simple_yaml(bad)


if __name__ == "__main__":
    unittest.main()
