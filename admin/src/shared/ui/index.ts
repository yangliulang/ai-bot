/** 设计系统薄封装：基于 Reka UI 原语 + Tailwind，业务页优先从这里引用 */
export { default as AdminPageHeader } from '@/shared/ui/AdminPageHeader.vue'
export {
  ADMIN_PAGE_HEADER_ACTIONS_CLASS,
  ADMIN_PAGE_HEADER_ROOT_CLASS,
  type AdminPageHeaderBadge,
  type AdminPageHeaderBadgeTone,
} from '@/shared/ui/admin-page-header'
export { default as AdminToastHost } from '@/shared/ui/AdminToastHost.vue'
export { default as UiButton } from '@/shared/ui/UiButton.vue'
export { default as UiStatChip } from '@/shared/ui/UiStatChip.vue'
export {
  ADMIN_TOOLBAR_CLUSTER_CLASS,
  ADMIN_TOOLBAR_CONTROL_H_CLASS,
  ADMIN_TOOLBAR_META_CLASS,
} from '@/shared/ui/toolbar-controls'
export { default as UiAnchorTip } from '@/shared/ui/UiAnchorTip.vue'
export { default as UiClipboardTipAction } from '@/shared/ui/UiClipboardTipAction.vue'
export { default as UiTableAction } from '@/shared/ui/UiTableAction.vue'
export { default as UiInput } from '@/shared/ui/UiInput.vue'
export { default as UiModal } from '@/shared/ui/UiModal.vue'
export { default as UiSelect } from '@/shared/ui/UiSelect.vue'
export type { UiSelectOption } from '@/shared/ui/UiSelect.vue'
export { default as UiSwitch } from '@/shared/ui/UiSwitch.vue'
export { default as UiEnableCheckbox } from '@/shared/ui/UiEnableCheckbox.vue'
export { default as UiTableEmptyRow } from '@/shared/ui/UiTableEmptyRow.vue'
export { adminTableHostOverflowClass } from '@/shared/ui/table-list'
