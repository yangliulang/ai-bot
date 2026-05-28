#!/usr/bin/env bash
# 阶段收束：phase 全 done → inventory §2 + backlog 切片 → phase-(N+1)
# 见 handoff/conventions/onboarding-modes.md
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PIPELINE_PROJECT_ROOT="$ROOT"

exec ruby "$ROOT/scripts/lib/phase-advance.rb" "$@"
