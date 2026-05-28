#!/usr/bin/env bash
# 功能包 status.yaml 更新后，提示流水线下一步 Skill（fail-open）
# stdin: Cursor Hook JSON；stdout: Hook 响应 JSON
#
# - postToolUse（Write/StrReplace status.yaml）：输出 additional_context
# - stop：仅当 pipeline.hooks.stop_followup=true 时输出 followup_message
# - 其它事件（含 afterFileEdit）：不输出，避免误触发反复注入

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PIPELINE_PROJECT_ROOT="$ROOT"

HOOKS_ENABLED=true
HOOKS_REMIND_ON_WRITE=true
HOOKS_STOP_FOLLOWUP=false
HOOKS_REQUIRE_NEW_CHAT=true

if [ -f "$ROOT/scripts/lib/read-pipeline-project.sh" ]; then
  # shellcheck source=scripts/lib/read-pipeline-project.sh
  source "$ROOT/scripts/lib/read-pipeline-project.sh"
  HOOKS_ENABLED="$(pp_hooks_bool pipeline.hooks.enabled true)"
  HOOKS_REMIND_ON_WRITE="$(pp_hooks_bool pipeline.hooks.remind_on_write true)"
  HOOKS_STOP_FOLLOWUP="$(pp_hooks_bool pipeline.hooks.stop_followup false)"
  HOOKS_REQUIRE_NEW_CHAT="$(pp_hooks_bool pipeline.hooks.require_new_chat true)"
fi

if [ "$HOOKS_ENABLED" = "false" ]; then
  exit 0
fi

INPUT="$(cat)"

HOOK_EVENT=""
FILE_PATH=""

if command -v python3 >/dev/null 2>&1 && [ -n "$INPUT" ]; then
  read -r HOOK_EVENT FILE_PATH < <(printf '%s' "$INPUT" | python3 -c '
import json, sys

def norm_path(p):
    if not isinstance(p, str) or "status.yaml" not in p:
        return None
    return p.split("file://")[-1] if p.startswith("file://") else p

raw = sys.stdin.read()
if not raw.strip():
    sys.exit(0)
try:
    data = json.loads(raw)
except json.JSONDecodeError:
    sys.exit(0)

event = data.get("hook_event_name") or ""

for key in ("file_path", "path", "filePath", "editedFile", "uri"):
    p = norm_path(data.get(key))
    if p:
        print(event, p)
        sys.exit(0)

tool = data.get("tool_name") or ""
if tool in ("Write", "StrReplace") or event == "postToolUse":
    ti = data.get("tool_input")
    if isinstance(ti, str):
        try:
            ti = json.loads(ti)
        except json.JSONDecodeError:
            ti = {}
    if isinstance(ti, dict):
        p = norm_path(ti.get("path") or ti.get("file_path"))
        if p:
            print(event, p)
            sys.exit(0)

print(event, "")
' 2>/dev/null || true)
fi

# 仅处理明确事件；禁止从整段 stdin grep 路径（会把对话里提到的 status.yaml 误判为本次写入）
case "$HOOK_EVENT" in
  postToolUse|stop) ;;
  *) exit 0 ;;
esac

if [ "$HOOK_EVENT" = "postToolUse" ] && [ "$HOOKS_REMIND_ON_WRITE" != "true" ]; then
  exit 0
fi
if [ "$HOOK_EVENT" = "stop" ] && [ "$HOOKS_STOP_FOLLOWUP" != "true" ]; then
  exit 0
fi

# stop：未命中路径时，找 3 分钟内修改过的 status.yaml
if { [ -z "$FILE_PATH" ] || [[ "$FILE_PATH" != *status.yaml ]]; } && [ "$HOOK_EVENT" = "stop" ]; then
  if [ -d "$ROOT/handoff/features" ]; then
    FILE_PATH="$(find "$ROOT/handoff/features" -name status.yaml -mmin -3 2>/dev/null | head -1 || true)"
  fi
fi

if [ -z "$FILE_PATH" ] || [[ "$FILE_PATH" != *status.yaml ]]; then
  exit 0
fi

case "$FILE_PATH" in
  /*) STATUS_FILE="$FILE_PATH" ;;
  *) STATUS_FILE="$ROOT/$FILE_PATH" ;;
esac

[ -f "$STATUS_FILE" ] || exit 0

FEATURE_ID="$(grep -E '^feature:' "$STATUS_FILE" | head -1 | sed 's/^feature:[[:space:]]*//;s/[[:space:]]*$//')"
PHASE="$(grep -E '^phase:' "$STATUS_FILE" | head -1 | sed 's/^phase:[[:space:]]*//;s/[[:space:]]*$//')"
NEXT="$(grep -E '^next:' "$STATUS_FILE" | head -1 | sed 's/^next:[[:space:]]*//;s/[[:space:]]*$//')"

