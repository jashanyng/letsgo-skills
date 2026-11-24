# 文件位置

用户本轮指定的路径、服务要求的固定位置优先；已有文件不因本规则迁移。同名冲突先核对，不静默覆盖。

## 短期文件

在执行任务的主机（本机或远程）上，`~` 指目标登录用户的家目录，单条命令使用 `sudo` 不改变这一基准。

| 文件 | 位置 |
| --- | --- |
| 临时文件、未确认候选、下载的安装包、脚本执行副本 | `~/tmp/<任务>/` |
| 替换前备份、回滚包 | `~/backups/<任务>/` |

临时文件在验证后按需清理；备份保留到恢复窗口结束，报告实际路径。含敏感数据的文件只给必要主体访问权限。家目录只读、空间不足或位于小容量闪存（如 OpenWrt overlay）时：临时文件可放 `/tmp/<任务>/`（可能重启即清空）；备份只放已核实的持久位置，没有时拉回本机 `~/backups/<主机>-<任务>/`。报告替代位置及原因。

## 用户交付物

在发起会话的本机长期保存、供用户直接使用的结果：可复用脚本放 `~/.agents/letsgo/generated/scripts/`，图表、报告等放 `~/.agents/letsgo/generated/product/<任务>/`。私人资料 `outputs.md` 记录了对应默认位置时以它为准。

文章（作为 Obsidian 笔记保存的 Markdown）依次取：用户本轮指定的目录、`outputs.md` 记录的 Obsidian 笔记目录、`~/.agents/letsgo/generated/product/articles/`。同名文件已存在时在文件名后追加序号，不覆盖。

## 长期服务文件

优先遵循目标系统、包管理器、容器平台或现有服务的布局。没有既有布局时：

| 文件 | 位置 |
| --- | --- |
| Linux 手工部署的应用、可执行文件、Compose 文件 | `/opt/<服务>/`；对外站点数据可放 `/srv/<服务>/` |
| Linux 配置与持久状态 | `/etc/<服务>/`、`/var/lib/<服务>/` 或已核实的数据卷 |
| systemd 系统／用户单元 | `/etc/systemd/system/`／`~/.config/systemd/user/` |
| OpenWrt 配置与启动脚本 | `/etc/config/`／`/etc/init.d/` |
| macOS LaunchAgent／LaunchDaemon | `~/Library/LaunchAgents/`／`/Library/LaunchDaemons/` |

持续运行的脚本属于服务部署，不放在临时目录。
