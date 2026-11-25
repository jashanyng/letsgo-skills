# 变更日志（Changelog）

本文件记录 `letsgo` 插件与本仓库所有公开可见的版本变更，作为每次版本更新说明（Release Notes）的唯一事实源。日常未发版改动应先记入 `## [Unreleased]`；执行 `scripts/release.sh <version>` 时会自动归档到对应版本标题下。

## [Unreleased]

## [0.0.10] - 2026-11-25

### 规范与基线

- **统一裸 `x.y.z` 版本号与市场锁定基线**（[ADR-0027](docs/adr/0027-bare-xyz-versioning.md)）：三端清单（`.claude-plugin/plugin.json`、`.codex-plugin/plugin.json`、`.antigravity-plugin/plugin.json`）的 `version`、市场清单（`.claude-plugin/marketplace.json`、`.agents/plugins/marketplace.json`）的 `source.ref` 以及 Git 发布标签统一采用无 `v` 前缀的裸 `x.y.z`；明确当前处于 `0.0.x` 制作期且默认仅递增 `z`，修改 `x` 或 `y` 须经维护者同意并传入 `scripts/release.sh --allow-xy-bump`。
- **三端共用 10 技能结构基线**（[ADR-0017](docs/adr/0017-minimal-plugin.md)、[ADR-0018](docs/adr/0018-single-skills-directory.md)、[ADR-0025](docs/adr/0025-git-wrap-skill.md)、[ADR-0026](docs/adr/0026-0.0.8-skills-update.md)）：Codex、Claude Code 与 Antigravity 共用唯一 `plugins/letsgo/skills/` 目录，收敛为 1 个隐式基础规则技能（`letsgo`）与 9 个显式技能（`stepping-begin`、`stepping-doit`、`stepping-finish`、`write-an-article`、`matt-flow`、`prove-it`、`skill-walk`、`try-swarm`、`git-wrap`）。
- **无事件钩子硬性约束与校验门禁**（[ADR-0010](docs/adr/0010-no-hooks-skills-carry-rules.md)）：插件不使用 `hooks/`、`rules/` 目录或任何宿主事件钩子，全部规则与行为通过技能与 `references/` 承载，并由 `scripts/validate.py` 与 `scripts/tests/` 强制门禁校验。
- **运行时载荷隔离**：版本演进与发版治理规范仅保存在仓库根级与 `docs/` 下，不写入 `plugins/letsgo/` 插件载荷；私人资料仅保存于用户本机 `~/.agents/letsgo/personal/`。
