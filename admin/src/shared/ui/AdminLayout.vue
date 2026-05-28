<!--
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 顶栏「退出登录」图标 **h-4 w-4**，与用户区图标一致
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 时点切换：**UTC+8 / UTC**，与列表头后缀 `(UTC+8)`、`(UTC)` 一致；title 单行说明接口 JSON 仍为 UTC ISO 8601
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 顶栏 **时间展示模式**（UTC+8 ↔ UTC）· FE_HANDOFF 接续
作者: 杨永的Agent
日期: 2026-05-21
修改功能: 左侧导航展开/收起（236px ↔ 72px · 底部折叠钮 · localStorage 记忆 · 对齐原型 Layout）
修改功能: 收起态 hover 在图标右侧显示菜单文案浮层（Teleport + fixed，规避 overflow 裁切）
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 收起态侧栏导航图标由 16px 增至 20px，便于识别
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 主内容区仅保留 px-6 py-6 全宽铺满（去掉 max-w-7xl/mx-auto，避免宽屏两侧留白）
作者: 杨永的Agent
日期: 2026-05-17
修改功能: 顶栏 sticky top-0 z-40、bg-slate-900/90 + backdrop-blur，右侧用户/退出区 shrink-0，主内容滚动时东部栏保持固定可见
-->
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import {
  adminDatetimeModeButtonLabel,
  toggleAdminDatetimeDisplayMode,
} from '@/shared/lib/admin-datetime-display'

import { useAuthStore } from '@/stores/auth'
import UiButton from '@/shared/ui/UiButton.vue'
import UiModal from '@/shared/ui/UiModal.vue'

import { ADMIN_NAV_ICON_SVG } from '@/assets/icons/admin-nav'
import logOutSvg from '@/assets/icons/log-out.svg?raw'
import productMarkSvg from '@/assets/icons/product-mark.svg?raw'
import sessionUserSvg from '@/assets/icons/session-user.svg?raw'
import {
  ADMIN_MENU_MODULE_LABELS,
  ADMIN_NAV_MODULE_ORDER,
  navLeavesByModule,
  type AdminNavModule,
} from '@/shared/config/admin-nav'

const SIDEBAR_WIDTH_EXPANDED_PX = 236
const SIDEBAR_WIDTH_COLLAPSED_PX = 72
const SIDEBAR_COLLAPSED_STORAGE_KEY = 'admin_sider_collapsed'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

auth.hydrateFromStorage()

const siderCollapsed = ref(false)
const logoutConfirmOpen = ref(false)

interface NavFlyoutState {
  label: string
  left: number
  top: number
  active: boolean
}

const navFlyout = ref<NavFlyoutState | null>(null)

onMounted(() => {
  try {
    siderCollapsed.value = localStorage.getItem(SIDEBAR_COLLAPSED_STORAGE_KEY) === '1'
  } catch {
    siderCollapsed.value = false
  }
})

function toggleSiderCollapsed() {
  siderCollapsed.value = !siderCollapsed.value
  try {
    localStorage.setItem(SIDEBAR_COLLAPSED_STORAGE_KEY, siderCollapsed.value ? '1' : '0')
  } catch {
    /* ignore quota / private mode */
  }
}

const asideWidthStyle = computed(() => ({
  width: `${siderCollapsed.value ? SIDEBAR_WIDTH_COLLAPSED_PX : SIDEBAR_WIDTH_EXPANDED_PX}px`,
}))

watch(siderCollapsed, (collapsed) => {
  if (!collapsed) navFlyout.value = null
})

function showCollapsedNavFlyout(
  event: MouseEvent | FocusEvent,
  label: string,
  path: string,
) {
  if (!siderCollapsed.value) return
  const el = event.currentTarget
  if (!(el instanceof HTMLElement)) return
  const rect = el.getBoundingClientRect()
  navFlyout.value = {
    label,
    left: rect.right + 10,
    top: rect.top + rect.height / 2,
    active: isNavActive(path),
  }
}

function hideCollapsedNavFlyout() {
  navFlyout.value = null
}

function openLogoutConfirm() {
  logoutConfirmOpen.value = true
}

function cancelLogout() {
  logoutConfirmOpen.value = false
}

function confirmLogout() {
  auth.logout()
  logoutConfirmOpen.value = false
  router.push({ path: '/login' })
}

