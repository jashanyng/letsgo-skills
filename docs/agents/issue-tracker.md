# Issue 追踪器：GitHub

本仓库的 Issue 与规格说明（spec）均保存在 GitHub Issues（`pcfprio/letsgo-skills`）。所有操作均使用 `gh` CLI。

## 操作约定

- **创建 Issue**：`gh issue create --title "..." --body "..."`。多行正文请使用 heredoc。
- **读取 Issue**：`gh issue view <number> --json number,title,body,labels,comments`。
- **列出 Issue**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，并按需搭配 `--label` 与 `--state` 过滤。
- **将 Issue 设为父 Issue 的子 Issue**：`gh issue create --parent <parent> ...`，或事后执行 `gh issue edit <parent> --add-sub-issue <child>`（需要 `gh` 2.94+）。旧版 `gh` 可使用 `gh api --method POST repos/<owner>/<repo>/issues/<parent>/sub_issues -F sub_issue_id=<child-db-id>`（这里的 id 为数据库 id，见下文**阻塞关系**）。若环境不支持子 Issue，则在子 Issue 正文顶部加上 `Part of #<parent>`。
- **评论 Issue**：`gh issue comment <number> --body "..."`
- **添加 / 移除标签**：`gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **关闭 Issue**：`gh issue close <number> --comment "..."`

仓库信息由 `git remote -v` 自动推断；在本地克隆目录中执行 `gh` 时会自动识别。

## 将 Pull Request 作为分流入口（Triage Surface）

**是否将 PR 作为需求入口：no。** _（如果本仓库将外部 PR 视为功能需求，请改为 `yes`；`/triage` 会读取此标记。）_

当设置为 `yes` 时，PR 与 Issue 共用相同的标签与状态流转，使用对应的 `gh pr` 命令：

- **读取 PR**：`gh pr view <number> --comments`，查看变更差异使用 `gh pr diff <number>`。
- **列出待分流的外部 PR**：`gh api --paginate 'repos/{owner}/{repo}/pulls?state=open' --jq '.[] | select(.author_association | IN("OWNER","MEMBER","COLLABORATOR") | not) | {number, title, author: .user.login, author_association, labels: [.labels[].name]}'`。
- **评论 / 打标签 / 关闭**：`gh pr comment`、`gh pr edit --add-label`/`--remove-label`、`gh pr close`。

GitHub 的 Issue 与 PR 共用同一套编号空间，因此单独的 `#42` 可能是其中任意一种：先尝试 `gh pr view 42`，失败再回退到 `gh issue view 42`。

## 当技能要求“发布到 issue tracker”时

创建一个 GitHub Issue。

## 当技能要求“获取相关 ticket”时

按上文**读取 Issue** 的方式读取。

## Wayfinding 操作约定

供 `/wayfinder` 使用。**地图（map）** 是一个主 Issue，其**子 Issue（child）** 作为具体的 ticket。

- **地图（Map）**：带有 `wayfinder:map` 标签的单个 Issue，正文记录 Notes / Decisions-so-far / Fog。创建命令：`gh issue create --label wayfinder:map`。
- **子 Ticket（Child ticket）**：作为 GitHub 子 Issue 关联到地图（见上文**将 Issue 设为父 Issue 的子 Issue**）。若未启用子 Issue 功能，则将子 Issue 列入地图正文的任务列表中，并在子 Issue 正文顶部加上 `Part of #<map>`。标签使用 `wayfinder:<type>`（`research` / `prototype` / `grilling` / `task`）。认领后，将该 ticket 指派给当前负责的开发者。
- **阻塞关系（Blocking）**：使用 GitHub **原生 Issue 依赖关系**作为权威且在界面可见的表示方式。通过 `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>` 添加依赖边，其中 `<blocker-db-id>` 是阻塞方 Issue 的数字**数据库 id**（通过 `gh api repos/<owner>/<repo>/issues/<n> --jq .id` 获取，**不是** `#number` 或 `node_id`）。GitHub 会返回 `issue_dependencies_summary.blocked_by`（仅统计未关闭的阻塞项，作为实时门控）。若原生依赖不可用，则在子 Issue 正文顶部回退使用 `Blocked by: #<n>, #<n>`。当所有阻塞方都关闭时，该 ticket 解除阻塞。
- **前沿查询（Frontier query）**：列出地图下所有未关闭的子 Issue（`gh issue list --state open`，范围限定在地图的子 Issue / 任务列表内），过滤掉存在未关闭阻塞项（`issue_dependencies_summary.blocked_by > 0`，或 `Blocked by` 行中仍有未关闭 Issue）以及已有指派人的条目；按地图中的顺序取第一个。
- **认领（Claim）**：`gh issue edit <n> --add-assignee @me`，作为会话的第一次写入操作。
- **解决（Resolve）**：先执行 `gh issue comment <n> --body "<answer>"`，再执行 `gh issue close <n>`，最后在地图正文的 Decisions-so-far 中追加一条上下文指针（摘要 + 链接）。
