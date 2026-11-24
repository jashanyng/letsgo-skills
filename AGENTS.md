# letsgo-skills

本仓库是 `letsgo` 插件的开发副本，支持 Codex、Claude Code 与 Antigravity，同时作为 Codex 与 Claude Code 的插件市场 `letsgo-skills`。

- 修改技能前先读 [docs/authoring.md](docs/authoring.md) 与 [GLOSSARY.md](GLOSSARY.md)；架构决策见 `docs/adr/`，当前插件范围遵循 [ADR-0017](docs/adr/0017-minimal-plugin.md)、[ADR-0018](docs/adr/0018-single-skills-directory.md)、[ADR-0019](docs/adr/0019-write-an-article-skill.md)、[ADR-0020](docs/adr/0020-matt-flow-skill.md)、[ADR-0022](docs/adr/0022-swarm-up-skill.md)、[ADR-0025](docs/adr/0025-git-wrap-skill.md) 与 [ADR-0026](docs/adr/0026-v360-skills-update.md)：三端共用一份 `plugins/letsgo/skills/`，只有隐式技能 `letsgo`、三个 `stepping-*` 技能、`write-an-article`、`matt-flow`、`prove-it`、`skill-walk`、`try-swarm` 与 `git-wrap`；不引入自定义任务流程、需求分类等流程概念，`matt-flow` 只转述 mattpocock-skills 自身的步骤，`skill-walk` 只引导采用指定的已生效技能。
- **硬性规定**：插件的任何功能都不得用事件钩子实现，只能通过三端安装插件后提供的技能与规则资料实现（[ADR-0010](docs/adr/0010-no-hooks-skills-carry-rules.md)）；`scripts/validate.py` 会拒绝任何钩子配置。
- 保持简洁：一条规则只写在一个文件里；基础、共用与用户级规则放在 `plugins/letsgo/skills/letsgo/references/`。
- 私人资料只保存在当前用户的 `~/.agents/letsgo/personal/` 分类目录，入口为 `index.md`，不得写入仓库或插件包。开发流程不得要求用户运行仓库安装脚本或复制规则到全局入口文件。
- 提交前运行 `python3 scripts/validate.py`；发布只用 `scripts/release.sh X.Y.Z`。修改了 `plugins/letsgo/` 并完成验收准备交付时，发布新版本并按 [docs/authoring.md](docs/authoring.md#校验与发布) 同步更新本机支持端（未改动 `plugins/letsgo/` 时不发版、不更新三端）。
- 不要编辑插件安装后的缓存目录（`~/.claude/plugins/cache/`、`~/.codex/plugins/cache/`、`~/.gemini/config/plugins/letsgo/`），那里的改动不会回到仓库。

## Agent skills

以下配置只服务于本仓库的开发流程，供 mattpocock-skills 读取；不属于 `letsgo` 插件，也不随发布分发（发布只打包 `plugins/letsgo/`）。

### Issue tracker

Issue 记录在 GitHub Issues（`jashanyng/letsgo-skills`），使用 `gh` CLI 操作。详见 `docs/agents/issue-tracker.md`。

### Triage labels

使用默认的五个标准 triage 标签，标签名与角色名一致。详见 `docs/agents/triage-labels.md`。

### Domain docs

单上下文（single-context）布局：仓库根目录 `GLOSSARY.md` + `docs/adr/`。详见 `docs/agents/domain.md`。
