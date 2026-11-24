# 移除 Git 收尾规则

> 状态：不内置隐式默认 Git 收尾规则的结论继续有效；终局按需收尾由显式技能 `git-wrap` 提供（[ADR-0025](0025-git-wrap-skill.md)）。

取代 [ADR-0014](0014-git-delivery-after-changes.md)、[ADR-0015](0015-remove-worktree-from-git-delivery.md) 与 [ADR-0021](0021-conditional-git-delivery.md) 中保留 `Git 收尾` 的决定。

2026-11-22 决定从 `letsgo` 插件中彻底移除 `Git 收尾`（`plugins/letsgo/skills/letsgo/references/git-delivery.md`）及其在 `letsgo`、`stepping`、`matt-flow`、`swarm-up`、`README.md` 与 `GLOSSARY.md` 中的全部引用。何时提交、合并或推送完全交由用户指令、宿主或具体开发技能决定，插件不再内置默认的 Git 提交与推送规则。
