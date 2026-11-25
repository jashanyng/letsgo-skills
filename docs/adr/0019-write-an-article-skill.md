# 新增显式技能 write-an-article

修订 [ADR-0017](0017-minimal-plugin.md) 与 [ADR-0018](0018-single-skills-directory.md) 中“插件只有 4 个技能”的部分。

2026-11-20 决定新增显式技能 `write-an-article`（`name: "letsgo:write-an-article"`，菜单显示 `letsgo: write an article`），生成一篇作为 Obsidian 笔记长期保存的文章。插件技能变为 `letsgo`、`stepping-begin`、`stepping-doit`、`stepping-finish`、`write-an-article` 五个。

- 只允许显式调用；有主题按主题写，没有主题时整理当前对话，对话也没有实质内容时只问一句主题。写前不确认主题或大纲，与 stepping 把需求当作明确需求的做法一致。
- 文章格式：只写 `tags`、`created`（及实际引用时的 `source`）properties，结束的 `---` 下一行紧接第一个一级标题；正文不用一级标题重复文件名，一级标题直接作为章节；标题编号固定四级（`一、`、`1、`、`(1)`、`①`），第五级及以下不编号。
- 存放位置写在共用规则 `file-paths.md`：用户本轮指定 → 私人资料 `outputs.md` 的 Obsidian 笔记目录 → `~/.agents/letsgo/generated/product/articles/`。
- 宿主装有 obsidian-skills 时按条件使用 `obsidian-markdown` 与 `defuddle`，不列为依赖，没装时退回基本做法；`obsidian-cli`、`obsidian-bases`、`json-canvas`、`obsidian-headless` 不使用。它们都可由智能体直接调用，无需用户手动触发。

2026-11-21 修订：不再读取、搜索或链接 vault 中的其他笔记，因此也不再使用 `obsidian-cli`。原因是查找相关笔记太耗时。仍允许检查同名文件、读取用户指定要更新的笔记和用户点名作为素材的文件。

## Considered Options

- **恢复 0.0.2 删除的 `obsidian-note`**：它依赖已废除的分类概念与写前确认，与当前“直接执行明确需求”的方向冲突。
- **作为 `letsgo` 隐式技能的一条规则**：普通的笔记请求也会命中，无法保证只在用户点名时生成文章。
- **把 obsidian-skills 登记为第三方依赖**：ADR-0017 已废除第三方技能登记；按“装了就用”引用即可。

## Consequences

- 按用户要求发布为 0.0.4（新增功能，但不破坏已有调用）。
- `scripts/validate.py` 的 `EXPECTED_SKILLS` 加入 `write-an-article`；非 stepping 的显式技能只要求链接语言约定。
