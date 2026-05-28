#!/usr/bin/env bash
# brownfield：从 inventory §4 生成 backlog.yaml
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PIPELINE_PROJECT_ROOT="$ROOT"

exec ruby "$ROOT/scripts/lib/seed-backlog-from-inventory.rb" "$@"