HAS_BLOCKERS=false
if grep -qE '^blockers:' "$STATUS_FILE" && ! grep -qE '^blockers:[[:space:]]*\[\][[:space:]]*$' "$STATUS_FILE"; then
  if awk '/^blockers:/{f=1;next} f && /^[^[:space:]]/{exit} f && /- /{found=1; exit}' "$STATUS_FILE"; then
    HAS_BLOCKERS=true
  fi
fi

# 功能已闭环（next: null / 空，或 phase: done）
if [ "$PHASE" = "done" ] || [ "$NEXT" = "null" ] || [ -z "$NEXT" ]; then
  if command -v ruby >/dev/null 2>&1 && [ -f "$ROOT/scripts/lib/phase-close-ready.rb" ]; then
    PHASE_CLOSE_JSON="$(ruby "$ROOT/scripts/lib/phase-close-ready.rb" --json 2>/dev/null || true)"
    if [ -n "$PHASE_CLOSE_JSON" ]; then
      PHASE_CLOSE_READY="$(printf '%s' "$PHASE_CLOSE_JSON" | python3 -c 'import json,sys; print("true" if json.load(sys.stdin).get("ready") else "false")' 2>/dev/null || echo "false")"
      if [ "$PHASE_CLOSE_READY" = "true" ]; then
        ACTIVE_PHASE="$(printf '%s' "$PHASE_CLOSE_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("active_phase",""))' 2>/dev/null || echo "?")"
        MSG="【流水线】阶段 \`phase-${ACTIVE_PHASE}\` **已全部 done**。请先**新开 Chat** 执行 \`/pipeline-product-phase-close\`（本阶段完成项追加到 inventory §2，并切片下一迭代）。**勿**直接 \`/pipeline-product-plan\`，以免按 PRD 重复规划已完成部分。"
        if [ "$HOOKS_REQUIRE_NEW_CHAT" = "true" ]; then
          MSG="${MSG} 请指挥官确认后新开 Chat；勿在本会话自动运行 \`advance-phase\`。"
        fi
        escape_json() {
          printf '%s' "$1" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' 2>/dev/null || \
            printf '%s' "$1" | sed 's/\\/\\\\/g;s/"/\\"/g;s/$/\\n/' | tr -d '\n' | sed 's/\\n$//'
        }
        ESC_MSG="$(escape_json "$MSG")"
        if [ "$HOOK_EVENT" = "stop" ]; then
          printf '{"followup_message":%s}\n' "$ESC_MSG"
        else
          printf '{"additional_context":%s}\n' "$ESC_MSG"
        fi
      fi
    fi
  fi
  exit 0
fi

TASK_KEY=""
case "$NEXT" in
  null|"") TASK_KEY="" ;;
  backend-agent)
    case "$PHASE" in
      contract_ready|backend_in_progress) TASK_KEY="backend.implement" ;;
    esac
    ;;
  test-agent)
    case "$PHASE" in
      backend_done) TASK_KEY="test.api" ;;
      frontend_done)
        if $HAS_BLOCKERS; then TASK_KEY=""; else TASK_KEY="test.e2e"; fi
        ;;
    esac
    ;;
  frontend-agent)
    case "$PHASE" in
      tested) TASK_KEY="frontend.integrate" ;;
      frontend_done) TASK_KEY="frontend.fix-e2e" ;;
      e2e_verified) TASK_KEY="frontend.fix-ui" ;;
    esac
    ;;
  designer-agent)
    case "$PHASE" in
      e2e_verified) TASK_KEY="designer.review" ;;
    esac
    ;;
  product-agent)
    case "$PHASE" in
      planned) TASK_KEY="product.contract" ;;
      ui_reviewed) TASK_KEY="product.accept" ;;
    esac
    ;;
esac

