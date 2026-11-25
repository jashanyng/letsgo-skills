# letsgo-skills

本仓库是 `letsgo` 插件的开发副本（支持 Codex、Claude Code 与 Antigravity），同时作为 Codex 与 Claude Code 的插件市场 `letsgo-skills`。

## 导航

- **修改技能、规则布局、增删/更名技能或执行发版与三端同步**：先读 [docs/authoring.md](docs/authoring.md)。
- **涉及领域术语与架构决策**：读 [GLOSSARY.md](GLOSSARY.md) 与 `docs/adr/`（三端共用唯一 `plugins/letsgo/skills/`，不引入已废除的任务流程与需求分类概念）。
- **涉及三端兼容边界、依赖前置、版本演进契约或升级迁移**：同步更新 [docs/compatibility.md](docs/compatibility.md)。
- **产生公开可见变更**：记入 [CHANGELOG.md](CHANGELOG.md) 的 `## [Unreleased]`。

## 硬性红线

- **严禁事件钩子**（[ADR-0010](docs/adr/0010-no-hooks-skills-carry-rules.md)）：插件功能只通过技能与 `plugins/letsgo/skills/letsgo/references/` 规则资料实现（一条规则只写一处），不使用 `hooks/`、`rules/` 或任何 `hooks` 配置。
- **载荷与私人资料隔离**：私人资料只保存在当前用户本机 `~/.agents/letsgo/personal/`（入口 `index.md`），不写入仓库或插件包；发版与版本治理文档只留在仓库根级与 `docs/`，不写入 `plugins/letsgo/`；开发流程不要求用户运行安装脚本或改写全局入口文件。
- **只编辑开发副本**：不编辑三端已安装的插件缓存目录（`~/.claude/plugins/cache/`、`~/.codex/plugins/cache/`、`~/.gemini/config/plugins/letsgo/`）。
- **校验与发版权限**：提交前运行 `python3 scripts/validate.py`（改动脚本时同时运行 `python3 -m unittest discover -s scripts/tests`）。版本号、市场 `ref` 与 Git 标签统一用裸 `x.y.z`（无 `v` 前缀）；仅在改动 `plugins/letsgo/` 并验收准备交付时使用 `scripts/release.sh x.y.z` 发版并同步更新本机支持端（未改 `plugins/letsgo/` 时不发版、不更新三端）。智能体仅被授权递增 `z`，修改 `x` 或 `y` 必须经维护者明确同意并显式传 `--allow-xy-bump`。

## Agent skills

以下配置只服务于本仓库的开发流程，供 mattpocock-skills 读取；不属于 `letsgo` 插件，也不随发布分发（发布只打包 `plugins/letsgo/`）。

### Issue tracker

Issue 记录在 GitHub Issues（`jashanyng/letsgo-skills`），使用 `gh` CLI 操作。详见 [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md)。

### Triage labels

使用默认的五个标准 triage 标签，标签名与角色名一致。详见 [docs/agents/triage-labels.md](docs/agents/triage-labels.md)。

### Domain docs

单上下文（single-context）布局：仓库根目录 [GLOSSARY.md](GLOSSARY.md) + `docs/adr/`。详见 [docs/agents/domain.md](docs/agents/domain.md)。
