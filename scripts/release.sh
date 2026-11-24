#!/bin/sh
# 发布 letsgo 插件的新版本：同步版本号与市场锁定的标签，校验，提交，打标签并推送。
# 用法：scripts/release.sh X.Y.Z
# 发布后，用户通过各宿主的插件管理器更新到该版本。

set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$REPO_ROOT"

fail() { printf '错误：%s\n' "$1" >&2; exit 1; }

[ $# -eq 1 ] || fail "用法：scripts/release.sh X.Y.Z"
VERSION=$1
TAG="v$VERSION"
printf '%s\n' "$VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$' || fail "版本号必须是 X.Y.Z 形式：$VERSION"
git rev-parse -q --verify "refs/tags/$TAG" >/dev/null && fail "标签 $TAG 已存在。"
[ -z "$(git status --porcelain)" ] || fail "工作区有未提交的改动，请先提交或清理。"

LAST=$(git tag --list 'v*' --sort=-v:refname | head -n 1)
if [ -n "$LAST" ]; then
  HIGHEST=$(printf '%s\n%s\n' "${LAST#v}" "$VERSION" | sort -t. -k1,1n -k2,2n -k3,3n | tail -n 1)
  [ "$HIGHEST" = "$VERSION" ] || fail "版本 $VERSION 必须大于上一个版本 ${LAST#v}。"
fi

python3 - "$VERSION" "$TAG" <<'PY'
import json, sys
from pathlib import Path

version, tag = sys.argv[1], sys.argv[2]
for path in (
    "plugins/letsgo/.claude-plugin/plugin.json",
    "plugins/letsgo/.codex-plugin/plugin.json",
    "plugins/letsgo/.antigravity-plugin/plugin.json",
):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data["version"] = version
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for path in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    for plugin in data["plugins"]:
        if plugin["name"] == "letsgo":
            plugin["source"]["ref"] = tag
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

python3 scripts/validate.py || { git checkout -- .; fail "校验未通过，已撤销版本号改动。"; }

git add -A
git commit -m "release: $TAG"
git tag -a "$TAG" -m "letsgo $TAG"
git push origin HEAD
git push origin "$TAG"
printf '已发布 %s。请通过 Codex、Claude Code 和 Antigravity 的插件管理器更新。\n' "$TAG"
