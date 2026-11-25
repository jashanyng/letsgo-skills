# 兼容性与升级指南

本文档定义 `letsgo` 插件在 Codex、Claude Code 与 Antigravity 三端运行时的环境兼容边界、版本演进契约与升级迁移步骤；上述治理内容仅保存在 `docs/`，不写入 `plugins/letsgo/` 运行时载荷。

## 环境与依赖兼容矩阵

### 宿主端支持与清单映射

| 宿主端 | 插件清单 | 分发 / 安装来源 | 技能调用形式 | 备注 |
| --- | --- | --- | --- | --- |
| Codex 桌面 / CLI | `plugins/letsgo/.codex-plugin/plugin.json`（`skills: "./skills/"`） | `.agents/plugins/marketplace.json`（市场 `letsgo-skills` 锁定裸 `x.y.z` 标签） | 隐式 `letsgo`；显式 `$letsgo:letsgo:<名称>` | Codex 自动在技能 `name` 前加插件名；菜单显示为 `letsgo: <空格分隔名称>` |
| Claude Code | `plugins/letsgo/.claude-plugin/plugin.json`（逐项登记 10 个技能） | `.claude-plugin/marketplace.json`（市场 `letsgo-skills` 锁定裸 `x.y.z` 标签） | 隐式 `letsgo`（菜单隐藏）；显式 `/letsgo:<名称>` | 对 `letsgo:` 前缀的 `name` 不重复拼接插件名 |
| Antigravity | `plugins/letsgo/.antigravity-plugin/plugin.json`（仅允许受支持字段） | 本地检出路径 `agy plugin install <插件目录>` | 隐式 `letsgo`；显式 `/letsgo:<名称>` | 不通过市场清单安装；`agy plugin validate --strict` 因 `name` 与目录名不一致产生的警告为预期行为 |

### 技能命名与三端调用映射

三端共用唯一的 `plugins/letsgo/skills/` 目录，无符号链接、无 `skills-codex/` 副本（[ADR-0018](adr/0018-single-skills-directory.md)）：

- 隐式基础规则技能：`letsgo`（`name: "letsgo"`，`user-invocable: false`，`allow_implicit_invocation: true`）。
- 显式技能（共 9 个，均配置 `disable-model-invocation: true`、`allow_implicit_invocation: false`，`name` 为 `letsgo:<目录名>`）：`stepping-begin`、`stepping-doit`、`stepping-finish`、`write-an-article`、`matt-flow`、`prove-it`、`guide`、`try-swarm`、`git-wrap`。

### 依赖前置与运行边界

- **`mattpocock-skills` 前置要求**：显式技能 `matt-flow` 借助 `ask-matt` 选用并串联 `mattpocock-skills` 技能，调用前需在本机对应宿主端已安装 `mattpocock-skills`。
- **`guide` 能力评估与宿主市场推荐边界**：`guide` 仅基于会话已载入能力清单及入围候选的 `SKILL.md` / MCP Schema 现场评估，不创建持久化能力索引文件；指定范围内未生效的能力不凭记忆执行。缺少必要支持时优先检索宿主自带市场（Antigravity 使用 `search_marketplace`，Claude Code 与 Codex 查询插件市场；若已安装 `find-skills` 则配合使用，必要时联网检索），且只报告名称、用途、安装方式及替代做法，不自行安装。
- **无事件钩子硬性边界**（[ADR-0010](adr/0010-no-hooks-skills-carry-rules.md)）：`letsgo` 插件不使用任何宿主生命周期事件钩子，拒绝 `hooks/`、`rules/` 目录及清单/前置元数据中的 `hooks` 字段，由 `scripts/validate.py` 机械拦截。
- **多智能体协同映射**：`try-swarm` 按宿主端原生能力评估与触发——Codex 对应 `multi_agent_v2`、Claude Code 对应 `Agent Teams`、Antigravity 对应 `swarm`。
- **本机私人资料隔离**：宿主主机、SSH、域名与默认产出目录等私人事实仅保存于当前用户本机 `~/.agents/letsgo/personal/`（入口为 `index.md`），交付文章等产出存放在 `~/.agents/letsgo/generated/`；安装或升级插件本身不会创建用户目录，也不会改写用户的全局 `AGENTS.md`、`CLAUDE.md` 或客户端配置文件。

## 演进阶段与版本兼容契约

依据 [ADR-0027](adr/0027-bare-xyz-versioning.md)，本仓库版本号与分发契约遵循以下约定：

