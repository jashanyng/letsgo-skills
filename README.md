# letsgo-skills

本仓库开发同一份供 Codex、Claude Code 与 Antigravity 使用的 `letsgo` 插件。插件只由技能组成，不使用事件钩子；使用者通过各客户端安装与更新插件，无需运行仓库脚本。

## 安装与更新

| 宿主 | 添加市场 | 安装插件 | 更新插件 |
| --- | --- | --- | --- |
| Codex 桌面／CLI | `codex plugin marketplace add jashanyng/letsgo-skills` | `codex plugin add letsgo@letsgo-skills` | `codex plugin marketplace upgrade letsgo-skills`，再 `codex plugin add letsgo@letsgo-skills` |
| Claude Code | `claude plugin marketplace add jashanyng/letsgo-skills` | `claude plugin install letsgo@letsgo-skills` | `claude plugin marketplace update letsgo-skills`，再 `claude plugin update letsgo@letsgo-skills` |
| Antigravity | 不适用 | `agy plugin install <插件目录>`（指向检出发布标签下的 `plugins/letsgo`） | 重新运行 `agy plugin install <插件目录>` |

安装或更新后开启新会话。

## 技能

| 技能 | Claude Code 与 Antigravity | Codex | 作用 |
| --- | --- | --- | --- |
| `letsgo` | 隐式，按场景自动选用 | 隐式 | 基础规则、共用规则与用户级规则：语言、私人资料与远程连接、浏览器、代码输出、文件位置、变更安全、故障报告；用户说“更新我的 letsgo 私人资料：……”时在 `~/.agents/letsgo/personal/` 创建或更新分类私人资料 |
| `stepping-begin` | `/letsgo:stepping-begin` | `$letsgo:letsgo:stepping-begin` | 把需求当作明确需求，建立步进会话并给出第一步 |
| `stepping-doit` | `/letsgo:stepping-doit` | `$letsgo:letsgo:stepping-doit` | 由智能体执行当前步骤，并展示下一步 |
| `stepping-finish` | `/letsgo:stepping-finish` | `$letsgo:letsgo:stepping-finish` | 由智能体完成全部剩余步骤 |
| `write-an-article` | `/letsgo:write-an-article` | `$letsgo:letsgo:write-an-article` | 按主题（未给主题时整理当前对话）生成一篇作为 Obsidian 笔记的文章，存放到私人资料指定的目录 |
| `matt-flow` | `/letsgo:matt-flow` | `$letsgo:letsgo:matt-flow` | 写在消息开头、后接需求（Antigravity 只识别开头的命令），借助 `ask-matt` 现场评估并推荐适合的 mattpocock-skills 技能或技能组合，自动串联无需判断的步骤，在门禁处给出可直接使用的提示词；需已安装 mattpocock-skills |
| `prove-it` | `/letsgo:prove-it` | `$letsgo:letsgo:prove-it` | 对当前改动现场评估适合的测试验收层度与方法，给出推荐、轻量、深度三个选项供用户选择后实施 |
| `guide` | `/letsgo:guide` | `$letsgo:letsgo:guide` | 按需求在能力范围或当前宿主全部能力中现场评估适合的 skill、MCP 与内置工具，推进实施、为需显式调用的技能给出可复制代码块提示词（调用时显式授权可代为执行），或在缺失支持时检索宿主市场只报告不安装 |
| `try-swarm` | `/letsgo:try-swarm` | `$letsgo:letsgo:try-swarm` | 评估当前需求是否适合采用宿主原生多智能体协同（Codex `multi_agent_v2`、Claude Code `Agent Teams`、Antigravity `swarm`），适合时采用、不适合时不采用，不干预任务执行节奏 |
| `git-wrap` | `/letsgo:git-wrap` | `$letsgo:letsgo:git-wrap` | 全部任务完成后，仅在显式调用时对涉及的所有 Git 仓库执行英文提交、工作树或任务临时分支向源分支的安全合并与推送，并按安全门槛评估清理工作树与临时分支 |

Codex 总在技能名前加插件名，所以 stepping 在 Codex 中多一层 `letsgo:`；菜单仍显示为 `letsgo: stepping begin` 等，输入 `$stepping` 即可找到。`letsgo` 是隐式技能，命中不能保证每次触发；它在 Claude Code 斜杠菜单中隐藏，Codex 与 Antigravity 没有隐藏机制，手动提到它时只会加载规则。私人资料只保存在用户本机，安装本身不创建任何用户目录。

## 开发与发布

只在本开发副本修改插件；规范见 [docs/authoring.md](docs/authoring.md)。作者运行 `python3 scripts/validate.py` 校验，使用 `scripts/release.sh x.y.z` 发布版本。版本更新记录见 [CHANGELOG.md](CHANGELOG.md)，三端兼容矩阵、演进契约与升级迁移步骤见 [docs/compatibility.md](docs/compatibility.md)。