SKILL=""
case "$TASK_KEY" in
  product.plan) SKILL="pipeline-product-plan" ;;
  product.contract) SKILL="pipeline-product-contract" ;;
  product.accept) SKILL="pipeline-product-accept" ;;
  backend.implement) SKILL="pipeline-backend" ;;
  test.prepare) SKILL="pipeline-test-prepare" ;;
  test.api) SKILL="pipeline-test-api" ;;
  test.e2e) SKILL="pipeline-test-e2e" ;;
  test.e2e-retest) SKILL="pipeline-test-e2e-retest" ;;
  frontend.integrate) SKILL="pipeline-frontend-integrate" ;;
  frontend.fix-e2e) SKILL="pipeline-frontend-fix-e2e" ;;
  frontend.fix-ui) SKILL="pipeline-frontend-fix-ui" ;;
  frontend.mock) SKILL="pipeline-frontend-mock" ;;
  designer.review) SKILL="pipeline-designer-review" ;;
  designer.rereview) SKILL="pipeline-designer-rereview" ;;
esac

SKIP_HINT=""
if command -v ruby >/dev/null 2>&1 && [ -f "$ROOT/scripts/lib/pipeline-skip-check.rb" ]; then
  SKIP_JSON="$(ruby "$ROOT/scripts/lib/pipeline-skip-check.rb" "$STATUS_FILE" --json 2>/dev/null || true)"
  if [ -n "$SKIP_JSON" ]; then
    SHOULD_SKIP="$(printf '%s' "$SKIP_JSON" | python3 -c 'import json,sys; print("true" if json.load(sys.stdin).get("should_skip") else "false")' 2>/dev/null || echo "false")"
    if [ "$SHOULD_SKIP" = "true" ]; then
      SKIP_TASK="$(printf '%s' "$SKIP_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("task",""))' 2>/dev/null || true)"
      TARGET_PHASE="$(printf '%s' "$SKIP_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("target_phase",""))' 2>/dev/null || true)"
      if [ -n "$TASK_KEY" ] && [ "$TASK_KEY" = "$SKIP_TASK" ]; then
        SKILL=""
      fi
      SKIP_HINT="【跳过】本功能 \`skips\` 含 \`${SKIP_TASK}\`，**勿**执行对应角色任务；请**新开 Chat** 运行 \`/pipeline-skip ${FEATURE_ID}\` 推进至 \`phase: ${TARGET_PHASE}\`。"
    fi
  fi
fi

MSG=""
if [ -n "$SKIP_HINT" ]; then
  MSG="$SKIP_HINT"
  if [ -n "$SKILL" ]; then
    CMD="/${SKILL} ${FEATURE_ID}"
    MSG="${MSG}（若已手动跳过，可执行 \`${CMD}\`。）"
  fi
elif [ -n "$SKILL" ]; then
  CMD="/${SKILL} ${FEATURE_ID}"
  MSG="【流水线】\`${FEATURE_ID}\` 当前 \`phase: ${PHASE}\`，\`next: ${NEXT}\`。请**新开 Chat** 执行：\`${CMD}\`（或 \`/pipeline-next ${FEATURE_ID}\`）。"
  if $HAS_BLOCKERS; then
    MSG="${MSG} 注意：\`blockers\` 非空，请先处理返工项。"
  fi
  if [ "$PHASE" = "contract_ready" ] && [ "$NEXT" = "backend-agent" ]; then
    MSG="${MSG} 可选并行：\`/pipeline-test-prepare ${FEATURE_ID}\`、\`/pipeline-frontend-mock ${FEATURE_ID}\`。"
  fi
  if [ "$HOOKS_REQUIRE_NEW_CHAT" = "true" ]; then
    MSG="${MSG} **请指挥官确认后新开 Chat 执行**；勿在本会话自动推进 \`status.yaml\` 门禁。"
  fi
else
  MSG="【流水线】\`${FEATURE_ID}\` → \`phase: ${PHASE}\`，\`next: ${NEXT}\`。无自动映射任务，请执行 \`/pipeline-next ${FEATURE_ID}\` 或查阅 \`handoff/pipeline/COMMANDER.md\` §3。"
  if $HAS_BLOCKERS; then
    MSG="${MSG} \`blockers\` 非空，见 status.yaml。"
  fi
  if [ "$HOOKS_REQUIRE_NEW_CHAT" = "true" ]; then
    MSG="${MSG} **请指挥官确认后新开 Chat**；勿在本会话自动推进。"
  fi
fi

escape_json() {
  printf '%s' "$1" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' 2>/dev/null || \
    printf '%s' "$1" | sed 's/\\/\\\\/g;s/"/\\"/g;s/$/\\n/' | tr -d '\n' | sed 's/\\n$//'
}

ESC_MSG="$(escape_json "$MSG")"

if [ "$HOOK_EVENT" = "stop" ]; then
  printf '{"followup_message":%s}\n' "$ESC_MSG"
else
  printf '{"additional_context":%s}\n' "$ESC_MSG"
fi
exit 0
