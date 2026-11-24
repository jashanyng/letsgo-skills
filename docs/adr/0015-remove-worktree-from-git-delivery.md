# 移除插件中的工作树规则，简化 Git 收尾

> 状态：移除工作树规则的结论继续有效；非初始分支自动合并回原分支与无条件执行的规定已由 [ADR-0021](0021-conditional-git-delivery.md) 修订；插件包不出现工作树的限制已由 [ADR-0025](0025-git-wrap-skill.md) 为显式技能 `git-wrap` 修订；不设隐式工作树规则的结论继续有效。

取代 [ADR-0006](0006-conditional-worktree-delivery.md)，并修订 [ADR-0014](0014-git-delivery-after-changes.md) 中关于独立工作树的部分。2026-11-16 决定从 letsgo 插件中移除全部工作树相关规则与文件（`linked-worktree-delivery.md`），插件包不再出现“工作树／worktree”。

Git 收尾（`_rules/spec/references/git-delivery.md`）简化为两种工作位置：

- **初始分支**：本轮开始时已检出、且未另建分支的分支；提交后推送。
- **非初始分支**：本轮另建了分支（不论在哪个检出目录中工作）；推送当前分支，再合并回创建它时所在的原分支并推送原分支，当前分支保留。

停止情形保留六条（原分支无法确定、合并冲突、仓库要求 PR 或分支受保护、本轮改动与既有改动无法区分、差异可能含秘密、推送被拒）。

## Considered Options

- **仅在当前分支提交推送，不合并回原分支**：原分支得不到本轮成果，仍需用户手工合并。
- **插件完全不管非初始分支**：违背 ADR-0014 由智能体直接完成收尾的长期指示。

## Consequences

- `GLOSSARY.md` 移除“源检出目录、源分支、工作分支”三个只服务于工作树流程的术语。
- `scripts/validate.py` 拒绝插件包中再次出现“工作树”或 `worktree`。
