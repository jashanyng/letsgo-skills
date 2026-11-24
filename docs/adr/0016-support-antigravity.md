# 新增 Antigravity 支持，形成三端共用插件

> 状态：主入口与技能数量部分已被 [ADR-0017](0017-minimal-plugin.md) 修订，双目录分流已被 [ADR-0018](0018-single-skills-directory.md) 取代。

2026-11-16 决定在 Codex 与 Claude Code 之外新增对 Antigravity 的支持，三端共用同一份 `plugins/letsgo/`，并在三端统一展示为 `letsgo:<名称>`（主入口保持 `letsgo`）。

- 新增原生清单 `plugins/letsgo/.antigravity-plugin/plugin.json`，只使用 Antigravity 允许的顶层字段，不依赖 `agy plugin install` 的 Claude Code 转换模式。
- 三端对技能名称的拼接规则不同：Antigravity 固定扫描 `skills/` 且不自动加插件名前缀；Claude Code 读取 `name: "letsgo:<名称>"` 时会自动去重，不会产生双倍前缀；Codex 无条件在 `name` 前拼接 `letsgo:`，但支持在 `.codex-plugin/plugin.json` 中指定 `"skills": "./skills-codex/"`。因此插件采用单包双目录分流：
  - `plugins/letsgo/skills/` 存放 `letsgo`（主入口）与 14 个 `letsgo:<名称>`，供 Antigravity 与 Claude Code 读取；
  - `plugins/letsgo/skills-codex/<名称>/` 存放 `name: <名称>` 的 `SKILL.md` 及同步副本供 Codex 读取（`codex plugin add` 归档时忽略符号链接，因此使用实体文件），由 `scripts/validate.py` 强制校验两边字节级一致。
- 新增 `plugins/letsgo/skills/_rules/references/hosts.md` 作为三端差异的唯一登记处，各技能入口引用它，不再各自重复书写宿主调用命令。
- Antigravity 识别 `SKILL.md` frontmatter 中的 `disable-model-invocation: true`；普通对话的通用规则仍由隐式技能 `conventions` 承载，不使用 Antigravity 插件的 `rules/AGENTS.md` 常驻规则，使三端行为保持一致。

## Considered Options

- **同时支持 Gemini CLI（`gemini-extension.json`）**：Gemini CLI 与 Antigravity 是不同产品，且 Gemini CLI 不保证识别 `disable-model-invocation`，会使显式技能暴露于隐式调用；本版只支持 Antigravity。
- **只用单个 `skills/` 目录**：若不加前缀，Antigravity 中显示裸名称（如 `/personal`），易与其他插件撞名；若直接加前缀而不为 Codex 分流，Codex 会显示为 `$letsgo:letsgo:personal`。
- **在 Antigravity 中使用 `rules/AGENTS.md` 常驻规则代替 `conventions`**：命中更稳，但每次对话固定载入，且三端承载机制分叉。

## Consequences

- 三端显式调用命令统一：主入口在 Antigravity 与 Claude Code 为 `/letsgo`（Claude Code 也可 `/letsgo:letsgo`）、在 Codex 为 `$letsgo:letsgo`（菜单显示 `letsgo`）；其余 14 个技能在 Antigravity 与 Claude Code 为 `/letsgo:<名称>`、在 Codex 为 `$letsgo:<名称>`。
- Antigravity 不识别 `user-invocable: false`，隐式技能 `letsgo:conventions` 可能出现在斜杠菜单中。
- `scripts/validate.py` 检查三份清单、`skills/` 与 `skills-codex/` 的同步一致性，并在本机装有 `agy` 时运行 `agy plugin validate --strict`。
