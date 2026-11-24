# 问题追踪器：GitHub

本仓库的 Issue 与规格说明均作为 GitHub Issues（`jashanyng/letsgo-skills`）托管。所有操作请使用 `gh` CLI。

## 操作规范

- **创建 Issue**：`gh issue create --title "..." --body "..."`。多行正文请使用 heredoc。
- **读取 Issue**：`gh issue view <number> --json number,title,body,labels,comments`。
- **列出 Issue**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，并按需搭配 `--label` 与 `--state` 过滤条件。
- **将 Issue 设为父 Issue 的子 Issue**：使用 `gh issue create --parent <parent> ...`，或事后执行 `gh issue edit <parent> --add-sub-issue <child>`（需 `gh` 2.94+）。旧版 `gh` 使用：`gh api --method POST repos/<owner>/<repo>/issues/<parent>/sub_issues -F sub_issue_id=<child-db-id>`（这里的数据库 ID 获取方式见下方**阻塞关系**）。若未启用 sub-issues，则在子 Issue 正文顶部添加 `Part of #<parent>`。
- **阻塞关系（Blocking）**：优先使用 GitHub 原生的 **issue dependencies**（在界面中可见的标准依赖关系）。通过 `gh issue create --blocked-by <n>,<n> ...` 或 `gh issue edit <child> --add-blocked-by <blocker>`（需 `gh` 2.94+）添加依赖边。旧版 `gh` 使用：`gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`，其中 `<blocker-db-id>` 为阻塞方的数字**数据库 ID**（通过 `gh api repos/<owner>/<repo>/issues/<n> --jq .id` 获取，_而非_ `#number` 或 `node_id`）。若原生依赖不可用，则退化为在子 Issue 正文顶部写一行 `Blocked by: #<n>, #<n>`。当所有阻塞方均已关闭时，该任务即解除阻塞。
- **统计未关闭的阻塞项数量**：`gh api repos/<owner>/<repo>/issues/<n> --jq .issue_dependencies_summary.blocked_by`（仅统计 open 状态的阻塞项；为 0 表示可开始）。注意 `gh issue view <n> --json blockedBy` 也会包含已关闭的阻塞项，需过滤：`--jq '[.blockedBy.nodes[] | select(.state == "OPEN")] | length'`。
- **评论 Issue**：`gh issue comment <number> --body "..."`
- **添加 / 移除标签**：`gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **关闭 Issue**：先用 `gh issue comment <number> --body "..."` 发表关闭说明，再执行 `gh issue close <number>`。注意若 Issue 已关闭，`gh issue close --comment` 会丢弃评论但仍返回退出码 0。

仓库信息由 `git remote -v` 自动推断；在本地克隆目录中运行 `gh` 会自动识别。

只向用户自己的仓库（`jashanyng/letsgo-skills`）提交 Issue。除非用户本人拥有 `mattpocock/skills`，否则绝不要向该仓库提交 Issue。在 fork 仓库中，`gh` 可能会默认指向上游父仓库，因此在每次会话首次执行 `gh issue create` 前，先用 `gh repo view --json nameWithOwner` 检查目标仓库；若不是用户自己的仓库，需先与用户确认。

## 将 Pull Request 作为分流入口（Triage Surface）

**PRs as a request surface: no.** _（如果本仓库将外部 PR 视为功能请求，请将其改为 `yes`；`/triage` 会读取该标记。）_

当设置为 `yes` 时，PR 将与 Issue 走相同的标签与状态流转，使用对应的 `gh pr` 命令：

- **读取 PR**：先执行 `gh pr view <number>`，再执行 `gh pr view <number> --comments`（非 TTY 环境下 `--comments` 仅打印评论而不含正文），需要查看变更时执行 `gh pr diff <number>`。
- **列出待分流的外部 PR**：`gh api --paginate 'repos/{owner}/{repo}/pulls?state=open' --jq '.[] | select(.author_association | IN("OWNER","MEMBER","COLLABORATOR") | not) | {number, title, author: .user.login, author_association, labels: [.labels[].name]}'`。
- **评论 / 打标签 / 关闭**：`gh pr comment`、`gh pr edit --add-label` / `--remove-label`、`gh pr close`。

GitHub 的 Issue 和 PR 共用同一套编号空间，因此单独的 `#42` 可能是其中任意一种：可先用 `gh pr view 42` 解析，失败后再回退到 `gh issue view 42`。

## 当技能要求“发布到问题追踪器（publish to the issue tracker）”时

创建一个 GitHub Issue。

## 当技能要求“获取相关工单（fetch the relevant ticket）”时

按上文**读取 Issue** 的方式读取。

## Wayfinding 操作

供 `/wayfinder` 使用。**地图（map）** 是一个主 Issue，其**子 Issue** 作为具体任务票（tickets）。

- **Map**：单个带有 `wayfinder:map` 标签的 Issue，正文记录 Notes / Decisions-so-far / Fog。使用 `gh issue create --label wayfinder:map` 创建。
- **子任务票（Child ticket）**：作为 GitHub sub-issue 关联到 map（参见**将 Issue 设为父 Issue 的子 Issue**）。若未启用 sub-issues，则将子任务加入 map 正文的任务列表中，并在子任务正文顶部标注 `Part of #<parent>`。标签格式为 `wayfinder:<type>`（`research` / `prototype` / `grilling` / `task`）。认领后将任务指派给推进开发的开发者。
- **阻塞关系**：参见上文**操作规范**中的**阻塞关系（Blocking）**。
- **前沿任务查询（Frontier query）**：列出 map 下所有未关闭的子任务（`gh issue list --state open`，限定在 map 的 sub-issues / 任务列表范围内），剔除存在未关闭阻塞项（参见**统计未关闭的阻塞项数量**，或 `Blocked by` 行中仍有 open 状态的 Issue）或已有指派人的任务；按 map 中的顺序取第一个。
- **认领（Claim）**：`gh issue edit <n> --add-assignee @me`，作为该会话的首次写入操作。
- **解决（Resolve）**：先 `gh issue comment <n> --body "<answer>"`，再 `gh issue close <n>`，最后将上下文摘要（要点 + 链接）追加到 map 的 Decisions-so-far 中。