function navLinkClass(path: string): string {
  const active = isNavActive(path)
  if (siderCollapsed.value) {
    const base =
      'group relative flex items-center justify-center rounded-md py-2.5 text-sm transition-[color,background-color] duration-200 [transition-timing-function:var(--ease-ui)]'
    return active
      ? `${base} bg-slate-800/55 text-emerald-400`
      : `${base} text-slate-400 hover:bg-slate-800/40 hover:text-slate-100`
  }
  const base =
    'group relative flex items-center gap-2.5 rounded-md border-l-2 border-transparent py-1.5 pl-2.5 pr-3 text-sm transition-[color,background-color,border-color] duration-200 [transition-timing-function:var(--ease-ui)]'
  return active
    ? `${base} border-emerald-500 bg-slate-800/55 text-emerald-400`
    : `${base} text-slate-400 hover:border-slate-600 hover:bg-slate-800/40 hover:text-slate-100`
}

function isNavActive(path: string): boolean {
  const p = route.path
  if (path === '/runtime/executions') {
    return p.startsWith('/runtime/executions')
  }
  if (path === '/system/channels') {
    return p.startsWith('/system/channels')
  }
  if (path === '/agents/instances') {
    return p.startsWith('/agents/instances')
  }
  return p === path || p.startsWith(`${path}/`)
}

function iconClass(path: string): string {
  const size = siderCollapsed.value ? 'h-5 w-5' : 'h-4 w-4'
  const base = `nav-sidebar-icon inline-flex ${size} shrink-0 transition-[color,width,height] duration-150`
  return isNavActive(path)
    ? `${base} text-emerald-400`
    : `${base} text-slate-500 group-hover:text-emerald-400`
}

const groups = computed(() => {
  return ADMIN_NAV_MODULE_ORDER.map((m: AdminNavModule) => ({
    module: m,
    label: ADMIN_MENU_MODULE_LABELS[m],
    leaves: navLeavesByModule(m),
  }))
})

const datetimeBtnLabel = computed(() => adminDatetimeModeButtonLabel())
const datetimeToggleTitle = '切换全局时点标注：UTC+8 ↔ UTC（接口 JSON 为 UTC ISO 8601）'
</script>

