import type { AdminNavIconKey } from '@/assets/icons/admin-nav/keys'

import access from '@/assets/icons/admin-nav/access.svg?raw'
import billingLedger from '@/assets/icons/admin-nav/billing-ledger.svg?raw'
import billingOverview from '@/assets/icons/admin-nav/billing-overview.svg?raw'
import billingPricing from '@/assets/icons/admin-nav/billing-pricing.svg?raw'
import channels from '@/assets/icons/admin-nav/channels.svg?raw'
import confirmation from '@/assets/icons/admin-nav/confirmation.svg?raw'
import executions from '@/assets/icons/admin-nav/executions.svg?raw'
import instances from '@/assets/icons/admin-nav/instances.svg?raw'
import observability from '@/assets/icons/admin-nav/observability.svg?raw'
import orchestration from '@/assets/icons/admin-nav/orchestration.svg?raw'
import prompts from '@/assets/icons/admin-nav/prompts.svg?raw'
import safety from '@/assets/icons/admin-nav/safety.svg?raw'
import settings from '@/assets/icons/admin-nav/settings.svg?raw'

export type { AdminNavIconKey } from '@/assets/icons/admin-nav/keys'

/** 来自 `src/assets/icons/admin-nav/*.svg`，供侧栏使用（currentColor） */
export const ADMIN_NAV_ICON_SVG: Record<AdminNavIconKey, string> = {
  executions,
  instances,
  prompts,
  orchestration,
  'tool-registry': orchestration,
  confirmation,
  safety,
  access,
  'billing-overview': billingOverview,
  'billing-pricing': billingPricing,
  'billing-ledger': billingLedger,
  observability,
  channels,
  settings,
}
