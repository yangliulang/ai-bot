<!--
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 刷新/保存等操作反馈改用全局 **`adminToast`**（移除页内 flash 文案）
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 白名单/封禁表空态 **`UiTableEmptyRow`**（表内居中，去掉表格外占位）
作者: 杨永的Agent
日期: 2026-05-18
修改功能: 门禁探测：**`requiresMainSite`** 徽标 + `title`（AC-09l · FE_HANDOFF）；与原型 `http://localhost:5176/access` 门禁探测对齐
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 封禁表行内 **复制** → **`UiClipboardTipAction`**（剪贴板回退 + 浮动提示）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: VIP 阈值 **updatedAt** 仅后缀 **`(UTC+8)`/`(UTC)`**，去掉冗长说明
作者: 杨永的Agent
日期: 2026-05-16
修改功能: `/access` 对接 **`/api/v1/admin/access-control/*`**（白名单/封禁/VIP/灰度）；**`POST …/agent/access/evaluate`** 探测；移除 DEMO 数据源（FE_HANDOFF）
作者: 杨永的Agent
日期: 2026-05-12
修改功能: 准入管理页与 product-doc 原型一致；移除与原型无关的联调（阻断目录 / access 评估表单）
-->
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import {
  BAN_REASON_OPTIONS,
  BAN_SCOPE_AGENT_PRODUCT_ZH,
  banReasonZh,
} from '@/entities/access/ban-labels'
import {
  WHITELIST_LIST_ID_RULE_HINT,
  isValidWhitelistListId,
} from '@/entities/access/whitelist-list-id'
import {
  createAccessControlBan,
  createAccessControlWhitelistEntry,
  deleteAccessControlBan,
  deleteAccessControlWhitelistEntry,
  getAccessControlMinVipTier,
  getAccessControlRollout,
  listAccessControlBans,
  listAccessControlWhitelist,
  patchAccessControlMinVipTier,
  patchAccessControlRollout,
  type BanItemDto,
  type WhitelistEntryDto,
} from '@/shared/api/access-control'
import { AppError } from '@/shared/api/errors'
import { adminNotifyManualRefresh, adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import { postAgentAccessEvaluate, type AgentEligibilityEnvelope } from '@/shared/api/agent-runtime'
import { adminTimeZoneParenSuffix } from '@/shared/lib/admin-datetime-display'
import { formatIsoTime } from '@/shared/copy/zh-runtime'
import AdminPage from '@/shared/ui/AdminPage.vue'
import AdminTimeTh from '@/shared/ui/AdminTimeTh.vue'
import {
  AdminPageHeader,
  UiButton,
  UiClipboardTipAction,
  UiInput,
  UiModal,
  UiSelect,
  UiSwitch,
  UiTableAction,
  UiTableEmptyRow,
  adminTableHostOverflowClass,
  type UiSelectOption,
} from '@/shared/ui'

const VIP_MIN = 0
const VIP_MAX = 127

type AccessTab = 'whitelist' | 'bans' | 'vip' | 'rollout' | 'probe'

const route = useRoute()
const router = useRouter()

const tab = computed<AccessTab>(() => {
  const t = route.query.tab as string | undefined
  if (t === 'bans' || t === 'vip' || t === 'rollout' || t === 'probe') return t
  return 'whitelist'
})

const accessUpdatedAtParen = computed(() => adminTimeZoneParenSuffix())

const tabLabels: Record<AccessTab, string> = {
  whitelist: '白名单',
  bans: '用户封禁',
  vip: 'VIP 门槛',
  rollout: '灰度门闸',
  probe: '门禁探测',
}

const accessTabs: AccessTab[] = ['whitelist', 'bans', 'vip', 'rollout', 'probe']

const whitelist = ref<WhitelistEntryDto[]>([])
const bans = ref<BanItemDto[]>([])

const whitelistLoading = ref(false)
const whitelistError = ref<string | null>(null)
const bansLoading = ref(false)
const bansError = ref<string | null>(null)

const vipLoading = ref(false)
const vipError = ref<string | null>(null)
const vipConfigKey = ref('AGENT_MIN_VIP_TIER')
const vipTierInput = ref(String(VIP_MIN))
const vipUpdatedAt = ref<string | null>(null)

const rolloutLoading = ref(false)
const rolloutError = ref<string | null>(null)
const rolloutEnforced = ref(false)
const rolloutSaving = ref(false)

const PAGE_SIZE = 10

const wlSearch = ref('')
const banSearch = ref('')
const wlPage = ref(0)
const banPage = ref(0)
const refreshBusy = ref(false)

function banScopeZh(scope: string): string {
  return scope === 'AGENT_PRODUCT' ? BAN_SCOPE_AGENT_PRODUCT_ZH : scope
}

function clampVipTier(n: number): number {
  if (!Number.isFinite(n)) return VIP_MIN
  return Math.min(VIP_MAX, Math.max(VIP_MIN, Math.trunc(n)))
}

async function loadWhitelist() {
  whitelistLoading.value = true
  whitelistError.value = null
  try {
    const r = await listAccessControlWhitelist()
    whitelist.value = r.items
  } catch (e) {
    whitelistError.value = e instanceof AppError ? e.message : '白名单加载失败'
  } finally {
    whitelistLoading.value = false
  }
}

async function loadBans() {
  bansLoading.value = true
  bansError.value = null
  try {
    const r = await listAccessControlBans()
    bans.value = r.items
  } catch (e) {
    bansError.value = e instanceof AppError ? e.message : '封禁列表加载失败'
  } finally {
    bansLoading.value = false
  }
}

async function loadVip() {
  vipLoading.value = true
  vipError.value = null
  try {
    const r = await getAccessControlMinVipTier()
    vipConfigKey.value = r.configKey
    vipTierInput.value = String(clampVipTier(r.minVipTier))
    vipUpdatedAt.value = r.updatedAt ?? null
  } catch (e) {
    vipError.value = e instanceof AppError ? e.message : 'VIP 策略加载失败'
  } finally {
    vipLoading.value = false
  }
}

async function loadRollout() {
  rolloutLoading.value = true
  rolloutError.value = null
  try {
    const r = await getAccessControlRollout()
    rolloutEnforced.value = r.rolloutWhitelistEnforced
  } catch (e) {
    rolloutError.value = e instanceof AppError ? e.message : '灰度策略加载失败'
  } finally {
    rolloutLoading.value = false
  }
}

async function refreshAll(toastOnSuccess = false) {
  refreshBusy.value = true
  try {
    await Promise.all([loadWhitelist(), loadBans(), loadVip(), loadRollout()])
    adminNotifyManualRefresh(toastOnSuccess, { ok: true, successMessage: '已刷新' })
  } finally {
    refreshBusy.value = false
  }
}

const filteredWl = computed(() => {
  const q = wlSearch.value.trim().toLowerCase()
  if (!q) return whitelist.value
  return whitelist.value.filter(
    (w) =>
      w.listId.toLowerCase().includes(q) ||
      w.userUid.toLowerCase().includes(q) ||
      w.userIdMasked.toLowerCase().includes(q) ||
      w.entryId.toLowerCase().includes(q) ||
      (w.note ?? '').toLowerCase().includes(q),
  )
})

const filteredBans = computed(() => {
  const q = banSearch.value.trim().toLowerCase()
  if (!q) return bans.value
  return bans.value.filter((b) => {
    const zh = banReasonZh(b.reasonCode)
    return (
      b.banId.toLowerCase().includes(q) ||
      b.userUid.toLowerCase().includes(q) ||
      b.reasonCode.toLowerCase().includes(q) ||
      zh.toLowerCase().includes(q)
    )
  })
})

const wlMaxPage = computed(() => Math.max(0, Math.ceil(filteredWl.value.length / PAGE_SIZE) - 1))
const pagedWl = computed(() => {
  const start = wlPage.value * PAGE_SIZE
  return filteredWl.value.slice(start, start + PAGE_SIZE)
})

const banMaxPage = computed(() => Math.max(0, Math.ceil(filteredBans.value.length / PAGE_SIZE) - 1))

const pagedBans = computed(() => {
  const start = banPage.value * PAGE_SIZE
  return filteredBans.value.slice(start, start + PAGE_SIZE)
})

const wlTableScrollX = computed(() => !whitelistLoading.value && pagedWl.value.length > 0)
const banTableScrollX = computed(() => !bansLoading.value && pagedBans.value.length > 0)

watch([wlSearch, () => filteredWl.value.length], () => {
  wlPage.value = 0
})
watch(wlMaxPage, (m) => {
  if (wlPage.value > m) wlPage.value = m
})

watch([banSearch, () => filteredBans.value.length], () => {
  banPage.value = 0
})
watch(banMaxPage, (m) => {
  if (banPage.value > m) banPage.value = m
})

function setTab(next: AccessTab) {
  void router.replace({ path: '/access', query: { ...route.query, tab: next } })
}

const banReasonSelectOptions = computed<UiSelectOption[]>(() =>
  BAN_REASON_OPTIONS.map((o) => ({ value: o.value, label: o.label })),
)

const wlAddOpen = ref(false)
const wlListId = ref('')
const wlUserUid = ref('')
const wlUserIdMasked = ref('')
const wlNote = ref('')
const wlListIdError = ref('')
const wlUserUidError = ref('')
const wlAddSubmitting = ref(false)
const wlAddFatal = ref<string | null>(null)

function openWlAdd() {
  wlListId.value = ''
  wlUserUid.value = ''
  wlUserIdMasked.value = ''
  wlNote.value = ''
  wlListIdError.value = ''
  wlUserUidError.value = ''
  wlAddFatal.value = null
  wlAddOpen.value = true
}

async function confirmWlAdd() {
  wlListIdError.value = ''
  wlUserUidError.value = ''
  wlAddFatal.value = null
  const lid = wlListId.value.trim()
  const uid = wlUserUid.value.trim()
  const masked = wlUserIdMasked.value.trim()
  if (!lid) {
    wlListIdError.value = '请输入名单 ID'
    return
  }
  if (!isValidWhitelistListId(lid)) {
    wlListIdError.value = WHITELIST_LIST_ID_RULE_HINT
    return
  }
  if (!uid) {
    wlUserUidError.value = '请输入用户 UID（tg_id，与运行时匹配）'
    return
  }
  if (/\s/.test(uid)) {
    wlUserUidError.value = 'UID 不应包含空格'
    return
  }
  wlAddSubmitting.value = true
  try {
    await createAccessControlWhitelistEntry({
      listId: lid,
      userUid: uid,
      userIdMasked: masked || undefined,
      note: wlNote.value.trim() || undefined,
    })
    wlAddOpen.value = false
    await loadWhitelist()
    adminToastSuccess('已加入白名单')
  } catch (e) {
    wlAddFatal.value = e instanceof AppError ? [e.code, e.message].filter(Boolean).join(' · ') : '请求失败'
  } finally {
    wlAddSubmitting.value = false
  }
}

const wlRemoveOpen = ref(false)
const wlRemoveTarget = ref<WhitelistEntryDto | null>(null)
const wlRemoveSubmitting = ref(false)
const wlRemoveFatal = ref<string | null>(null)

function requestRemoveWl(row: WhitelistEntryDto) {
  wlRemoveTarget.value = row
  wlRemoveFatal.value = null
  wlRemoveOpen.value = true
}

async function confirmRemoveWl() {
  const row = wlRemoveTarget.value
  if (!row) return
  wlRemoveSubmitting.value = true
  wlRemoveFatal.value = null
  try {
    await deleteAccessControlWhitelistEntry(row.entryId)
    wlRemoveOpen.value = false
    wlRemoveTarget.value = null
    await loadWhitelist()
    adminToastSuccess('已移除')
  } catch (e) {
    wlRemoveFatal.value = e instanceof AppError ? [e.code, e.message].filter(Boolean).join(' · ') : '移除失败'
  } finally {
    wlRemoveSubmitting.value = false
  }
}

const banAddOpen = ref(false)
const banUserUid = ref('')
const banReasonCode = ref('AGENT_USER_BLOCKED')
const banExpiresLocal = ref('')
const banLinkedPause = ref(false)
const banUserError = ref('')
const banAddSubmitting = ref(false)
const banAddFatal = ref<string | null>(null)

function openBanAdd() {
  banUserUid.value = ''
  banReasonCode.value = 'AGENT_USER_BLOCKED'
  banExpiresLocal.value = ''
  banLinkedPause.value = false
  banUserError.value = ''
  banAddFatal.value = null
  banAddOpen.value = true
}

function localDatetimeToIso(local: string): string | null {
  if (!local.trim()) return null
  const d = new Date(local)
  return Number.isNaN(d.getTime()) ? null : d.toISOString()
}

async function confirmBanAdd() {
  banUserError.value = ''
  banAddFatal.value = null
  const uid = banUserUid.value.trim()
  if (!uid) {
    banUserError.value = '请输入用户 UID'
    return
  }
  if (/\s/.test(uid)) {
    banUserError.value = 'UID 不应包含空格'
    return
  }
  banAddSubmitting.value = true
  try {
    await createAccessControlBan({
      userUid: uid,
      reasonCode: banReasonCode.value,
      expiresAt: localDatetimeToIso(banExpiresLocal.value),
      linkedPause: banLinkedPause.value,
    })
    banAddOpen.value = false
    await loadBans()
    adminToastSuccess('已创建封禁')
  } catch (e) {
    banAddFatal.value = e instanceof AppError ? [e.code, e.message].filter(Boolean).join(' · ') : '请求失败'
  } finally {
    banAddSubmitting.value = false
  }
}

const banRevokeOpen = ref(false)
const banRevokeId = ref<string | null>(null)
const banRevokeSubmitting = ref(false)
const banRevokeFatal = ref<string | null>(null)

function requestRevokeBan(banId: string) {
  banRevokeId.value = banId
  banRevokeFatal.value = null
  banRevokeOpen.value = true
}

async function confirmRevokeBan() {
  const id = banRevokeId.value
  if (!id) return
  banRevokeSubmitting.value = true
  banRevokeFatal.value = null
  try {
    await deleteAccessControlBan(id)
    banRevokeOpen.value = false
    banRevokeId.value = null
    await loadBans()
    adminToastSuccess('已撤销封禁')
  } catch (e) {
    banRevokeFatal.value = e instanceof AppError ? [e.code, e.message].filter(Boolean).join(' · ') : '撤销失败'
  } finally {
    banRevokeSubmitting.value = false
  }
}

const vipSaving = ref(false)

async function persistVip() {
  vipSaving.value = true
  vipError.value = null
  try {
    const n = clampVipTier(Number.parseInt(vipTierInput.value, 10))
    const r = await patchAccessControlMinVipTier(n)
    vipTierInput.value = String(clampVipTier(r.minVipTier))
    vipUpdatedAt.value = r.updatedAt ?? null
    adminToastSuccess(`已保存：minVipTier=${r.minVipTier}`)
  } catch (e) {
    vipError.value = e instanceof AppError ? [e.code, e.message].filter(Boolean).join(' · ') : '保存失败'
  } finally {
    vipSaving.value = false
  }
}

async function resetVipToServer() {
  await loadVip()
  adminToastSuccess('已从服务端重新加载')
}

async function saveRollout() {
  rolloutSaving.value = true
  rolloutError.value = null
  try {
    const r = await patchAccessControlRollout(rolloutEnforced.value)
    rolloutEnforced.value = r.rolloutWhitelistEnforced
    adminToastSuccess(`灰度门闸：${r.rolloutWhitelistEnforced ? '开启' : '关闭'}`)
  } catch (e) {
    rolloutError.value = e instanceof AppError ? [e.code, e.message].filter(Boolean).join(' · ') : '保存失败'
    await loadRollout()
  } finally {
    rolloutSaving.value = false
  }
}

const evalUserId = ref('')
const evalChatId = ref('')
const evalLoading = ref(false)
const evalResult = ref<AgentEligibilityEnvelope | null>(null)
const evalError = ref<string | null>(null)

async function runEvaluateProbe() {
  evalError.value = null
  evalResult.value = null
  const uid = evalUserId.value.trim()
  if (!uid) {
    evalError.value = '请输入 userId'
    return
  }
  evalLoading.value = true
  try {
    const chatRaw = evalChatId.value.trim()
    let telegramChatId: number | undefined
    if (chatRaw) {
      const n = Number.parseInt(chatRaw, 10)
      if (!Number.isFinite(n)) {
        evalError.value = 'telegramChatId 须为整数'
        evalLoading.value = false
        return
      }
      telegramChatId = n
    }
    evalResult.value = await postAgentAccessEvaluate({
      userId: uid,
      channel: 'telegram',
      telegramChatId,
    })
  } catch (e) {
    evalError.value = e instanceof AppError ? [e.code, e.message].filter(Boolean).join(' · ') : '探测失败'
  } finally {
    evalLoading.value = false
  }
}

/** 服务端显式下发的 `requiresMainSite`（含 `null`）；字段省略则无徽标。 */
const evalRequiresMainSiteBadge = computed(() => {
  const r = evalResult.value
  if (!r || !Object.prototype.hasOwnProperty.call(r, 'requiresMainSite')) return null
  const v = r.requiresMainSite
  if (v === true) {
    return {
      cls: 'border-amber-500/35 bg-amber-500/10 text-amber-100',
      title:
        'requiresMainSite=true：欠托管绑定，宜引导用户经主站 / H5 完成绑定（常为 AGENT_SUBACCOUNT_ALLOWED=false）。',
      text: 'requiresMainSite: true · 引导主站 / H5',
    }
  }
  if (v === false) {
    return {
      cls: 'border-slate-500/40 bg-slate-800/50 text-slate-200',
      title: 'requiresMainSite=false：当前门禁允许会话（或非「欠绑定」阻断）；无需仅因绑定缺失跳转主站。',
      text: 'requiresMainSite: false',
    }
  }
  return {
    cls: 'border-sky-500/30 bg-sky-950/35 text-sky-100',
    title: 'requiresMainSite=null：非「欠绑定」类语义（例如封禁、灰度 rollout、全局关闸等）。完整原因见 allowed / code / reason。',
    text: 'requiresMainSite: null',
  }
})

function wlRowKey(w: WhitelistEntryDto) {
  return w.entryId
}

onMounted(() => {
  void refreshAll()
})
</script>

<template>
  <AdminPage>
    <AdminPageHeader
      title="准入管理"
      :badges="[{ label: '风控运营', tone: 'sky' }]"
      description="白名单、封禁、VIP 门槛、灰度名单门闸；数据来自 /api/v1/admin/access-control/*。"
      dev-meta="pageId · access.overview"
    >
      <template #actions>
        <UiButton type="button" variant="secondary" size="sm" :loading="refreshBusy" @click="refreshAll(true)">
          刷新
        </UiButton>
      </template>
    </AdminPageHeader>

    <div class="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
      <button
        v-for="t in accessTabs"
        :key="t"
        type="button"
        class="admin-seg"
        :class="
          tab === t
            ? 'admin-seg-active'
            : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
        "
        @click="setTab(t)"
      >
        {{ tabLabels[t] }}
      </button>
    </div>

    <!-- 白名单 -->
    <section v-show="tab === 'whitelist'" class="admin-panel p-4 sm:p-5">
      <div class="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <h2 class="text-sm font-medium text-white">白名单</h2>
        <UiButton type="button" :disabled="whitelistLoading" @click="openWlAdd">添加条目</UiButton>
      </div>
      <p v-if="whitelistError" class="mb-3 text-sm text-rose-300">{{ whitelistError }}</p>
      <div class="mb-4 max-w-lg">
        <UiInput
          v-model="wlSearch"
          type="search"
          label="搜索（前端过滤）"
          placeholder="名单 ID、entryId、UID、掩码、备注…"
        />
      </div>
      <div
        class="rounded-lg border border-slate-800"
        :class="adminTableHostOverflowClass(wlTableScrollX)"
      >
        <table class="min-w-full text-sm">
          <thead class="bg-slate-900/80 text-left text-xs uppercase text-slate-500">
            <tr>
              <th class="px-4 py-2">entryId</th>
              <th class="px-4 py-2">名单ID</th>
              <th class="px-4 py-2">userUid</th>
              <th class="px-4 py-2">展示掩码</th>
              <th class="px-4 py-2">备注</th>
              <th class="px-4 py-2"><AdminTimeTh>加入时间</AdminTimeTh></th>
              <th class="px-4 py-2">操作人</th>
              <th class="px-4 py-2">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            <UiTableEmptyRow
              v-if="whitelistLoading && whitelist.length === 0"
              :colspan="8"
              state="loading"
            />
            <UiTableEmptyRow
              v-else-if="filteredWl.length === 0"
              :colspan="8"
              :state="wlSearch.trim() ? 'filtered' : 'empty'"
              :title="wlSearch.trim() ? '暂无匹配条目' : '暂无条目'"
              :description="wlSearch.trim() ? '可尝试放宽或重置搜索条件。' : '或服务端返回空列表'"
            />
            <tr v-for="w in pagedWl" v-else :key="wlRowKey(w)">
              <td class="max-w-[120px] px-4 py-2 font-mono text-[11px] text-slate-400">
                <span class="truncate" :title="w.entryId">{{ w.entryId }}</span>
              </td>
              <td class="px-4 py-2 font-mono text-xs">{{ w.listId }}</td>
              <td class="px-4 py-2 font-mono text-xs">{{ w.userUid }}</td>
              <td class="px-4 py-2 font-mono text-xs">{{ w.userIdMasked }}</td>
              <td class="max-w-[200px] truncate px-4 py-2 text-slate-300" :title="w.note ?? ''">
                {{ w.note ?? '—' }}
              </td>
              <td class="px-4 py-2 font-mono text-xs tabular-nums text-slate-500">
                {{ formatIsoTime(w.addedAt) }}
              </td>
              <td class="px-4 py-2 text-xs text-slate-400">{{ w.addedBy ?? '—' }}</td>
              <td class="px-4 py-2">
                <UiTableAction variant="rose" icon="trash" @click="requestRemoveWl(w)">移除</UiTableAction>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div
        v-if="filteredWl.length > PAGE_SIZE"
        class="mt-3 flex flex-wrap items-center justify-end gap-2 text-xs text-slate-500"
      >
        <span>{{ wlPage * PAGE_SIZE + 1 }}–{{ Math.min((wlPage + 1) * PAGE_SIZE, filteredWl.length) }} / {{ filteredWl.length }}</span>
        <UiButton
          type="button"
          variant="ghost"
          size="sm"
          :disabled="wlPage <= 0"
          @click="wlPage -= 1"
        >
          上一页
        </UiButton>
        <UiButton
          type="button"
          variant="ghost"
          size="sm"
          :disabled="wlPage >= wlMaxPage"
          @click="wlPage += 1"
        >
          下一页
        </UiButton>
      </div>
    </section>

    <!-- 用户封禁 -->
    <section v-show="tab === 'bans'" class="admin-panel p-4 sm:p-5">
      <div class="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <h2 class="text-sm font-medium text-white">用户封禁</h2>
        <UiButton type="button" :disabled="bansLoading" @click="openBanAdd">新建封禁</UiButton>
      </div>
      <p v-if="bansError" class="mb-3 text-sm text-rose-300">{{ bansError }}</p>
      <div class="mb-4 max-w-lg">
        <UiInput
          v-model="banSearch"
          type="search"
          label="搜索（前端过滤）"
          placeholder="封禁 ID、UID、原因…"
        />
      </div>
      <div
        class="rounded-lg border border-slate-800"
        :class="adminTableHostOverflowClass(banTableScrollX)"
      >
        <table class="min-w-full text-sm">
          <thead class="bg-slate-900/80 text-left text-xs uppercase text-slate-500">
            <tr>
              <th class="px-4 py-2">ID</th>
              <th class="px-4 py-2">用户UID</th>
              <th class="px-4 py-2">原因</th>
              <th class="px-4 py-2">范围</th>
              <th class="px-4 py-2"><AdminTimeTh>到期时间</AdminTimeTh></th>
              <th class="px-4 py-2">暂停联动</th>
              <th class="px-4 py-2"><AdminTimeTh>创建时间</AdminTimeTh></th>
              <th class="px-4 py-2">创建人</th>
              <th class="px-4 py-2">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            <UiTableEmptyRow v-if="bansLoading && bans.length === 0" :colspan="9" state="loading" />
            <UiTableEmptyRow
              v-else-if="filteredBans.length === 0"
              :colspan="9"
              :state="banSearch.trim() ? 'filtered' : 'empty'"
              :title="banSearch.trim() ? '暂无匹配封禁记录' : '暂无封禁记录'"
              :description="banSearch.trim() ? '可尝试放宽或重置搜索条件。' : ''"
            />
            <tr v-for="b in pagedBans" v-else :key="b.banId">
              <td class="max-w-[140px] px-4 py-2">
                <div class="flex items-center gap-1.5 font-mono text-xs">
                  <span class="truncate" :title="b.banId">{{ b.banId }}</span>
                  <UiClipboardTipAction
                    variant="sky"
                    label="复制"
                    :text="b.banId"
                    button-class="shrink-0"
                  />
                </div>
              </td>
              <td class="max-w-[160px] px-4 py-2">
                <div class="flex items-center gap-1.5 font-mono text-xs">
                  <span class="truncate" :title="b.userUid">{{ b.userUid }}</span>
                  <UiClipboardTipAction
                    variant="sky"
                    label="复制"
                    :text="b.userUid"
                    button-class="shrink-0"
                  />
                </div>
              </td>
              <td class="px-4 py-2 text-slate-300">{{ banReasonZh(b.reasonCode) }}</td>
              <td class="px-4 py-2 text-slate-400">{{ banScopeZh(b.scope) }}</td>
              <td class="px-4 py-2 font-mono text-xs tabular-nums text-slate-500">
                {{ b.expiresAt ? formatIsoTime(b.expiresAt) : '永久 / 未设' }}
              </td>
              <td class="px-4 py-2 text-slate-300">{{ b.linkedPause ? '是' : '否' }}</td>
              <td class="px-4 py-2 font-mono text-xs tabular-nums text-slate-500">
                {{ formatIsoTime(b.createdAt) }}
              </td>
              <td class="px-4 py-2 text-xs text-slate-400">{{ b.createdBy ?? '—' }}</td>
              <td class="px-4 py-2">
                <UiTableAction variant="rose" icon="trash" @click="requestRevokeBan(b.banId)">撤销</UiTableAction>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div
        v-if="filteredBans.length > PAGE_SIZE"
        class="mt-3 flex flex-wrap items-center justify-end gap-2 text-xs text-slate-500"
      >
        <span
          >{{ banPage * PAGE_SIZE + 1 }}–{{
            Math.min((banPage + 1) * PAGE_SIZE, filteredBans.length)
          }}
          / {{ filteredBans.length }}</span
        >
        <UiButton
          type="button"
          variant="ghost"
          size="sm"
          :disabled="banPage <= 0"
          @click="banPage -= 1"
        >
          上一页
        </UiButton>
        <UiButton
          type="button"
          variant="ghost"
          size="sm"
          :disabled="banPage >= banMaxPage"
          @click="banPage += 1"
        >
          下一页
        </UiButton>
      </div>
    </section>

    <!-- VIP 门槛 -->
    <section v-show="tab === 'vip'" class="admin-panel space-y-4 p-4 sm:p-5">
      <h2 class="text-sm font-medium text-white">VIP 门槛</h2>
      <p class="text-xs text-slate-500">
        <code class="rounded bg-slate-800 px-1 text-[11px] text-slate-400">{{ vipConfigKey }}</code>
        <span> · 与服务端 membership 策略同窗 · 合法范围 {{ VIP_MIN }}–{{ VIP_MAX }}</span>
      </p>
      <p v-if="vipError" class="text-sm text-rose-300">{{ vipError }}</p>
      <p v-if="vipLoading" class="text-sm text-slate-500">加载中…</p>
      <template v-else>
        <p class="text-xs font-medium text-slate-400">准入最低 VIP（minVipTier）</p>
        <div class="max-w-xs">
          <UiInput
            v-model="vipTierInput"
            type="number"
            label="档位"
            autocomplete="off"
          />
        </div>
        <p v-if="vipUpdatedAt" class="text-xs text-slate-600">
          服务端 updatedAt<span class="font-normal text-slate-500">{{ accessUpdatedAtParen }}</span>：
          <span class="font-mono tabular-nums">{{ formatIsoTime(vipUpdatedAt) }}</span>
        </p>
        <div class="flex flex-wrap gap-2">
          <UiButton type="button" :loading="vipSaving" @click="persistVip">保存</UiButton>
          <UiButton type="button" variant="secondary" :disabled="vipLoading" @click="resetVipToServer">
            从服务端重载
          </UiButton>
        </div>
      </template>
    </section>

    <!-- 灰度门闸 -->
    <section v-show="tab === 'rollout'" class="admin-panel space-y-4 p-4 sm:p-5">
      <h2 class="text-sm font-medium text-white">灰度名单门闸</h2>
      <p class="text-xs leading-relaxed text-slate-500">
        对应服务端
        <code class="rounded bg-slate-800 px-1 font-mono text-[11px]">rolloutWhitelistEnforced</code>
        。开启且用户未列入 rollout 白名单时，
        <code class="rounded bg-slate-800 px-1 font-mono text-[11px]">POST …/access/evaluate</code>
        返回
        <code class="rounded bg-slate-800 px-1 font-mono text-[11px]">AGENT_ROLLOUT_BLOCKED</code>
        （顺序见 BACKEND_SPEC）。
      </p>
      <p v-if="rolloutError" class="text-sm text-rose-300">{{ rolloutError }}</p>
      <p v-if="rolloutLoading" class="text-sm text-slate-500">加载中…</p>
      <template v-else>
        <label class="flex cursor-pointer items-center justify-between gap-3 text-sm text-slate-300">
          <span>强制执行 rollout 白名单（rolloutWhitelistEnforced）</span>
          <UiSwitch v-model="rolloutEnforced" size="sm" aria-label="强制执行 rollout 白名单" />
        </label>
        <UiButton type="button" :loading="rolloutSaving" @click="saveRollout">保存策略</UiButton>
      </template>
    </section>

    <!-- 门禁探测 -->
    <section v-show="tab === 'probe'" class="admin-panel space-y-4 p-4 sm:p-5">
      <h2 class="text-sm font-medium text-white">门禁探测</h2>
      <p class="text-xs leading-relaxed text-slate-500">
        调用
        <code class="rounded bg-slate-800 px-1 font-mono text-[11px]">POST /api/v1/agent/access/evaluate</code>
        ，用于核对封禁、灰度白名单等与控制台配置是否一致。
      </p>
      <div class="grid max-w-xl gap-3">
        <UiInput v-model="evalUserId" label="userId" placeholder="Telegram user id（字符串）" autocomplete="off" />
        <UiInput
          v-model="evalChatId"
          label="telegramChatId（可选）"
          placeholder="与 Phase1 chat_id 放行对齐时填写"
          autocomplete="off"
        />
      </div>
      <UiButton type="button" :loading="evalLoading" @click="runEvaluateProbe">执行探测</UiButton>
      <p v-if="evalError" class="text-sm text-rose-300">{{ evalError }}</p>
      <span
        v-if="evalRequiresMainSiteBadge"
        :class="['inline-flex max-w-full rounded-md border px-2 py-1 text-[11px] font-medium leading-snug', evalRequiresMainSiteBadge.cls]"
        :title="evalRequiresMainSiteBadge.title"
        >{{ evalRequiresMainSiteBadge.text }}</span
      >
      <pre
        v-if="evalResult"
        class="max-h-80 overflow-auto rounded-lg border border-slate-800 bg-slate-950/80 p-3 font-mono text-[11px] leading-relaxed text-emerald-200/90"
        >{{ JSON.stringify(evalResult, null, 2) }}</pre
      >
    </section>

    <!-- 添加白名单 -->
    <UiModal
      v-model:open="wlAddOpen"
      title="添加白名单条目"
      :show-default-close="false"
      description="POST /api/v1/admin/access-control/whitelist · 重复 listId+userUid 返回 409。"
    >
      <div class="space-y-3">
        <p v-if="wlAddFatal" class="text-sm text-rose-300">{{ wlAddFatal }}</p>
        <UiInput
          v-model="wlListId"
          label="名单 ID（listId）"
          placeholder="例如 rollout 或数字主键"
          autocomplete="off"
          :error-message="wlListIdError || undefined"
        />
        <UiInput
          v-model="wlUserUid"
          label="用户 UID（userUid · tg_id）"
          placeholder="与运行时匹配的 canonical id"
          autocomplete="off"
          :error-message="wlUserUidError || undefined"
        />
        <UiInput
          v-model="wlUserIdMasked"
          label="展示掩码（可选 · userIdMasked）"
          placeholder="省略则服务端默认与 userUid 相同"
          autocomplete="off"
        />
        <div>
          <label class="mb-1 block text-xs font-medium text-slate-400" for="access-wl-note">备注（可选）</label>
          <textarea
            id="access-wl-note"
            v-model="wlNote"
            rows="2"
            placeholder="可选"
            class="box-border min-h-[4.5rem] w-full rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white [color-scheme:dark] placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-emerald-600/60"
          />
        </div>
      </div>
      <template #footer>
        <UiButton variant="ghost" type="button" :disabled="wlAddSubmitting" @click="wlAddOpen = false">取消</UiButton>
        <UiButton type="button" :loading="wlAddSubmitting" @click="confirmWlAdd">确定</UiButton>
      </template>
    </UiModal>

    <!-- 移除白名单确认 -->
    <UiModal
      v-model:open="wlRemoveOpen"
      title="移除白名单条目"
      :show-default-close="false"
      description="DELETE /api/v1/admin/access-control/whitelist/{entryId}"
    >
      <p v-if="wlRemoveFatal" class="text-sm text-rose-300">{{ wlRemoveFatal }}</p>
      <p v-else-if="wlRemoveTarget" class="text-sm text-slate-300">
        将移除
        <span class="font-mono text-white">{{ wlRemoveTarget.entryId }}</span>
        （{{ wlRemoveTarget.listId }} · {{ wlRemoveTarget.userUid }}）
      </p>
      <template #footer>
        <UiButton variant="ghost" type="button" :disabled="wlRemoveSubmitting" @click="wlRemoveOpen = false">
          取消
        </UiButton>
        <UiButton variant="danger" type="button" :loading="wlRemoveSubmitting" @click="confirmRemoveWl">
          移除
        </UiButton>
      </template>
    </UiModal>

    <!-- 新建封禁 -->
    <UiModal v-model:open="banAddOpen" title="新建封禁" :show-default-close="false">
      <div class="space-y-3">
        <p v-if="banAddFatal" class="text-sm text-rose-300">{{ banAddFatal }}</p>
        <UiInput
          v-model="banUserUid"
          label="用户UID"
          placeholder="用户 UID"
          autocomplete="off"
          :error-message="banUserError || undefined"
        />
        <UiSelect
          v-model="banReasonCode"
          label="封禁原因"
          placeholder="请选择"
          :options="banReasonSelectOptions"
        />
        <div>
          <label class="mb-1 block text-xs font-medium text-slate-400" for="access-ban-exp">到期时间</label>
          <input
            id="access-ban-exp"
            v-model="banExpiresLocal"
            type="datetime-local"
            class="box-border h-10 w-full rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 px-3 text-sm text-white [color-scheme:dark] focus:outline-none focus:ring-1 focus:ring-emerald-600/60"
          />
          <p class="mt-1 text-xs text-slate-600">留空表示永久 / 未设到期</p>
        </div>
        <label class="flex cursor-pointer items-center justify-between gap-3 text-sm text-slate-300">
          <span>联动暂停实例（数值 userUid 时服务端尝试 PAUSED）</span>
          <UiSwitch v-model="banLinkedPause" size="sm" aria-label="联动暂停实例" />
        </label>
      </div>
      <template #footer>
        <UiButton variant="ghost" type="button" :disabled="banAddSubmitting" @click="banAddOpen = false">取消</UiButton>
        <UiButton type="button" :loading="banAddSubmitting" @click="confirmBanAdd">确定</UiButton>
      </template>
    </UiModal>

    <!-- 撤销封禁确认 -->
    <UiModal
      v-model:open="banRevokeOpen"
      title="撤销封禁"
      :show-default-close="false"
      description="DELETE /api/v1/admin/access-control/bans/{banId}"
    >
      <p v-if="banRevokeFatal" class="text-sm text-rose-300">{{ banRevokeFatal }}</p>
      <template #footer>
        <UiButton variant="ghost" type="button" :disabled="banRevokeSubmitting" @click="banRevokeOpen = false">
          取消
        </UiButton>
        <UiButton variant="danger" type="button" :loading="banRevokeSubmitting" @click="confirmRevokeBan">
          撤销
        </UiButton>
      </template>
    </UiModal>
  </AdminPage>
</template>
