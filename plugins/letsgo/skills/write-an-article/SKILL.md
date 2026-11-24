---
name: "letsgo:write-an-article"
description: 仅在显式调用时，按用户给定的主题（未给主题时整理当前对话）生成一篇作为 Obsidian 笔记长期保存的文章。
disable-model-invocation: true
---

# letsgo: write an article

遵守[语言约定](../letsgo/references/language.md)；存放位置按[文件位置](../letsgo/references/file-paths.md)的“用户交付物”确定；其他规则按[letsgo 规则入口](../letsgo/SKILL.md)命中时读取。

生成一篇文章：一个作为 Obsidian 笔记长期保存的 Markdown 文件。

## 确定内容

1. 调用消息给出主题或要求时按它写；当前对话、本地文件与网页都可作为素材，资料不足时由智能体自行查找。
2. 没有主题时把当前对话整理成文章，并在回复中说明“按当前对话整理”；当前对话也没有实质内容时只问一句“写什么主题”。
3. 写之前不确认主题或大纲。

## 借助 Obsidian 技能

宿主中有以下技能时使用它们，没有时按括号内的方式处理；这些技能都无需用户手动触发。

- `obsidian-markdown`：写作前读取，properties、callout 与嵌入的写法以它为准（没有时只用标准 Markdown 加 properties）。
- `defuddle`：引用网页时用它抽取正文（没有时用宿主自带的网页读取）。

不使用 `obsidian-cli`、`obsidian-bases`、`json-canvas`、`obsidian-headless`：本技能不读取 vault 中的其他笔记；`.base` 与 `.canvas` 不是文章；同步和发布 vault 超出本技能范围。

## 格式

- 文件以 properties 开头，只写 `tags`、`created`（`YYYY-MM-DD`）；实际引用了网址时再写 `source`（网址列表）。
- properties 结束的 `---` 下一行直接是第一个一级标题，中间不空行；没有 properties 时文件第一行就是第一个一级标题。
- 文件名是主题的简短写法，只替换文件系统不允许的字符。Obsidian 会把文件名显示为页面标题，正文不再用一级标题重复文件名；一级标题直接作为文章章节。
- 标题编号固定四级，第五级及以下不编号：

  ```markdown
  # 一、标题
  ## 1、标题
  ### (1) 标题
  #### ① 标题
  ```

- 章节按主题自行组织；最后一个一级章节总结要点，标题按内容取（如“要点”“结论”“小结”）。

## 内容要求

- 不编造；推断要标明是推断。整理对话时只写有依据的内容，分清已完成、已验证与未决事项。
- 密码、令牌、私钥、Cookie 等凭据不写进文章，需要提及时写“敏感信息已省略”；私人资料中的信息只在主题确实需要时写入。
- 默认只新建文件，不修改已有笔记；用户明确指定某篇笔记时才更新它，并遵守[变更安全](../letsgo/references/change-safety.md)。
- 不读取、不搜索存放目录或 vault 中的其他笔记，文章中也不写指向其他笔记的 wikilink；外部资料用普通网址引用。例外只有：检查目标目录中是否有同名文件（只看文件名）、读取用户明确指定要更新的笔记、读取用户调用时点名作为素材的文件。

## 完成

报告文件路径与一级章节列表。使用了插件默认目录时，提示用户可在 letsgo 私人资料中设置自己的 Obsidian 笔记目录。
