# 升级 skill-walk 为 guide、移除拷问收敛门禁并放松 matt-flow 选型措辞

> 状态：其中关于 `guide` 触发方式标签、停下必给极简接力代码块及收尾复盘规则已由 [ADR-0029](0029-minimal-prompts-and-orchestrator-choice.md) 修订。

修订 [ADR-0017](0017-minimal-plugin.md)、[ADR-0020](0020-matt-flow-skill.md) 与 [ADR-0026](0026-0.0.8-skills-update.md) 中关于 `skill-walk`、`grill-gate.md` 与 `matt-flow` 选型约束的部分；插件技能总数保持 10 个（隐式技能 `letsgo` + 9 个显式技能），计划发布为 `0.0.11`。

2026-11-25 决定对 `letsgo` 插件做以下三项调整：

- **将 `skill-walk` 更名并扩展为 `guide`（引导实施）**：
  - 将 `plugins/letsgo/skills/skill-walk/` 迁移为 `plugins/letsgo/skills/guide/`（`name: "letsgo:guide"`，Codex 菜单显示 `letsgo: guide`，继续保持 `disable-model-invocation: true`、`allow_implicit_invocation: false`）。
  - 评估对象由“用户指定的已生效 skill(s)”扩展为当前宿主客户端具备的所有“能力”（统称 skill、MCP 工具与内置工具）。引入“能力范围”优先级：本次消息明确指定 > 上下文明确表达“用 X 来做”（仅提及或讨论不算指定） > 默认“全部能力”（支持“全部能力”“全部”“all”同义）；读写文件、终端、搜索等基础内置能力始终可用。
  - 采用两段低耗筛选：初筛仅查看会话已载入能力清单的名称与描述（不在回复中罗列完整清单）；深读仅对入围候选读取 `SKILL.md` 或 MCP Schema（单轮一般不超过 3 个，确需更多时简短说明原因），同会话内已评估结论直接复用；不建立持久化能力索引文件；指定范围内某能力未在当前宿主生效时提示未生效，按缺失能力处理，不凭记忆执行。
  - 规范执行节奏与提示词输出：
    - 可隐式触发或直接调用的能力：直接推进，每采用一项输出 `【guide】采用 <能力> —— <一句话用途>`；若范围外已安装的 skill / MCP 明显更合适，直接采用并在说明行加注 `（范围外）`。
    - 必须显式调用的技能（设了 `disable-model-invocation: true`）：默认停下，给出以目标原生命令（Claude Code 与 Antigravity 为 `/<skill>`，Codex 为 `$<skill>`，同会话继续时不前置 `letsgo:guide`）开头的代码块提示词；仅当用户在调用时明确授权（如“显式技能可代为执行”），才在本会话内读取其 `SKILL.md` 直接执行并输出说明（高危变更仍遵守 `change-safety.md`）。
    - 无匹配扩展能力但当前客户端可直接实施：输出 `【guide】无匹配能力，直接实施 —— <原因>`，是否停下由现场决定，不额外干预。
    - 缺少必要支持：优先检索宿主自带市场（Antigravity 使用 `search_marketplace`，Claude Code 与 Codex 查询插件市场），已安装 `find-skills` 时配合使用，必要时联网检索；只报告名称、用途、安装方式及不添加时的替代做法，停下等待用户决定，不自行安装。
  - 全部任务完成后输出简短总结，列出本次使用的能力与各自用法要点。
- **彻底移除拷问收敛门禁（`references/grill-gate.md`）**：删除 `plugins/letsgo/skills/letsgo/references/grill-gate.md`，并从 `plugins/letsgo/skills/letsgo/SKILL.md` 的 `description` 与路由表中移除对应条目；`grilling`、`grill-me` 或 `grill-with-docs` 收敛后不再由插件隐式门禁拦截，若需只报告不实施，由用户在调用时显式声明。
- **放松 `matt-flow` 选型措辞**：更新 `plugins/letsgo/skills/matt-flow/SKILL.md`、`agents/openai.yaml` 及 `plugins/letsgo/skills/letsgo/references/matt-route.md` 路线图第 1 条，移除“最小必要”“最小技能序列”等偏向缩减组合的限定语，改为按当前需求的复杂度、清晰度与上下文状态现场评估并推荐单个技能或完整主线等合适技能组合。

## Considered Options

- **是否为 `guide` 建立持久化能力索引文件**：持久化的本地能力清单缓存会在插件增删、MCP 变更或跨项目切换时迅速过期失效，且每次维护都需要额外的磁盘读写与同步逻辑；宿主会话已载入可用能力的名称与简要描述，采用“名称/描述初筛 + 仅深读少数入围候选 + 同会话复用评估结论”的两段式现场评估即可兼顾准确度与上下文开销。
- **对必须显式调用的技能一律停下还是默认自动代跑**：设置 `disable-model-invocation: true` 的技能往往带有明确的边界约束或独立上下文假设（例如发布、Git 收尾、交互式工作流），默认停下并给出原生命令代码块可保留用户控制权并帮助用户掌握用法；但在连续推进场景下完全禁止代跑又略显僵硬，因此保留默认停下策略，仅在用户调用 `guide` 时显式授权（如“显式技能可代为执行”）才放行本会话读取并执行。
- **范围外出现明显更合适能力时如何处置**：若严格限定在指定范围，明知范围外已有更高契合度的已安装能力却故意退而求其次会损害方案质量；若停下多问一轮会打断节奏；若静默启用又违背范围契约。因此选择直接采用并显式加注 `（范围外）`，在兼顾结果质量与推进效率的同时保持过程完全透明。
- **保留可配置的 `grill-gate.md` 还是彻底删除改为调用时显式声明**：隐式加载的全局收敛门禁无法准确区分“拷问完直接继续实施”与“先停下审阅方案”两种意图，且容易在 `guide` 或其他组合调用中造成预期外的停顿；彻底删除 `grill-gate.md` 使默认规则保持最小无侵入，用户需要只报告不实施时在调用提示词中显式声明（如 `/grill-with-docs …（方案明确后只报告，不实施）`）即可精确控制。

## Consequences

- `letsgo` 插件保持 10 个技能不变，计划在完成校验后发布为 `0.0.11`。
- 原使用 `/letsgo:skill-walk`（Codex：`$letsgo:letsgo:skill-walk`）的调用方式迁移为 `/letsgo:guide`（Codex：`$letsgo:letsgo:guide`）；需要拷问收敛后停下的场景需在调用时显式声明。
- 更新三端 `plugin.json`、`scripts/validate.py`（`EXPECTED_SKILLS` 替换为 `guide`，并在 `LEGACY_PATTERNS` 拦截插件技能源码内残留的 `letsgo:skill-walk` 与 `grill-gate.md`）及单元测试 `scripts/tests/test_plugin_validation.py`，同步更新 `GLOSSARY.md`、`CHANGELOG.md`、`docs/compatibility.md`、`docs/authoring.md`、`AGENTS.md` 与 `README.md`。
