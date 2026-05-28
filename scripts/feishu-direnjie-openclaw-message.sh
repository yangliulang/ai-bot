#!/usr/bin/env bash
# 参考 ChainUP weekly-report-reminder.sh：用 OpenClaw Feishu 通道向指定群聊发送文本消息。
# 安全提示：请勿将含 App Secret 的脚本提交到公开仓库；优先使用同目录下 .env（勿入库）或环境变量覆盖默认值。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ -f "./.feishu-direnjie.env" ]]; then
  # shellcheck source=/dev/null
  source "./.feishu-direnjie.env"
fi

# 飞书应用（可用环境变量覆盖）
FEISHU_APP_ID="${FEISHU_APP_ID:-cli_a938881eae22deee}"
FEISHU_APP_SECRET="${FEISHU_APP_SECRET:-AV7GD1Dgdx365gxPx7gbBcEDebysnsu1}"
FEISHU_BOT_NAME="${FEISHU_BOT_NAME:-狄仁杰}"

# OpenClaw：账户 key（写入 channels.feishu.accounts.<该 key>）及群聊 open_chat_id（oc_ 开头）
OPENCLAW_FEISHU_ACCOUNT="${OPENCLAW_FEISHU_ACCOUNT:-direnjie}"
OPENCLAW_FEISHU_TARGET="${OPENCLAW_FEISHU_TARGET:-oc_006afaf62fc4cc0a3cf535cb8c480950}"

# 若置为 0，则不会写入 ~/.openclaw/ 配置（需已手动配置好同名 account 且 appId 一致）
SYNC_OPENCLAW_FEISHU_ACCOUNT="${SYNC_OPENCLAW_FEISHU_ACCOUNT:-1}"

NOW="$(date '+%Y-%m-%d %H:%M:%S')"
DEFAULT_MSG="【${FEISHU_BOT_NAME}】${NOW}"$'\n'"大家好，这是一条自动化测试消息。"

OPENCLAW_MSG_EXTRA=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      OPENCLAW_MSG_EXTRA+=(--dry-run)
      shift
      ;;
    --)
      shift
      FEISHU_MESSAGE="$*"
      set --
      break
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -gt 0 ]]; then
  FEISHU_MESSAGE="$*"
fi
FEISHU_MESSAGE="${FEISHU_MESSAGE:-$DEFAULT_MSG}"

if [[ -z "${FEISHU_APP_ID}" || -z "${FEISHU_APP_SECRET}" ]]; then
  echo "[error] 请设置 FEISHU_APP_ID / FEISHU_APP_SECRET（或使用 .feishu-direnjie.env）" >&2
  exit 1
fi

if [[ -z "${OPENCLAW_FEISHU_TARGET}" ]]; then
  echo "[error] OPENCLAW_FEISHU_TARGET 不能为空（群 open_chat_id，一般为 oc_ 开头）" >&2
  exit 1
fi

OPENCLAW_CMD=(openclaw)
if [[ -n "${OPENCLAW_PROFILE:-}" ]]; then
  OPENCLAW_CMD+=(--profile "$OPENCLAW_PROFILE")
fi

ensure_openclaw_feishu_account() {
  local current=""
  set +e
  current="$("${OPENCLAW_CMD[@]}" config get "channels.feishu.accounts.${OPENCLAW_FEISHU_ACCOUNT}.appId" 2>/dev/null)"
  local st=$?
  set -e
  if [[ $st -eq 0 && "$current" == "$FEISHU_APP_ID" ]]; then
    return 0
  fi

  echo "[info] 向 OpenClaw 写入/更新 Feishu account「${OPENCLAW_FEISHU_ACCOUNT}」（${FEISHU_BOT_NAME}）…" >&2
  FEISHU_APP_ID="$FEISHU_APP_ID" FEISHU_APP_SECRET="$FEISHU_APP_SECRET" FEISHU_BOT_NAME="$FEISHU_BOT_NAME" OPENCLAW_FEISHU_ACCOUNT="$OPENCLAW_FEISHU_ACCOUNT" node -e '
const id = process.env.FEISHU_APP_ID || "";
const secret = process.env.FEISHU_APP_SECRET || "";
const name = process.env.FEISHU_BOT_NAME || "";
const key = process.env.OPENCLAW_FEISHU_ACCOUNT || "direnjie";
if (!id || !secret || !key) process.exit(1);
const patch = {
  channels: {
    feishu: {
      accounts: {
        [key]: { appId: id, appSecret: secret, name: name || key },
      },
    },
  },
};
process.stdout.write(JSON.stringify(patch));
  ' | "${OPENCLAW_CMD[@]}" config patch --stdin
}

if [[ "${SYNC_OPENCLAW_FEISHU_ACCOUNT}" == "1" ]]; then
  ensure_openclaw_feishu_account
fi

OPENCLAW_CMD+=(message send --channel feishu --account "$OPENCLAW_FEISHU_ACCOUNT" --target "$OPENCLAW_FEISHU_TARGET" -m "$FEISHU_MESSAGE")
# Bash 3.2 + set -u：空数组用 [@] 会报 unbound variable，需按元素个数追加
if ((${#OPENCLAW_MSG_EXTRA[@]} > 0)); then
  OPENCLAW_CMD+=("${OPENCLAW_MSG_EXTRA[@]}")
fi

echo "[info] sending via: openclaw … --account ${OPENCLAW_FEISHU_ACCOUNT} --target ${OPENCLAW_FEISHU_TARGET}" >&2
"${OPENCLAW_CMD[@]}"
