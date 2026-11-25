# 统一采用裸 x.y.z 版本号与制作期版本治理

修订 [ADR-0001](0001-publish-as-plugin.md) 中的 `vX.Y.Z` 标签规范，以及 [ADR-0005](0005-remove-worktree-rules.md)、[ADR-0017](0017-minimal-plugin.md)、[ADR-0018](0018-single-skills-directory.md)、[ADR-0019](0019-write-an-article-skill.md)、[ADR-0020](0020-matt-flow-skill.md)、[ADR-0022](0022-swarm-up-skill.md)、[ADR-0024](0024-matt-guide-skill.md)、[ADR-0025](0025-git-wrap-skill.md) 与 [ADR-0026](0026-0.0.8-skills-update.md) 中的历史版本号表述。

2026-11-25 决定全面规范 `letsgo` 插件的版本号格式、演进阶梯、变更权限红线及历史版本序列：

- **裸 `x.y.z` 格式统一**：插件三端清单（`plugin.json`）中的 `version`、市场锁定文件（`.claude-plugin/marketplace.json`、`.agents/plugins/marketplace.json`）中的 `ref` 以及 Git 发布标签，一律采用不带 `v` 前缀的裸 `x.y.z` 形式，彻底消除“版本号无 `v`、标签带 `v`”带来的对照与解析歧义。
- **制作期与 `1.0.0` 后演进规则**：当前插件处于制作期，版本从 `0.0.1` 起步并仅递增 `z`；仅当插件正式对外推荐使用或发布至外部技能平台时才定为 `1.0.0`。进入 `1.0.0` 后，`x` 对应重大架构、组织或品牌代际调整，`y` 对应开发期周期批次，`z` 对应同批次内功能与修复递增。
- **权限红线与机械门禁**：智能体仅被授权递增 `z`；任何对 `x` 或 `y` 的修改都必须事先取得维护者明确同意，并通过 `scripts/release.sh --allow-xy-bump x.y.z` 显式放行。未传入 `--allow-xy-bump` 时，`scripts/release.sh` 默认阻断任何 `x`、`y` 变动。结构校验器 `scripts/validate.py` 强制要求三端 `version` 为裸 `x.y.z` 且市场 `ref` 严格等于 `version`。
- **载荷隔离边界**：版本演进规则与发版治理流程属于仓库开发规范，只保存在仓库根级文档（`AGENTS.md`、`README.md`、`GLOSSARY.md`）与 `docs/` 下，严禁写入 `plugins/letsgo/` 插件运行时载荷。
- **历史版本重映射与版本重置对齐**：
  - 将八个历史决策版本节点按时间演进顺序重映射为 `0.0.1` 至 `0.0.8`：`ADR-0005`（原 `v1.0.8` → `0.0.1`）、`ADR-0017`（原 `3.0.0` → `0.0.2`）、`ADR-0018`（原 `3.1.0` → `0.0.3`）、`ADR-0019`（原 `3.1.1` → `0.0.4`）、`ADR-0020`（原 `3.2.0` → `0.0.5`）、`ADR-0022`（原 `3.3.0` → `0.0.6`）、`ADR-0024` / `ADR-0025`（原 `3.5.0` → `0.0.7`）、`ADR-0026`（原 `3.6.0` → `0.0.8`，文档重命名为 `0026-0.0.8-skills-update.md`）。
  - 将仓库身份迁移后原已发版本视为 `0.0.9`，本次版本治理落地发布为裸标签 `0.0.10`。
  - 发布 `0.0.10` 时同步删除本地与远端历史带 `v` 标签，并将本机三端客户端（Codex、Claude Code、Antigravity）卸载旧版本缓存后重装对齐至 `0.0.10`。

## Considered Options

- **继续保留 `vX.Y.Z` 标签与 `3.x` 序列，仅在文档中注明处于试用阶段**：容易误导外部读者以为已进入稳定大版本周期，且 `version` 与 `tag` 仍需人工或脚本做 `v` 前缀转换。
- **从本次起改用 `0.0.10` 但不重映射历史 ADR 中的 `v1.0.8` 与 `3.x`**：历史 ADR 与当前 `0.0.x` 序列断层，后续查阅演进脉络时无法对齐。
- **仅靠文档约束智能体不改 `x`、`y` 而不加发版脚本门禁**：长会话或跨工具执行时仍存在越权跳版本风险，必须由 `scripts/release.sh` 与 `scripts/validate.py` 提供机械阻断。

## Consequences

- `scripts/validate.py` 与 `scripts/release.sh` 按裸 `x.y.z` 与 `--allow-xy-bump` 门禁执行校验与发版，并由 `scripts/tests` 单元测试覆盖。
- 由于目标版本 `0.0.10` 数值低于此前已发布的 `3.6.0`，各端升级前若命中旧缓存，须先卸载旧缓存再重新安装并核验版本为 `0.0.10`。
- `AGENTS.md`、`docs/authoring.md`、`GLOSSARY.md`、`README.md` 及相关历史 ADR 同步更新，确保仓库内无旧版 `ADR-0026` 路径断链与旧标签规则残留。
