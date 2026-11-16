#!/usr/bin/env bash
# Creates the two things the scripts need that are not on main:
#   1. the v2 EEA harness (branch eea-truck-validation-2026-11, commit 73990f0) as a git worktree
#   2. the VECTO fork (mohgsaad-art/VECTO, branch IEPC-experiments, commit b8d6126)
# Both are placed next to the hdev repo (../hdev-v2 and ../VECTO). The harness is used unchanged.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$REPO"
[ -d ../hdev-v2 ] || git worktree add --detach ../hdev-v2 73990f0
[ -d ../VECTO ] || git clone --depth 1 --branch IEPC-experiments --single-branch https://github.com/mohgsaad-art/VECTO.git ../VECTO
git -C ../VECTO rev-parse HEAD   # expect b8d6126ab0bc2ab8beb3eaee878f7198126b600a
