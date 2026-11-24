# 生成目录只放用户交付物，短期文件留在执行主机

2026-11-02 决定 `~/.agents/letsgo/generated/` 只保存用户交付物（`scripts/` 与 `product/<任务>/`）。临时文件、候选、安装包、执行副本、备份与回滚包都是短期文件，无论执行主机是本机还是远程主机，都放在目标用户的 `~/tmp/<任务>/` 与 `~/backups/<任务>/`。家目录不适合时（小容量闪存、只读、空间不足或没有可用家目录），由 Agent 评估替代位置并报告：临时文件可用 `/tmp`，备份只放持久位置，必要时拉回本机。此决策修订 [ADR-0008](0008-plugin-runtime-and-personal-context.md) 中的生成物位置。

此前本机短期文件放在 `generated/{tmp,backups}`，远程放在 `~/data/{scripts,backups,rollbacks,installer,tmp}`，两套路径并存，生成目录也因此堆积了与交付无关的过程文件。统一后，用户在 letsgo 目录里只看到需要长期保留的结果，各主机上的短期文件位置也一致。

## 取舍与后果

- 插件不迁移已有文件；旧的 `generated/tmp`、`generated/backups` 与远程 `~/data/...` 由用户按需另行处理。
- `~/tmp/`、`~/backups/` 不带 letsgo 前缀，与用户其他文件共处；依靠按任务分目录和“同名冲突先核对、不覆盖”避免冲突。
- 长期服务文件仍遵循目标系统与服务的既有布局。