- **裸 `x.y.z` 统一格式**：三端 `plugin.json` 的 `version`、两份 `marketplace.json` 的 `source.ref` 以及 Git 发布标签一律使用不带 `v` 前缀的裸 `x.y.z`。
- **`0.0.x` 制作期契约**：插件处于 `0.0.x` 制作期，从 `0.0.1` 起步并仅递增 `z`；在此阶段允许围绕十个核心技能与规则路由持续打磨。智能体仅被授权递增 `z`，任何 `x` 或 `y` 变更必须经维护者明确同意并在发布时显式传入 `scripts/release.sh --allow-xy-bump x.y.z`。
- **`1.0.0` 公开推荐分界与 `x/y/z` 语义**：仅当插件正式对外推荐或上架外部技能平台时，才将版本定为 `1.0.0`。进入 `1.0.0` 后：
  - `x`：重大架构调整、组织形态或品牌代际变更；
  - `y`：开发期周期批次演进；
  - `z`：同批次内的功能增补与缺陷修复递增。

## 升级与迁移指南

### 标准升级与版本核验命令

发布新版本 `x.y.z` 后，在各自宿主的 CLI 中升级插件、核验已生效版本与 `x.y.z` 一致，并开启新会话使其生效：

1. **Codex**：
   ```sh
   codex plugin marketplace upgrade letsgo-skills && codex plugin add letsgo@letsgo-skills
   codex plugin list --marketplace letsgo-skills
   ```
2. **Claude Code**：
   ```sh
   claude plugin marketplace update letsgo-skills && claude plugin update letsgo@letsgo-skills
   claude plugin list | grep -A 3 -F 'letsgo@letsgo-skills'
   ```
3. **Antigravity**（指向检出目标版本标签的本仓库副本）：
   ```sh
   agy plugin install plugins/letsgo
   agy plugin list | grep -F 'letsgo'
   ```

> 注：请勿直接编辑插件缓存目录（`~/.claude/plugins/cache/`、`~/.codex/plugins/cache/`、`~/.gemini/config/plugins/letsgo/`），所有修改应在本开发副本完成并经发布流程分发。

### 版本重置时先卸载旧缓存再重装

当发生版本序列重置、导致目标版本数值低于宿主端已安装旧缓存版本时（例如 [ADR-0027](adr/0027-bare-xyz-versioning.md) 将历史 `3.6.0` 重置对齐至 `0.0.10`），直接执行 `update` / `upgrade` 可能无法覆盖更高版本号的旧缓存。此时必须先卸载旧插件并清理缓存，再重新安装并核验版本号：

1. **Codex**：先卸载或移除已安装的 `letsgo@letsgo-skills` 旧版本缓存，更新市场后重新执行 `codex plugin add letsgo@letsgo-skills`，再用 `codex plugin list --marketplace letsgo-skills` 确认版本。
2. **Claude Code**：先执行 `claude plugin uninstall letsgo@letsgo-skills` 清除旧版本缓存，更新市场后重新执行 `claude plugin install letsgo@letsgo-skills`，再用 `claude plugin list | grep -A 3 -F 'letsgo@letsgo-skills'` 确认 `Version` 字段。
3. **Antigravity**：先执行 `agy plugin uninstall letsgo`（或卸载旧安装项），再执行 `agy plugin install plugins/letsgo` 并通过 `agy plugin list | grep -F 'letsgo'` 确认版本一致。

### 历史迁移记录

| 迁移节点 | 变更与重映射说明 | 参考决策 |
| --- | --- | --- |
| `0.0.11`（2026-11-25） | 将 `skill-walk` 更名并扩展为 `guide`（覆盖 skill、MCP 与内置工具），移除 `grill-gate.md` 隐式门禁并放松 `matt-flow` 选型措辞；原 `/letsgo:skill-walk`（Codex `$letsgo:letsgo:skill-walk`）迁移至 `/letsgo:guide`（Codex `$letsgo:letsgo:guide`），需要拷问收敛后停下可在调用时显式声明 | [ADR-0028](adr/0028-guide-skill-and-rules-update.md) |
| `0.0.10`（2026-11-25） | 废弃历史带 `v` 前缀标签与 `3.x` 编号序列（原 `v1.0.8` 与 `3.0.0`–`3.6.0` 按演进节点重映射为 `0.0.1`–`0.0.8`，身份迁移后版本记为 `0.0.9`），统一切换为裸 `x.y.z` 标签并从 `0.0.10` 续接；从旧版升级需按上节先卸载旧缓存再重装 | [ADR-0027](adr/0027-bare-xyz-versioning.md) |
| `0.0.8`（2026-11-24） | 移除 `matt-guide`、将 `swarm-up` 重命名为 `try-swarm`（不再干预任务节奏），新增 `prove-it`、`skill-walk` 与 `grill-gate.md` 收敛门禁，技能数由 9 个增至 10 个 | [ADR-0026](adr/0026-0.0.8-skills-update.md) |
| `0.0.7`（2026-11-22） | 新增显式技能 `git-wrap`，专门承担多仓库与链接工作树的安全收尾（含长期保护分支校验与清理评估） | [ADR-0025](adr/0025-git-wrap-skill.md) |
