<!--
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 嵌套模型表 table-fixed + colgroup 统一列宽
修改功能: 模型子表增加 apiModel 列
修改功能: 厂商行展开按钮 — SVG 箭头替代过小 Unicode 三角
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 「厂商与模型」可展开台账表（对齐 product-doc `/ai-settings` Tab 1）
-->
<script setup lang="ts">
import { computed } from 'vue'

import type { LlmModelSummary, LlmProviderSummary } from '@/shared/api/admin-ai-settings'
import {
  healthStatusTag,
  probeResultToHealth,
  type LlmHealthStatus,
} from '@/features/ai-settings/catalog-constants'
import { UiButton, UiSwitch, UiTableAction, UiTableEmptyRow } from '@/shared/ui'

const props = defineProps<{
  providers: LlmProviderSummary[]
  models: LlmModelSummary[]
  probeByProvider: Record<string, string>
  expandedProviderIds: string[]
  deletingProviderId: string | null
  deletingModelId: string | null
}>()

const emit = defineEmits<{
  'update:expandedProviderIds': [ids: string[]]
  'add-provider': []
  'edit-provider': [row: LlmProviderSummary]
  'delete-provider': [row: LlmProviderSummary]
  probe: [providerId: string]
  'add-model': [row: LlmProviderSummary]
  'toggle-model-enabled': [model: LlmModelSummary, enabled: boolean]
  'delete-model': [model: LlmModelSummary]
}>()

const expandedSet = computed(() => new Set(props.expandedProviderIds))

function modelsForProvider(providerId: string): LlmModelSummary[] {
  return props.models.filter((m) => m.providerId === providerId)
}

function modelCounts(providerId: string): { active: number; total: number } {
  const rows = modelsForProvider(providerId)
  return {
    active: rows.filter((m) => m.status === 'enabled').length,
    total: rows.length,
  }
}

function healthFor(providerId: string): LlmHealthStatus {
  return probeResultToHealth(props.probeByProvider[providerId])
}

function isExpanded(providerId: string): boolean {
  return expandedSet.value.has(providerId)
}

function toggleExpand(providerId: string) {
  const next = new Set(props.expandedProviderIds)
  if (next.has(providerId)) {
    next.delete(providerId)
  } else {
    next.add(providerId)
  }
  emit('update:expandedProviderIds', [...next])
}

function formatContext(n: number | null): string {
  if (n == null) return '—'
  return n.toLocaleString('en-US')
}

function formatApiModel(m: LlmModelSummary): string {
  const wire = m.apiModel?.trim()
  if (!wire || wire === m.modelId) return '—'
  return wire
}

/** 各厂商展开区嵌套表共用列宽（table-fixed + colgroup） */
const MODEL_NESTED_COLGROUP = [
  '32%',
  '24%',
  '14%',
  '12%',
  '8%',
  '10%',
] as const
</script>

