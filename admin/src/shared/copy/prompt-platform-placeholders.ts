// 作者: 杨永的Agent
// 日期: 2026-05-19
// 修改功能: Phase1 **`{{slug}}` 平台白名单键** · 与服务端 **`prompt_placeholder_validation._PHASE1_PLATFORM_PLACEHOLDER_SLUGS`** 对齐展示（FE_HANDOFF · AC-09f）

/** 服务端归一为 UPPER 无空格后与 messages 内 `{{…}}` 匹配；运营编辑常用小写下划线写法。 */
export const PHASE1_PLATFORM_PROMPT_PLACEHOLDER_EXAMPLES = [
  '{{ effective_locale }}',
  '{{ scenario_id }}',
  '{{ execution_id }}',
  '{{ prompt_pack_version }}',
  '{{ user_visible_message }}',
  '{{ requires_main_site }}',
  '{{ session_id }}',
  '{{ agent_context }}',
] as const
