# 编写 letsgo 插件

本仓库是开发副本；用户通过 Codex、Claude Code 或 Antigravity 的插件管理器安装 `plugins/letsgo/`。仓库脚本只服务作者的校验和发布。术语见 [GLOSSARY.md](../GLOSSARY.md)，当前范围见 [ADR-0017](adr/0017-minimal-plugin.md)、[ADR-0018](adr/0018-single-skills-directory.md)、[ADR-0025](adr/0025-git-wrap-skill.md)、[ADR-0026](adr/0026-0.0.8-skills-update.md) 与 [ADR-0027](adr/0027-bare-xyz-versioning.md)。

## 布局

三端共用唯一的技能目录 `plugins/letsgo/skills/`，只有 10 个技能：

```text
skills/
├── letsgo/                     隐式技能：基础规则、共用规则、用户级规则与私人资料流程
│   ├── SKILL.md                规则路由表
│   ├── agents/openai.yaml
│   └── references/             基础、共用与用户级规则
│       ├── grill-gate.md       拷问收敛门禁规则
│       ├── matt-route.md       只供 matt-flow 读取的路线与门禁规范
│       └── stepping/           步进专用规则
├── stepping-begin/
├── stepping-doit/
├── stepping-finish/
├── write-an-article/           显式技能：生成作为 Obsidian 笔记的文章
├── matt-flow/                  显式技能：借助 ask-matt 选用适合的 mattpocock 技能并自动串联推进
├── prove-it/                   显式技能：对当前改动现场评估测试验收层度，三选一后实施
├── skill-walk/                 显式技能：引导用户采用指定 skill(s) 逐步实现需求
├── try-swarm/                  显式技能：评估并按需采用宿主原生多智能体协同，不干预执行节奏
└── git-wrap/                   显式技能：对涉及仓库执行英文提交、向源分支安全合并推送与清理评估
```

- 一条规则只写在 `letsgo/references/` 的一个文件里，其他文件链接它；显式技能以 `../letsgo/references/...` 引用（`matt-route.md` 只供 `matt-flow` 读取）。`SKILL.md` 保持简短。
- 不使用符号链接（`codex plugin add` 归档时会忽略），也不再维护 Codex 副本。
- Claude Code 清单 `.claude-plugin/plugin.json` 逐项登记技能目录；Codex 清单 `.codex-plugin/plugin.json` 的 `skills` 为 `./skills/`；Antigravity 清单 `.antigravity-plugin/plugin.json` 只用其允许的字段。

## 命名与调用

| 技能 | `name` | `display_name`（Codex 菜单） | 调用 |
| --- | --- | --- | --- |
| `letsgo` | `letsgo` | `letsgo` | 隐式：无 `disable-model-invocation`，`user-invocable: false`，`allow_implicit_invocation: true` |
| `stepping-*`、`write-an-article`、`matt-flow`、`prove-it`、`skill-walk`、`try-swarm`、`git-wrap` | `letsgo:<目录名>` | `letsgo: stepping begin`、`letsgo: write an article` 等 | 显式：`disable-model-invocation: true`，`allow_implicit_invocation: false` |

Codex 总在 `name` 前加插件名，Antigravity 从不加，Claude Code 对 `letsgo:` 开头的 `name` 不重复加。因此 stepping 在 Claude Code 与 Antigravity 中为 `/letsgo:stepping-begin`，在 Codex 中为 `$letsgo:letsgo:stepping-begin`。`agy plugin validate --strict` 会因 `name` 与目录名不一致报警告，这是预期的。

## 规则

- **不得使用事件钩子**（[ADR-0010](adr/0010-no-hooks-skills-carry-rules.md)）：`validate.py` 拒绝 `hooks/`、`rules/` 目录及任何钩子配置。普通对话的规则只由隐式技能 `letsgo` 引入；不修改用户的全局 `AGENTS.md`、`CLAUDE.md` 或设置文件。
- 插件包只含通用规则。主机、SSH 别名、私人域名、网络拓扑与产出路径偏好只在用户本机的 `~/.agents/letsgo/personal/`，不写进技能、示例或测试夹具。
- 新概念先进入 [GLOSSARY.md](../GLOSSARY.md)，难以逆转的取舍用 `docs/adr/` 记录。

## 校验与发布

- 编辑只在开发副本进行，不编辑三端的插件缓存。
- 校验：`python3 scripts/validate.py`；改动校验或发版脚本时运行单元测试 `python3 -m unittest discover -s scripts/tests`。可另用 `agy plugin validate plugins/letsgo` 检查 Antigravity 读取结果。
- **版本规则与权限红线**（[ADR-0027](adr/0027-bare-xyz-versioning.md)）：
  - 插件 `version`、市场 `ref` 与 Git 标签统一使用不带 `v` 前缀的裸 `x.y.z`。
  - 当前处于制作期，从 `0.0.1` 起步并仅递增 `z`；正式对外推荐或上架外部技能平台时定为 `1.0.0`（`1.0.0` 后 `x` 对应重大架构/组织/品牌代际，`y` 对应开发期周期批次，`z` 对应同批次功能与修复递增）。
  - 智能体仅被授权递增 `z`；修改 `x` 或 `y` 必须经维护者明确同意并显式传 `--allow-xy-bump`（未传时 `scripts/release.sh` 默认阻断）。
  - 版本与发版治理规则只保存在仓库根级与 `docs/` 文档，严禁写入 `plugins/letsgo/` 运行时载荷。
- 发布：修改了 `plugins/letsgo/` 并完成验收后，先提交工作区改动，再运行 `scripts/release.sh x.y.z`（维护者同意修改 `x`/`y` 时传 `scripts/release.sh --allow-xy-bump x.y.z`）同步版本号与市场锁定标签、校验、提交、打标签并推送；仅修改仓库开发文档或脚本、未改动 `plugins/letsgo/` 时无需发版与更新客户端。
- **同步更新本机三端客户端**：Codex 与 Claude Code 的市场锁定在远程裸 `x.y.z` 标签，每次运行 `scripts/release.sh x.y.z` 发布成功后，必须立即在本仓库根目录下为本机已安装的支持端更新插件并核验版本号一致（若遇到版本重置导致目标版本低于已缓存旧版，须先卸载旧缓存再重装核验）：
  - **Codex**：`codex plugin marketplace upgrade letsgo-skills && codex plugin add letsgo@letsgo-skills`，再用 `codex plugin list | grep -F 'letsgo@letsgo-skills'` 核验版本为 `x.y.z`（避免裸跑 `codex plugin list` 输出完整远端市场目录）。
  - **Claude Code**：`claude plugin marketplace update letsgo-skills && claude plugin update letsgo@letsgo-skills`，再用 `claude plugin list | grep -A 3 -F 'letsgo@letsgo-skills'` 核验 `Version` 为 `x.y.z`。
  - **Antigravity**：`agy plugin install plugins/letsgo`（刚完成发布的开发副本即对应 `x.y.z`），再用 `agy plugin list | grep -F 'letsgo'` 核验版本为 `x.y.z`。
  - 本机已安装对应客户端与本插件时，若更新失败或版本号不一致，视为交付未完成并如实报告阻塞原因；未安装某客户端 CLI 或该端尚未安装本插件时跳过并在报告中注明。更新后提示开启新会话生效。
