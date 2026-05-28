#!/usr/bin/env bash
# 从 pipeline.project.yaml 读取配置（需 Ruby Psych，macOS/Linux 常见可用）
# 用法: source scripts/lib/read-pipeline-project.sh
#       pp_get apps.backend.path

set -euo pipefail

_pp_root() {
  if [ -n "${PIPELINE_PROJECT_ROOT:-}" ]; then
    echo "$PIPELINE_PROJECT_ROOT"
    return
  fi
  local lib_dir
  if [ -n "${BASH_SOURCE[0]+x}" ]; then
    lib_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  else
    lib_dir="$(cd "$(dirname "$0")" && pwd)"
  fi
  echo "$(cd "$lib_dir/../.." && pwd)"
}

_pp_file() {
  echo "$(_pp_root)/pipeline.project.yaml"
}

pp_require_file() {
  local f
  f="$(_pp_file)"
  if [ ! -f "$f" ]; then
    echo "错误: 未找到 $f（可从 pipeline.project.yaml.example 复制）" >&2
    return 1
  fi
}

# pp_get <dot.path>  例: pp_get apps.backend.dev.base_url
pp_get() {
  local key="${1:?key required}"
  pp_require_file || return 1
  export PIPELINE_PROJECT_FILE="$(_pp_file)"
  export PP_KEY="$key"
  ruby -ryaml -e '
    require "yaml"
    path = ENV.fetch("PP_KEY")
    data = YAML.load_file(ENV.fetch("PIPELINE_PROJECT_FILE"))
    val = path.split(".").reduce(data) { |m, k| m.is_a?(Hash) ? m[k] : nil }
    abort "missing key: #{path}" if val.nil? || (val.respond_to?(:empty?) && val.empty?)
    puts val
  '
}

# pp_get_optional <dot.path> [default] — 缺键或空值时返回 default（不 abort）
pp_get_optional() {
  local key="${1:?key required}"
  local default="${2:-}"
  if ! pp_require_file 2>/dev/null; then
    printf '%s' "$default"
    return 0
  fi
  export PIPELINE_PROJECT_FILE="$(_pp_file)"
  export PP_KEY="$key"
  export PP_DEFAULT="$default"
  ruby -ryaml -e '
    require "yaml"
    path = ENV.fetch("PP_KEY")
    default = ENV.fetch("PP_DEFAULT", "")
    data = YAML.load_file(ENV.fetch("PIPELINE_PROJECT_FILE"))
    val = path.split(".").reduce(data) { |m, k| m.is_a?(Hash) ? m[k] : nil }
    if val.nil? || (val.respond_to?(:empty?) && val.empty?)
      print default
    else
      print val
    end
  '
}

# pp_hooks_bool <dot.path> <default true|false>
pp_hooks_bool() {
  local key="${1:?key required}"
  local default="${2:-true}"
  local raw
  raw="$(pp_get_optional "$key" "$default")"
  case "$(printf '%s' "$raw" | tr '[:upper:]' '[:lower:]')" in
    true|yes|1|on) printf 'true' ;;
    false|no|0|off) printf 'false' ;;
    *) printf '%s' "$default" ;;
  esac
}

# 打印 tasks.yaml 常用占位符（供 Agent / 文档对照）
pp_print_context() {
  pp_require_file || return 1
  cat <<EOF
features_root=$(pp_get features.root)
backend_path=$(pp_get apps.backend.path)
frontend_path=$(pp_get apps.frontend.path)
api_base_url=$(pp_get apps.backend.dev.base_url)
web_dev_url=$(pp_get apps.frontend.dev.base_url)
prd_path=$(pp_get project.prd.primary)
default_roadmap=$(pp_get roadmap.default_phase_file)
onboarding_mode=$(pp_get_optional project.onboarding.mode greenfield)
inventory_path=$(pp_get_optional product.inventory handoff/product/inventory.md)
backlog_path=$(pp_get_optional product.backlog handoff/product/backlog.yaml)
active_phase=$(pp_get_optional roadmap.active_phase 1)
EOF
}
