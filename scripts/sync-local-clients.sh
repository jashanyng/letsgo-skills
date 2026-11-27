#!/bin/sh
# 同步并核验本机 Codex、Claude Code 与 Antigravity 已安装的 letsgo 插件版本与仓库清单一致。
# 用法：scripts/sync-local-clients.sh [--check-only]
# 环境变量（均可选，用于指定仓库目录或替换三端 CLI 可执行文件）：
#   LETSGO_REPO_ROOT  仓库根目录（默认取脚本所在目录的上一级）
#   CODEX_BIN         Codex CLI 命令或路径（默认 codex；设为空字符串表示跳过）
#   CLAUDE_BIN        Claude Code CLI 命令或路径（默认 claude；设为空字符串表示跳过）
#   AGY_BIN           Antigravity CLI 命令或路径（默认 agy；设为空字符串表示跳过）

set -eu

CHECK_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --check-only)
      CHECK_ONLY=1
      ;;
    *)
      printf '用法：scripts/sync-local-clients.sh [--check-only]\n' >&2
      exit 1
      ;;
  esac
done

REPO_ROOT=${LETSGO_REPO_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}
MANIFEST="$REPO_ROOT/plugins/letsgo/.claude-plugin/plugin.json"
VERSION=$(python3 -B -c 'import json, sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")).get("version", ""))' "$MANIFEST")

if ! printf '%s\n' "$VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  printf '错误：清单版本号无效：%s\n' "$VERSION" >&2
  exit 1
fi

resolve_bin() {
  raw=$1
  [ -n "$raw" ] || return 1
  case "$raw" in
    */*) [ -x "$raw" ] && printf '%s\n' "$raw" ;;
    *) command -v "$raw" 2>/dev/null ;;
  esac
}

extract_version() {
  python3 -B -c '
import re
import sys

client = sys.argv[1]
text = sys.stdin.read()

if client == "codex":
    for line in text.splitlines():
        m = re.match(r"^letsgo@letsgo-skills\s+installed\b[^0-9]*([0-9]+\.[0-9]+\.[0-9]+)\b", line)
        if m:
            print(m.group(1))
            sys.exit(0)
elif client == "claude":
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if "letsgo@letsgo-skills" in line:
            for sub in lines[idx + 1 : idx + 5]:
                m = re.search(r"Version:\s*([0-9]+\.[0-9]+\.[0-9]+)\b", sub)
                if m:
                    print(m.group(1))
                    sys.exit(0)
            print("unknown")
            sys.exit(0)
elif client == "agy":
    for line in text.splitlines():
        m = re.match(r"^-\s+letsgo\s+\([^)]*?\b([0-9]+\.[0-9]+\.[0-9]+)\b", line)
        if m:
            print(m.group(1))
            sys.exit(0)
' "$1"
}

FAILURES=""
record_failure() {
  label=$1
  if [ -z "$FAILURES" ]; then
    FAILURES=$label
  else
    FAILURES="$FAILURES, $label"
  fi
}

list_client() {
  client=$1
  bin=$2
  case "$client" in
    codex) "$bin" plugin list --marketplace letsgo-skills 2>&1 ;;
    claude) "$bin" plugin list 2>&1 ;;
    agy) "$bin" plugin list 2>&1 ;;
  esac
}

update_client() {
  client=$1
  bin=$2
  case "$client" in
    codex) "$bin" plugin marketplace upgrade letsgo-skills >/dev/null && "$bin" plugin add letsgo@letsgo-skills >/dev/null ;;
    claude) "$bin" plugin marketplace update letsgo-skills >/dev/null && "$bin" plugin update letsgo@letsgo-skills >/dev/null ;;
    agy) "$bin" plugin install "$REPO_ROOT/plugins/letsgo" >/dev/null ;;
  esac
}

sync_client() {
  client=$1
  label=$2
  raw_bin=$3
  plugin_name=$4

  if ! bin=$(resolve_bin "$raw_bin"); then
    printf '%s：跳过（未安装 CLI）\n' "$label"
    return 0
  fi
  if ! list_out=$(list_client "$client" "$bin"); then
    printf '%s：失败（无法列出插件：%s）\n' "$label" "$list_out" >&2
    record_failure "$label"
    return 0
  fi
  installed_ver=$(printf '%s\n' "$list_out" | extract_version "$client")
  if [ -z "$installed_ver" ]; then
    printf '%s：跳过（尚未安装 %s）\n' "$label" "$plugin_name"
    return 0
  fi
  if [ "$CHECK_ONLY" -eq 0 ]; then
    if ! update_client "$client" "$bin"; then
      printf '%s：失败（更新或安装命令执行失败）\n' "$label" >&2
      record_failure "$label"
      return 0
    fi
    list_out=$(list_client "$client" "$bin") || true
    installed_ver=$(printf '%s\n' "$list_out" | extract_version "$client")
  fi
  if [ "$installed_ver" != "$VERSION" ]; then
    printf '%s：失败（当前版本 %s != 目标版本 %s）\n' "$label" "${installed_ver:-unknown}" "$VERSION" >&2
    record_failure "$label"
    return 0
  fi
  printf '%s：已核验为 %s\n' "$label" "$installed_ver"
}

sync_client codex "Codex" "${CODEX_BIN-codex}" "letsgo@letsgo-skills"
sync_client claude "Claude Code" "${CLAUDE_BIN-claude}" "letsgo@letsgo-skills"
sync_client agy "Antigravity" "${AGY_BIN-agy}" "letsgo"

if [ -n "$FAILURES" ]; then
  printf '错误：以下客户端同步或版本核验未通过：%s\n' "$FAILURES" >&2
  exit 1
fi

if [ "$CHECK_ONLY" -eq 1 ]; then
  printf '三端核验完成（当前版本 %s）。\n' "$VERSION"
else
  printf '三端同步与核验完成（版本 %s），请开启新会话使更新生效。\n' "$VERSION"
fi
