#!/bin/sh
# 发布 letsgo 插件的新版本：同步版本号与市场锁定的裸 x.y.z 标签，校验，提交，打标签并推送。
# 用法：scripts/release.sh [--allow-xy-bump] x.y.z
# 默认仅允许递增 z；修改 x 或 y 须经维护者同意并显式传入 --allow-xy-bump。
# 环境变量：LETSGO_RELEASE_SKIP_TESTS=1 仅为单测防重入递归守卫，常规发版勿设。

set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$REPO_ROOT"

fail() { printf '错误：%s\n' "$1" >&2; exit 1; }

rollback_and_fail() {
  git checkout -- .
  if [ -n "${1:-}" ]; then
    fail "$1"
  fi
  exit 1
}

ALLOW_XY_BUMP=0
VERSION=""
for arg in "$@"; do
  case "$arg" in
    --allow-xy-bump)
      ALLOW_XY_BUMP=1
      ;;
    -*)
      fail "用法：scripts/release.sh [--allow-xy-bump] x.y.z"
      ;;
    *)
      [ -z "$VERSION" ] || fail "用法：scripts/release.sh [--allow-xy-bump] x.y.z"
      VERSION=$arg
      ;;
  esac
done

[ -n "$VERSION" ] || fail "用法：scripts/release.sh [--allow-xy-bump] x.y.z"
printf '%s\n' "$VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$' || fail "版本号必须是无 v 前缀的裸 x.y.z 形式：$VERSION"
git rev-parse -q --verify "refs/tags/$VERSION" >/dev/null && fail "标签 $VERSION 已存在。"
[ -z "$(git status --porcelain)" ] || fail "工作区有未提交的改动，请先提交或清理。"

CURRENT=$(python3 -c 'import json; from pathlib import Path; print(json.loads(Path("plugins/letsgo/.claude-plugin/plugin.json").read_text(encoding="utf-8")).get("version", ""))')
printf '%s\n' "$CURRENT" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$' || fail "当前清单版本无效：$CURRENT"

LAST_BARE=$({ git tag --list | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' || true; } | sort -t. -k1,1n -k2,2n -k3,3n | tail -n 1)

python3 - "$CURRENT" "$VERSION" "$ALLOW_XY_BUMP" "$LAST_BARE" <<'PY'
import sys

def parse(ver: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in ver.split("."))  # type: ignore[return-value]

current_str, target_str, allow_raw, last_bare = sys.argv[1:5]
cur = parse(current_str)
new = parse(target_str)
allow_xy = allow_raw == "1"

if not allow_xy:
    if new[:2] != cur[:2]:
        sys.stderr.write(
            f"错误：未传 --allow-xy-bump 禁止修改 x 或 y（当前 {current_str} -> 目标 {target_str}）；"
            "智能体仅可递增 z，修改 x 或 y 须经维护者同意后显式传入 --allow-xy-bump。\n"
        )
        sys.exit(1)
    if new[2] <= cur[2]:
        sys.stderr.write(f"错误：新版本 {target_str} 的 z 必须大于当前版本 {current_str}。\n")
        sys.exit(1)
else:
    if new == cur:
        sys.stderr.write(f"错误：版本 {target_str} 与当前版本相同。\n")
        sys.exit(1)
    if new[:2] == cur[:2] and new[2] <= cur[2]:
        sys.stderr.write(f"错误：同 x.y 下新版本 {target_str} 必须大于当前版本 {current_str}。\n")
        sys.exit(1)

if last_bare:
    last = parse(last_bare)
    if new <= last:
        sys.stderr.write(f"错误：版本 {target_str} 必须大于上一个裸版本标签 {last_bare}。\n")
        sys.exit(1)
PY

python3 - "$VERSION" <<'PY'
import json, sys
from pathlib import Path

version = sys.argv[1]
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
            plugin["source"]["ref"] = version
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

python3 -B scripts/changelog_guard.py archive "$VERSION" || rollback_and_fail ""

python3 -B scripts/validate.py || rollback_and_fail "校验未通过，已撤销版本号改动。"
if [ "${LETSGO_RELEASE_SKIP_TESTS:-0}" != "1" ]; then
  LETSGO_RELEASE_SKIP_TESTS=1 python3 -B -m unittest discover -s scripts/tests || rollback_and_fail "单元测试未通过，已撤销版本号改动。"
fi

git add -A
git commit -m "release: $VERSION"
git tag -a "$VERSION" -m "letsgo $VERSION"
git push origin HEAD
git push origin "$VERSION"
printf '已发布 %s。请通过 Codex、Claude Code 和 Antigravity 的插件管理器更新。\n' "$VERSION"
