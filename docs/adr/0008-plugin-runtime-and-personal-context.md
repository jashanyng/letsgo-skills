# 插件自带运行规则，私人资料留在用户本机

> 生成物位置已由 [ADR-0009](0009-short-term-files-on-execution-host.md) 修订；钩子注入规则的部分已由 [ADR-0010](0010-no-hooks-skills-carry-rules.md) 取代，`letsgo:setup` 同时更名为 `letsgo:personal`；私人资料的单文件位置与全局门禁已由 [ADR-0011](0011-classified-personal-context-and-task-gates.md) 取代。

2026-10-30 决定让 Codex 与 Claude Code 通过安装并使用插件获得全部功能：插件的 `SessionStart` 钩子为普通对话提供规则入口和通用路由，技能相对读取同一安装副本中的资料。Claude Code 与 Codex 使用各自支持的钩子配置，合用只读的会话脚本。私人事实统一由当前用户的 `~/.agents/letsgo/personal.md` 保存，`letsgo:setup` 仅显式整理它；插件包没有主机快照或任何用户的资产资料。此决策取代 [ADR-0003](0003-no-bundled-host-snapshots.md) 的快照事实来源、[ADR-0007](0007-hidden-rules-and-host-registration.md) 的随包私人登记与安装脚本同步规则，并修正 [ADR-0001](0001-publish-as-plugin.md) 的旧生成物位置。

旧方式要求每台机器运行开发仓库的安装脚本来复制规则和改写全局入口，插件更新本身无法更新这些规则；随包私人登记也不适合对外分发。新的资料入口由钩子按当前安装路径提供，不写全局入口或规则副本。用户首次显式设置之前，其他 letsgo 技能停下；普通对话仍可使用通用规则。主机的易变状态在任务现场实时只读核验，`personal.md` 只保存用户可阅读和维护的背景。

## 取舍与后果

- 本版验收 Codex 桌面手动安装与 Claude Code GitHub 市场安装，首版支持 macOS、Linux 和 WSL。Codex 的插件钩子需用户审阅并信任；禁用钩子时，普通对话的自动规则命中不保证生效，显式技能仍有自身入口门禁。
- 本机生成物移到 `~/.agents/letsgo/generated/`，远程短期文件在目标用户家目录下按任务存放；长期服务文件遵循目标系统与服务布局。
- 现有私有开发仓库保留历史。将来对外公开时，从净化后的内容创建全新历史的发行仓库；旧提交与标签不进入公开仓库。
