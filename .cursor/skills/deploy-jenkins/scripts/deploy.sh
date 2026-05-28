#!/usr/bin/env bash
# Trigger ChainUp AI Bot Jenkins jobs with BRANCH parameter.
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: deploy.sh <BRANCH> <job-id> [job-id ...]" >&2
  echo "  job-id: botadmin | deeplink | server-api | website" >&2
  exit 1
fi

BRANCH="$1"
shift

if [[ -z "${BRANCH// /}" ]]; then
  echo "BRANCH must not be empty." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
ENV_FILE="$ROOT_DIR/.cursor/jenkins.env"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

JENKINS_USER="${JENKINS_USER:-}"
JENKINS_TOKEN="${JENKINS_TOKEN:-}"
JENKINS_BASE="${JENKINS_BASE:-https://jenkins.dw2nn.com}"

if [[ -z "$JENKINS_USER" || -z "$JENKINS_TOKEN" ]]; then
  echo "Missing JENKINS_USER or JENKINS_TOKEN." >&2
  echo "Copy and edit: cp \"$ROOT_DIR/.cursor/jenkins.env.example\" \"$ROOT_DIR/.cursor/jenkins.env\"" >&2
  exit 1
fi

resolve_job() {
  case "$1" in
    botadmin) echo botadmin ;;
    deeplink) echo deeplink ;;
    server-api) echo server-api ;;
    website) echo website ;;
    *) echo "" ;;
  esac
}

urlencode() {
  python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1], safe=''))" "$1"
}

ENCODED_BRANCH="$(urlencode "$BRANCH")"
FAIL=0

for id in "$@"; do
  job="$(resolve_job "$id")"
  if [[ -z "$job" ]]; then
    echo "Unknown job id: $id (expected botadmin, deeplink, server-api, or website)" >&2
    FAIL=1
    continue
  fi

  url="${JENKINS_BASE}/job/${job}/buildWithParameters?BRANCH=${ENCODED_BRANCH}"
  view_url="${JENKINS_BASE}/view/chainup-ai-bot/job/${job}/"

  echo "→ Triggering ${job} (BRANCH=${BRANCH})..."
  http_code="$(curl -s -o /dev/null -w "%{http_code}" -X POST "$url" --user "${JENKINS_USER}:${JENKINS_TOKEN}")"

  case "$http_code" in
    200|201|302)
      echo "  OK (HTTP ${http_code})"
      echo "  ${view_url}"
      ;;
    *)
      echo "  FAILED (HTTP ${http_code})" >&2
      echo "  ${view_url}" >&2
      FAIL=1
      ;;
  esac
done

exit "$FAIL"