<template>
  <div class="min-h-[100dvh] bg-slate-950 text-slate-100 antialiased">
    <div class="flex min-h-[100dvh]">
      <aside
        class="admin-pro-sider sticky top-0 z-30 flex h-[100dvh] shrink-0 flex-col overflow-hidden border-r border-slate-800/90 bg-slate-900/70 shadow-[inset_1px_0_0_0_rgba(255,255,255,0.04)] backdrop-blur-md transition-[width] duration-300 [transition-timing-function:var(--ease-ui)]"
        :class="{ 'admin-pro-sider--collapsed': siderCollapsed }"
        :style="asideWidthStyle"
      >
        <div
          class="shrink-0 border-b border-slate-800"
          :class="siderCollapsed ? 'px-2 py-3' : 'px-4 py-4'"
        >
          <div
            class="flex min-w-0 items-center"
            :class="siderCollapsed ? 'justify-center' : 'gap-3'"
          >
            <span
              class="admin-product-mark inline-flex h-10 w-10 shrink-0 items-center justify-center"
              aria-hidden="true"
            >
              <span class="admin-product-mark__inner" v-html="productMarkSvg" />
            </span>
            <div v-show="!siderCollapsed" class="min-w-0">
              <p class="text-sm font-semibold tracking-tight text-white/95">AI 交易智能体</p>
              <p class="mt-0.5 text-xs leading-snug text-slate-500">扁平入口 · 运行态视图为主</p>
            </div>
          </div>
        </div>
        <nav
          class="min-h-0 flex-1 space-y-6 overflow-x-hidden overflow-y-auto py-4"
          :class="siderCollapsed ? 'px-1.5' : 'px-2'"
        >
          <div v-for="g in groups" :key="g.module">
            <div
              v-show="!siderCollapsed"
              class="mb-2 px-2 text-[11px] font-medium uppercase tracking-wider text-slate-500"
            >
              {{ g.label }}
            </div>
            <div class="space-y-0.5">
              <RouterLink
                v-for="leaf in g.leaves"
                :key="leaf.pageId"
                :to="leaf.path"
                :class="navLinkClass(leaf.path)"
                :aria-label="siderCollapsed ? leaf.label : undefined"
                @mouseenter="showCollapsedNavFlyout($event, leaf.label, leaf.path)"
                @mouseleave="hideCollapsedNavFlyout"
                @focusin="showCollapsedNavFlyout($event, leaf.label, leaf.path)"
                @focusout="hideCollapsedNavFlyout"
              >
                <!-- 图标来自 src/assets/icons/admin-nav/*.svg（currentColor），仅静态资源 -->
                <span :class="iconClass(leaf.path)" v-html="ADMIN_NAV_ICON_SVG[leaf.iconKey]" />
                <span v-if="!siderCollapsed" class="min-w-0 flex-1 truncate">
                  {{ leaf.label }}
                </span>
              </RouterLink>
            </div>
          </div>
        </nav>
        <button
          type="button"
          class="admin-sider-trigger flex h-12 w-full shrink-0 items-center justify-center border-t border-slate-800/90 text-slate-400 transition-[color,background-color] duration-200 [transition-timing-function:var(--ease-ui)] hover:bg-white/10 hover:text-white active:scale-[0.98]"
          :aria-label="siderCollapsed ? '展开侧栏' : '收起侧栏'"
          :aria-expanded="!siderCollapsed"
          @click="toggleSiderCollapsed"
        >
          <svg
            class="h-4 w-4 transition-transform duration-300 [transition-timing-function:var(--ease-ui)]"
            :class="siderCollapsed ? 'rotate-180' : ''"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
      </aside>
      <div class="flex min-w-0 flex-1 flex-col">
        <header
          v-if="auth.username"
          class="sticky top-0 z-40 flex min-h-[4.5rem] shrink-0 flex-wrap items-center justify-end gap-4 border-b border-slate-800 bg-slate-900/90 px-6 py-4 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)] backdrop-blur-md"
          aria-label="当前登录用户"
        >
          <UiButton
            variant="ghost"
            size="sm"
            class="mr-auto shrink-0 text-[11px] text-slate-400 hover:text-slate-100"
            type="button"
            :title="datetimeToggleTitle"
            @click="toggleAdminDatetimeDisplayMode"
          >
            {{ datetimeBtnLabel }}
          </UiButton>
          <div class="flex shrink-0 items-center gap-4">
            <div
              class="group flex min-h-10 min-w-0 items-center gap-2.5 text-right"
              :title="
                '会话保存在本机 localStorage，换设备或清除站点数据后需重新登录。当前用户：' +
                (auth.username ?? '')
              "
            >
              <span
                class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-slate-700/80 bg-slate-800/45 text-slate-500 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)] transition-[color,border-color] duration-200 [transition-timing-function:var(--ease-ui)] group-hover:border-emerald-500/35 group-hover:text-emerald-400/90"
                aria-hidden="true"
              >
                <span
                  class="inline-block h-4 w-4 [&>svg]:block [&>svg]:h-full [&>svg]:w-full"
                  v-html="sessionUserSvg"
                />
              </span>
              <span
                class="max-w-[16rem] truncate text-sm font-semibold leading-tight tracking-tight text-slate-100 sm:max-w-xs md:max-w-sm"
                :title="auth.username ?? ''"
              >
                {{ auth.username }}
              </span>
            </div>
            <UiButton
              variant="ghost"
              size="sm"
              class="shrink-0 text-slate-400 hover:text-white"
              type="button"
              @click="openLogoutConfirm"
            >
              <span
                class="inline-block h-4 w-4 shrink-0 opacity-90 [&>svg]:block [&>svg]:h-full [&>svg]:w-full"
                aria-hidden="true"
                v-html="logOutSvg"
              />
              退出登录
            </UiButton>
          </div>
        </header>
        <main class="flex-1 w-full min-w-0 px-6 py-6">
          <RouterView />
        </main>
      </div>
    </div>

    <Teleport to="body">
      <div
        v-if="siderCollapsed && navFlyout"
        class="nav-sidebar-flyout-portal pointer-events-none fixed z-[200] -translate-y-1/2 whitespace-nowrap rounded-md border bg-slate-900/98 px-2.5 py-1 text-xs font-medium shadow-[0_8px_24px_-6px_rgba(0,0,0,0.55)] backdrop-blur-sm"
        :class="
          navFlyout.active
            ? 'border-emerald-500/45 text-emerald-200'
            : 'border-slate-700/90 text-slate-100'
        "
        :style="{ left: `${navFlyout.left}px`, top: `${navFlyout.top}px` }"
        role="tooltip"
      >
        {{ navFlyout.label }}
      </div>
    </Teleport>

    <UiModal
      v-model:open="logoutConfirmOpen"
      title="退出登录"
      description="确定要退出当前控制台会话吗？本地登录状态将被清除。"
      :show-default-close="false"
    >
      <template #footer>
        <UiButton variant="ghost" type="button" @click="cancelLogout">取消</UiButton>
        <UiButton variant="danger" type="button" @click="confirmLogout">确认退出</UiButton>
      </template>
    </UiModal>
  </div>
</template>

<style scoped>
.admin-product-mark {
  position: relative;
  border-radius: var(--radius-ui-lg);
  color: rgb(52 211 153);
  background: linear-gradient(
    145deg,
    rgb(30 41 59 / 0.96) 0%,
    rgb(15 23 42 / 0.98) 48%,
    rgb(15 23 42 / 1) 100%
  );
  box-shadow:
    inset 0 1px 0 0 rgb(255 255 255 / 0.07),
    0 0 0 1px rgb(16 185 129 / 0.22),
    0 12px 28px -10px rgb(0 0 0 / 0.65);
}

.admin-product-mark::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(
    135deg,
    rgb(52 211 153 / 0.35),
    rgb(16 185 129 / 0.08) 40%,
    rgb(148 163 184 / 0.12) 100%
  );
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.admin-product-mark__inner {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (prefers-reduced-motion: no-preference) {
  .admin-product-mark {
    animation: admin-product-mark-glow 2.75s ease-in-out infinite;
  }

  .admin-product-mark__inner :deep(svg) {
    animation: admin-product-mark-icon 3.25s ease-in-out infinite;
  }
}

@keyframes admin-product-mark-glow {
  0%,
  100% {
    box-shadow:
      inset 0 1px 0 0 rgb(255 255 255 / 0.07),
      0 0 0 1px rgb(16 185 129 / 0.18),
      0 10px 26px -10px rgb(0 0 0 / 0.6),
      0 0 18px -4px rgb(16 185 129 / 0.12);
  }

  50% {
    box-shadow:
      inset 0 1px 0 0 rgb(255 255 255 / 0.09),
      0 0 0 1px rgb(52 211 153 / 0.28),
      0 14px 32px -10px rgb(0 0 0 / 0.72),
      0 0 28px -2px rgb(52 211 153 / 0.22);
  }
}

@keyframes admin-product-mark-icon {
  0%,
  100% {
    transform: translateY(0) scale(1);
    filter: drop-shadow(0 0 3px rgb(52 211 153 / 0.3));
  }

  50% {
    transform: translateY(-2px) scale(1.05);
    filter: drop-shadow(0 0 10px rgb(52 211 153 / 0.45));
  }
}

.admin-product-mark__inner :deep(svg) {
  display: block;
  height: 1.625rem;
  width: 1.625rem;
}
.nav-sidebar-icon :deep(svg) {
  display: block;
  width: 1rem;
  height: 1rem;
}

.admin-pro-sider--collapsed .nav-sidebar-icon :deep(svg) {
  width: 1.25rem;
  height: 1.25rem;
}

.admin-sider-trigger {
  background: rgb(0 0 0 / 0.2);
}

.nav-sidebar-flyout-portal {
  box-shadow:
    inset 0 1px 0 0 rgb(255 255 255 / 0.06),
    0 8px 24px -6px rgb(0 0 0 / 0.55);
}

.nav-sidebar-flyout-portal::before {
  content: '';
  position: absolute;
  right: 100%;
  top: 50%;
  margin-right: 4px;
  border: 5px solid transparent;
  border-right-color: rgb(51 65 85 / 0.95);
  transform: translateY(-50%);
}

@media (prefers-reduced-motion: reduce) {
  .admin-pro-sider {
    transition-duration: 0.01ms !important;
  }

  .admin-sider-trigger svg {
    transition-duration: 0.01ms !important;
  }

}
</style>
