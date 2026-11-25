---
name: letsgo
description: "letsgo 基础规则与私人资料。用于：打开网页、操作浏览器或做浏览器验收；输出 Shell 命令集或 SQL；在本机或远程主机生成、下载、备份文件或部署服务文件；覆盖或删除已有产物；操作用户自己的主机、SSH、域名或家庭／公司网络；涉及科学上网或 webshare／住宅 IP；故障修复后报告；用户要求创建或更新自己的 letsgo 私人资料（主机、SSH、域名、网络、默认产出位置）。"
user-invocable: false
metadata:
  short-description: "letsgo 基础规则、共用规则与私人资料"
---

# letsgo

宿主按场景自动选用本技能；它不用于显式调用，也不启动其他 letsgo 技能。规则资料以本技能所在插件副本的相对路径读取，只读取本次命中的条件，命中多个时分别读取。

| 条件 | 读取 |
| --- | --- |
| 始终 | [语言约定](references/language.md) |
| 需要用户自己的主机、SSH、域名、私人网络或默认产出位置；执行远程命令；涉及科学上网或 webshare／住宅 IP | [私人资料与远程连接](references/personal-context.md) |
| 用户要求创建或更新自己的 letsgo 私人资料 | [私人资料设置](references/personal.md) |
| 打开网页、与页面交互或做浏览器验收 | [浏览器入口](references/browser.md) |
| 输出源代码、Shell 命令集或 SQL | [代码输出](references/output.md) |
| 在本机或远程主机产生临时文件、备份或用户交付物，或部署长期服务文件 | [文件位置](references/file-paths.md) |
| 覆盖、替换或删除已有产物；以附件、旧文件或脚本输出为依据 | [变更安全](references/change-safety.md) |
| 完成故障修复后报告 | [故障报告](references/fault-report.md) |

缺少私人资料不阻止普通对话。`references/stepping/` 只供 `stepping-*` 技能读取，`references/matt-route.md` 只供 `matt-flow` 读取。
