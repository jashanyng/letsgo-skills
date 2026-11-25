"""在隔离副本中验证插件校验门。"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
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

    def validate(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/validate.py"], cwd=self.fixture, text=True, capture_output=True, check=False
        )

    def assertRejected(self, message: str) -> None:
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stdout)

    def edit(self, relative: str, old: str, new: str) -> None:
        path = self.fixture / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def append(self, relative: str, text: str) -> None:
        with (self.fixture / relative).open("a", encoding="utf-8") as stream:
            stream.write(text)

    def test_valid_plugin_passes(self) -> None:
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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
        self.edit(f"{SKILLS}/stepping-begin/SKILL.md", "(../letsgo/references/stepping/workflow.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("missing route ../letsgo/references/stepping/workflow.md")

    def test_article_skill_must_link_language(self) -> None:
        self.edit(f"{SKILLS}/write-an-article/SKILL.md", "(../letsgo/references/language.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("write-an-article: missing route ../letsgo/references/language.md")

    def test_article_skill_must_be_explicit(self) -> None:
        self.edit(f"{SKILLS}/write-an-article/SKILL.md", "disable-model-invocation: true\n", "")
        self.assertRejected("write-an-article: must be explicit-only")

    def test_matt_flow_skill_must_link_matt_route(self) -> None:
        self.edit(f"{SKILLS}/matt-flow/SKILL.md", "(../letsgo/references/matt-route.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("matt-flow: missing route ../letsgo/references/matt-route.md")

    def test_prove_it_skill_must_link_language(self) -> None:
        self.edit(f"{SKILLS}/prove-it/SKILL.md", "(../letsgo/references/language.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("prove-it: missing route ../letsgo/references/language.md")

    def test_prove_it_skill_must_be_explicit(self) -> None:
        self.edit(f"{SKILLS}/prove-it/SKILL.md", "disable-model-invocation: true\n", "")
        self.assertRejected("prove-it: must be explicit-only")

    def test_skill_walk_skill_must_link_language(self) -> None:
        self.edit(f"{SKILLS}/skill-walk/SKILL.md", "(../letsgo/references/language.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("skill-walk: missing route ../letsgo/references/language.md")

    def test_skill_walk_skill_must_be_explicit(self) -> None:
        self.edit(f"{SKILLS}/skill-walk/SKILL.md", "disable-model-invocation: true\n", "")
        self.assertRejected("skill-walk: must be explicit-only")

    def test_try_swarm_skill_must_link_language(self) -> None:
        self.edit(f"{SKILLS}/try-swarm/SKILL.md", "(../letsgo/references/language.md)", "(../letsgo/SKILL.md)")
        self.assertRejected("try-swarm: missing route ../letsgo/references/language.md")

    def test_try_swarm_skill_must_be_explicit(self) -> None:
        self.edit(f"{SKILLS}/try-swarm/SKILL.md", "disable-model-invocation: true\n", "")
        self.assertRejected("try-swarm: must be explicit-only")

    def test_git_wrap_skill_must_link_language(self) -> None:
        self.edit(f"{SKILLS}/git-wrap/SKILL.md", "(../letsgo/references/language.md)", "(../letsgo/SKILL.md)")
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
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("plugin.json must not declare hooks", result.stdout)
        self.assertIn("SKILL.md must not declare hooks", result.stdout)

    def test_system_metadata_cannot_enter_plugin_payload(self) -> None:
        (self.fixture / SKILLS / "letsgo/.DS_Store").write_bytes(b"junk")
        self.assertRejected("unwanted file in plugin payload")

    def test_antigravity_manifest_version_and_fields_are_checked(self) -> None:
        manifest = self.fixture / "plugins/letsgo/.antigravity-plugin/plugin.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["version"] = "9.9.9"
        data["skills"] = "./skills/"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("plugin versions differ", result.stdout)
        self.assertIn("unsupported fields", result.stdout)

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
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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

if __name__ == "__main__":
    unittest.main()
