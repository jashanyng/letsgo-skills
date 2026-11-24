# 领域文档（Domain Docs）

工程技能在探索本仓库代码库时，应按以下规则读取领域文档。

## 探索代码前先读这些文件

- 仓库根目录的 **`GLOSSARY.md`**，或
- 若根目录存在 **`GLOSSARY-MAP.md`**：它指向各个上下文的 `GLOSSARY.md`，请按需读取与当前主题相关的术语表。
- **`docs/adr/`**：阅读与你即将修改的区域相关的 ADR（架构决策记录）。在多上下文（multi-context）仓库中，还应检查 `src/<context>/docs/adr/` 中的上下文级决策。

如果上述文件不存在，**请静默继续**。不要提示缺失，也不要主动建议预先创建。当术语或架构决策真正敲定时，`/domain-modeling` 技能（通过 `/grill-with-docs` 和 `/improve-codebase-architecture` 触发）会按需懒创建它们。

## 文件结构

单上下文（Single-context）仓库（绝大多数仓库）：

```
/
├── GLOSSARY.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

多上下文（Multi-context）仓库（根目录存在 `GLOSSARY-MAP.md`）：

```
/
├── GLOSSARY-MAP.md
├── docs/adr/                          ← 系统级决策
└── src/
    ├── ordering/
    │   ├── GLOSSARY.md
    │   └── docs/adr/                  ← 上下文级决策
    └── billing/
        ├── GLOSSARY.md
        └── docs/adr/
```

## 使用术语表中的词汇

当你的输出涉及领域概念（如 Issue 标题、重构方案、假设、测试名称）时，请使用 `GLOSSARY.md` 中定义的标准术语，不要擅自替换为术语表明确避免的同义词。

如果你需要的概念尚未收录在术语表中，这是一个信号：要么你引入了项目并不使用的说法（需重新斟酌），要么确实存在术语空白（记录下来留待 `/domain-modeling` 处理）。

## 标出 ADR 冲突

如果你的方案与现有 ADR 相矛盾，请明确指出，不要静默覆盖：

> _与 ADR-0007（事件溯源订单）冲突，但值得重新讨论，因为……_
