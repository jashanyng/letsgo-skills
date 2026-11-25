# letsgo-skills

本仓库是 `letsgo` 插件的开发副本，支持 Codex、Claude Code 与 Antigravity，同时作为 Codex 与 Claude Code 的插件市场 `letsgo-skills`。

- 修改技能前先读 [docs/authoring.md](docs/authoring.md) 与 [GLOSSARY.md](GLOSSARY.md)；架构决策见 `docs/adr/`，当前插件范围遵循 [ADR-0017](docs/adr/0017-minimal-plugin.md)、[ADR-0018](docs/adr/0018-single-skills-directory.md)、[ADR-0019](docs/adr/0019-write-an-article-skill.md)、[ADR-0020](docs/adr/0020-matt-flow-skill.md)、[ADR-0022](docs/adr/0022-swarm-up-skill.md)、[ADR-0025](docs/adr/0025-git-wrap-skill.md)、[ADR-0026](docs/adr/0026-0.0.8-skills-update.md) 与 [ADR-0028](docs/adr/0028-guide-skill-and-rules-update.md)：三端共用一份 `plugins/letsgo/skills/`，只有隐式技能 `letsgo`、三个 `stepping-*` 技能、`write-an-article`、`matt-flow`、`prove-it`、`guide`、`try-swarm` 与 `git-wrap`；不引入自定义任务流程、需求分类等流程概念，`matt-flow` 只转述 mattpocock-skills 自身的步骤，`guide` 只按需求在能力范围或当前宿主全部能力中现场评估适合的 skill、MCP 与内置工具并推进实施、给出原生命令提示词或推荐缺失能力。
- **硬性规定**：插件的任何功能都不得用事件钩子实现，只能通过三端安装插件后提供的技能与规则资料实现（[ADR-0010](docs/adr/0010-no-hooks-skills-carry-rules.md)）；`scripts/validate.py` 会拒绝任何钩子配置。
- 保持简洁：一条规则只写在一个文件里；基础、共用与用户级规则放在 `plugins/letsgo/skills/letsgo/references/`。
- 私人资料只保存在当前用户的 `~/.agents/letsgo/personal/` 分类目录，入口为 `index.md`，不得写入仓库或插件包。开发流程不得要求用户运行仓库安装脚本或复制规则到全局入口文件。
- 提交前运行 `python3 scripts/validate.py`；发布只用 `scripts/release.sh x.y.z`（或经维护者同意修改 `x`/`y` 时使用 `scripts/release.sh --allow-xy-bump x.y.z`）。修改了 `plugins/letsgo/` 并完成验收准备交付时，发布新版本并按 [docs/authoring.md](docs/authoring.md#校验与发布) 同步更新本机支持端（未改动 `plugins/letsgo/` 时不发版、不更新三端）。
- **变更日志与兼容性文档门禁**：公开可见变更须记入根目录 [CHANGELOG.md](CHANGELOG.md) 的 `## [Unreleased]`（`scripts/release.sh` 发版时会自动归档到 `## [x.y.z] - YYYY-MM-DD`）；涉及三端宿主适配、依赖前置、版本演进契约或升级迁移步骤的改动须同步更新 [docs/compatibility.md](docs/compatibility.md)；`scripts/validate.py` 会强制校验两份文档存在性及版本节完整性。
- **版本规则与权限红线**（[ADR-0027](docs/adr/0027-bare-xyz-versioning.md)）：版本号、市场 `ref` 与 Git 标签统一使用不带 `v` 前缀的裸 `x.y.z`。制作期从 `0.0.1` 起步并仅递增 `z`；正式对外推荐或上架外部技能平台时才定为 `1.0.0`（`1.0.0` 后 `x` 对应重大架构/组织/品牌代际，`y` 对应开发期周期批次，`z` 对应同批次功能与修复递增）。智能体仅被授权递增 `z`，修改 `x` 或 `y` 必须经维护者明确同意并显式传 `--allow-xy-bump`（未传时 `scripts/release.sh` 默认阻断）；且仓库内部发版与版本治理文档只保存在仓库根级与 `docs/`，不得写入 `plugins/letsgo/` 运行时载荷。
- 不要编辑插件安装后的缓存目录（`~/.claude/plugins/cache/`、`~/.codex/plugins/cache/`、`~/.gemini/config/plugins/letsgo/`），那里的改动不会回到仓库。

## Agent skills

以下配置只服务于本仓库的开发流程，供 mattpocock-skills 读取；不属于 `letsgo` 插件，也不随发布分发（发布只打包 `plugins/letsgo/`）。

### Issue tracker

Issue 记录在 GitHub Issues（`jashanyng/letsgo-skills`），使用 `gh` CLI 操作。详见 `docs/agents/issue-tracker.md`。

### Triage labels

使用默认的五个标准 triage 标签，标签名与角色名一致。详见 `docs/agents/triage-labels.md`。

### Domain docs

单上下文（single-context）布局：仓库根目录 `GLOSSARY.md` + `docs/adr/`。详见 `docs/agents/domain.md`。
