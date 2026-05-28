/** 展示名：可与产品文案拆分至 i18n */
export const appName = 'TG-BOT-Admin'

/**
 * 是否展示页内开发元信息（pageId、路线图、契约 TBD、演示说明等）。
 * 默认：`vite` 开发服务为 true；`vite build` 产物为 false。
 * 覆盖：`.env` 中设置 `VITE_ADMIN_PAGE_DEV_META=0`（强制关）或 `=1`（强制开，如预发排查）。
 */
export const showAdminPageDevMeta: boolean =
  import.meta.env.VITE_ADMIN_PAGE_DEV_META === '1'
    ? true
    : import.meta.env.VITE_ADMIN_PAGE_DEV_META === '0'
      ? false
      : import.meta.env.DEV