<template>
  <section class="admin-panel overflow-hidden">
    <div
      class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/90 px-4 py-3 sm:px-5"
    >
      <h2 class="text-sm font-medium text-white">厂商与模型</h2>
      <UiButton type="button" size="sm" @click="emit('add-provider')">添加厂商</UiButton>
    </div>

    <div class="overflow-x-auto">
      <table class="min-w-full text-left text-sm">
        <thead class="bg-slate-900/80 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th class="w-10 px-2 py-3" />
            <th class="min-w-[8rem] px-3 py-3">厂商</th>
            <th class="whitespace-nowrap px-3 py-3">下属模型</th>
            <th class="min-w-[12rem] px-3 py-3">Base URL</th>
            <th class="min-w-[8rem] px-3 py-3">密钥</th>
            <th class="whitespace-nowrap px-3 py-3">健康</th>
            <th class="min-w-[11rem] px-3 py-3 text-right">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800">
          <template v-for="p in providers" :key="p.providerId">
            <tr class="bg-slate-950/20 hover:bg-slate-900/35">
              <td class="px-2 py-2 align-middle">
                <button
                  type="button"
                  class="flex h-9 w-9 shrink-0 items-center justify-center rounded-[var(--radius-ui)] text-slate-300 transition-[transform,colors] duration-200 ease-ui hover:bg-slate-800 hover:text-white active:scale-[0.98]"
                  :aria-expanded="isExpanded(p.providerId)"
                  :aria-label="isExpanded(p.providerId) ? '收起行' : '展开行'"
                  @click="toggleExpand(p.providerId)"
                >
                  <svg
                    viewBox="0 0 16 16"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4 transition-transform duration-200 ease-ui"
                    :class="isExpanded(p.providerId) ? 'rotate-90' : ''"
                    aria-hidden="true"
                  >
                    <path
                      d="M6 4.5 10.5 8 6 11.5"
                      stroke="currentColor"
                      stroke-width="1.75"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </button>
              </td>
              <td class="px-3 py-2 align-middle">
                <div class="font-medium text-slate-100">{{ p.displayName }}</div>
                <div class="mt-0.5 font-mono text-[11px] text-slate-500">{{ p.providerId }}</div>
              </td>
              <td class="px-3 py-2 align-middle font-mono text-xs tabular-nums text-slate-400">
                {{ modelCounts(p.providerId).active }}/{{ modelCounts(p.providerId).total }}
              </td>
              <td class="max-w-[16rem] px-3 py-2 align-middle">
                <span
                  class="block truncate font-mono text-xs text-slate-400"
                  :title="p.baseUrl"
                >
                  {{ p.baseUrl }}
                </span>
              </td>
              <td class="px-3 py-2 align-middle">
                <span
                  class="block max-w-[10rem] truncate text-xs text-slate-500"
                  :title="p.secretRef ?? undefined"
                >
                  {{ p.configured ? p.secretRef ?? '已配置' : '未配置' }}
                </span>
              </td>
              <td class="px-3 py-2 align-middle">
                <span
                  class="inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium"
                  :class="healthStatusTag(healthFor(p.providerId)).className"
                >
                  {{ healthStatusTag(healthFor(p.providerId)).label }}
                </span>
              </td>
              <td class="px-3 py-2 align-middle">
                <div class="flex flex-wrap items-center justify-end gap-1">
                  <UiButton type="button" size="sm" variant="ghost" @click="emit('edit-provider', p)">
                    修改
                  </UiButton>
                  <UiButton type="button" size="sm" variant="ghost" @click="emit('probe', p.providerId)">
                    探测
                  </UiButton>
                  <UiButton
                    type="button"
                    size="sm"
                    variant="ghost"
                    class="text-rose-300/90 hover:text-rose-200"
                    :loading="deletingProviderId === p.providerId"
                    :disabled="deletingProviderId !== null && deletingProviderId !== p.providerId"
                    @click="emit('delete-provider', p)"
                  >
                    删除
                  </UiButton>
                </div>
              </td>
            </tr>
            <tr v-if="isExpanded(p.providerId)" class="bg-slate-950/50">
              <td colspan="7" class="px-3 py-4 sm:px-5">
                <div
                  class="rounded-[var(--radius-ui-lg)] border border-slate-800/90 bg-slate-900/40 p-4"
                >
                  <div class="mb-3 flex flex-wrap items-center gap-2">
                    <UiButton type="button" size="sm" variant="secondary" @click="emit('add-model', p)">
                      添加模型
                    </UiButton>
                    <p v-if="probeByProvider[p.providerId]" class="text-xs text-slate-500">
                      最近探测：{{ probeByProvider[p.providerId] }}
                    </p>
                  </div>
                  <div class="overflow-x-auto rounded-lg border border-slate-800">
                    <table class="ai-settings-model-table w-full min-w-[40rem] table-fixed text-left text-sm">
                      <colgroup>
                        <col
                          v-for="(width, colIdx) in MODEL_NESTED_COLGROUP"
                          :key="colIdx"
                          :style="{ width }"
                        />
                      </colgroup>
                      <thead class="bg-slate-900/70 text-xs uppercase text-slate-500">
                        <tr>
                          <th class="px-3 py-2 font-medium">modelId</th>
                          <th class="px-3 py-2 font-medium">apiModel</th>
                          <th class="px-3 py-2 font-medium">上下文窗</th>
                          <th class="px-3 py-2 font-medium">状态</th>
                          <th class="px-3 py-2 font-medium">启用</th>
                          <th class="px-3 py-2 text-right font-medium">操作</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-slate-800/80">
                        <tr
                          v-for="m in modelsForProvider(p.providerId)"
                          :key="m.modelId"
                          class="hover:bg-slate-900/30"
                        >
                          <td class="min-w-0 px-3 py-2 align-middle">
                            <span
                              class="block truncate font-mono text-xs text-emerald-200/90"
                              :title="m.modelId"
                            >
                              {{ m.modelId }}
                            </span>
                          </td>
                          <td class="min-w-0 px-3 py-2 align-middle">
                            <span
                              class="block truncate font-mono text-xs text-slate-400"
                              :title="formatApiModel(m) === '—' ? undefined : formatApiModel(m)"
                            >
                              {{ formatApiModel(m) }}
                            </span>
                          </td>
                          <td
                            class="px-3 py-2 align-middle font-mono text-xs tabular-nums text-slate-400"
                          >
                            {{ formatContext(m.contextWindowTokens) }}
                          </td>
                          <td class="px-3 py-2 align-middle">
                            <span
                              class="inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium"
                              :class="
                                m.status === 'enabled'
                                  ? 'border-sky-500/35 bg-sky-500/10 text-sky-200'
                                  : 'border-slate-600 bg-slate-800/50 text-slate-400'
                              "
                            >
                              {{ m.status === 'enabled' ? '现行' : m.status }}
                            </span>
                          </td>
                          <td class="px-3 py-2 align-middle">
                            <UiSwitch
                              size="sm"
                              :model-value="m.status === 'enabled'"
                              :aria-label="`启用 ${m.modelId}`"
                              @update:model-value="emit('toggle-model-enabled', m, $event)"
                            />
                          </td>
                          <td class="px-3 py-2 text-right align-middle">
                            <UiTableAction
                              variant="rose"
                              icon="trash"
                              :loading="deletingModelId === m.modelId"
                              :disabled="deletingModelId !== null && deletingModelId !== m.modelId"
                              @click="emit('delete-model', m)"
                            >
                              删除
                            </UiTableAction>
                          </td>
                        </tr>
                        <UiTableEmptyRow
                          v-if="modelsForProvider(p.providerId).length === 0"
                          :colspan="6"
                          state="empty"
                          title="暂无模型"
                          description="点击「添加模型」登记 modelId（可选 apiModel）"
                        />
                      </tbody>
                    </table>
                  </div>
                </div>
              </td>
            </tr>
          </template>
          <UiTableEmptyRow
            v-if="!providers.length"
            :colspan="7"
            state="empty"
            title="暂无厂商"
            description="点击「添加厂商」填写 Base URL 与密钥引用；首张台账创建后可展开行并添加模型。"
          >
            <UiButton type="button" size="sm" @click="emit('add-provider')">添加厂商</UiButton>
          </UiTableEmptyRow>
        </tbody>
      </table>
    </div>
  </section>
</template>
