<!--
作者: 杨永的Agent
日期: 2026-05-28
修改功能: 配置项自适应多列网格（STM/SESSION/READ · 字段 2 列）
作者: 杨永的Agent
日期: 2026-05-28
修改功能: MR-MEM-01 续 · GlobalConfigBundle GET/PATCH 可编辑保存（configVersion 乐观锁 · 热生效）
-->
<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'

import MemoryRuntimeConfigFieldRow from '@/features/ai-settings/MemoryRuntimeConfigFieldRow.vue'
import {
  MEMORY_RUNTIME_CONFIG_FIELDS,
  READ_MEMORY_CONFIG_FIELDS,
  SESSION_MEMORY_CONFIG_FIELDS,
  STM_MEMORY_CONFIG_FIELDS,
  coerceDraftValue,
  valuesEqual,
} from '@/features/ai-settings/memory-runtime-config-constants'
import { AppError } from '@/shared/api/errors'
import {
  AGENT_AI_SETTINGS_VERSION_CONFLICT,
  getTradingAgentConfigBundle,
  patchTradingAgentConfigBundle,
  type TradingAgentConfigValue,
} from '@/shared/api/admin-trading-agent-config'
import { adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import UiButton from '@/shared/ui/UiButton.vue'

const loading = ref(true)
const saving = ref(false)
const loadError = ref<string | null>(null)
const configVersion = ref(1)
const appliedKeys = ref<string[]>([])
const envDefaults = ref<Record<string, TradingAgentConfigValue>>({})

const savedValues = reactive<Record<string, TradingAgentConfigValue>>({})
const draftValues = reactive<Record<string, TradingAgentConfigValue>>({})

const dirtyKeys = computed(() =>
  MEMORY_RUNTIME_CONFIG_FIELDS.filter(
    (f) => !valuesEqual(f, draftValues[f.configKey], savedValues[f.configKey]),
  ).map((f) => f.configKey),
)

const hasDirty = computed(() => dirtyKeys.value.length > 0)

function applyBundle(data: Awaited<ReturnType<typeof getTradingAgentConfigBundle>>) {
  configVersion.value = data.configVersion
  appliedKeys.value = data.appliedKeys ?? []
  envDefaults.value = data.defaults ?? {}
  for (const field of MEMORY_RUNTIME_CONFIG_FIELDS) {
    const v = data.values[field.configKey]
    const fallback = field.defaultValue as TradingAgentConfigValue
    savedValues[field.configKey] = v ?? fallback
    draftValues[field.configKey] = v ?? fallback
  }
}

async function loadBundle() {
  loading.value = true
  loadError.value = null
  try {
    applyBundle(await getTradingAgentConfigBundle())
  } catch (e) {
    loadError.value = e instanceof AppError ? e.message : '加载配置失败'
  } finally {
    loading.value = false
  }
}

function isBundleOverride(key: string): boolean {
  return appliedKeys.value.includes(key)
}

function revertDraft() {
  for (const field of MEMORY_RUNTIME_CONFIG_FIELDS) {
    draftValues[field.configKey] = savedValues[field.configKey]!
  }
}

async function saveDirty() {
  if (!hasDirty.value || saving.value) return
  saving.value = true
  const patch: Record<string, TradingAgentConfigValue> = {}
  for (const key of dirtyKeys.value) {
    const meta = MEMORY_RUNTIME_CONFIG_FIELDS.find((f) => f.configKey === key)
    if (!meta) continue
    patch[key] = coerceDraftValue(meta, draftValues[key]!)
  }
  const version = configVersion.value
  try {
    const updated = await patchTradingAgentConfigBundle(
      { values: patch, expectedConfigVersion: version },
      { ifMatch: version },
    )
    applyBundle(updated)
    adminToastSuccess('记忆与上下文配置已保存 · 热生效，无需重启 API')
  } catch (e) {
    if (e instanceof AppError && e.code === AGENT_AI_SETTINGS_VERSION_CONFLICT) {
      adminToastError('配置已被他人更新，已刷新最新版本')
      await loadBundle()
    } else {
      adminToastError(e instanceof AppError ? e.message : '保存失败')
    }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  void loadBundle()
})
</script>

<template>
  <section class="admin-panel space-y-5 p-4 sm:p-5" aria-labelledby="memory-runtime-config-heading">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div class="min-w-0 space-y-1">
        <h2 id="memory-runtime-config-heading" class="text-sm font-medium text-white">
          记忆与上下文（STM / 会话并发 / 只读澄清）
        </h2>
        <p class="text-xs leading-relaxed text-slate-500">
          <code class="font-mono text-[11px]">GET|PATCH /api/v1/admin/trading-agent-config/bundle</code>
          · 对齐 keys §2.1～§2.3。Bundle 覆盖优先于 Env；保存后热生效，无需重启进程。
        </p>
      </div>
      <p
        v-if="!loading && !loadError"
        class="shrink-0 rounded border border-slate-800 bg-slate-950/60 px-2 py-1 font-mono text-[10px] text-slate-500"
      >
        configVersion {{ configVersion }}
      </p>
    </div>

    <div
      class="rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2.5 text-xs leading-relaxed text-slate-400"
      role="note"
    >
      <p class="font-medium text-slate-300">Env 与 Bundle 优先级</p>
      <p class="mt-1">
        未写入 Bundle 的键仍读
        <code class="font-mono text-[11px] text-emerald-400/90">CHAINUP_AGENT_*</code>；已 PATCH 的键标
        <span class="text-emerald-300/90">Bundle 覆盖</span>，同进程立即生效。
      </p>
    </div>

    <p v-if="loading" class="text-sm text-slate-500" role="status">加载 GlobalConfigBundle…</p>
    <p v-else-if="loadError" class="text-sm text-rose-400" role="alert">{{ loadError }}</p>

    <template v-else>
      <div class="space-y-6 border-t border-slate-800/80 pt-4">
        <div class="space-y-3">
          <h3 class="text-xs font-medium uppercase tracking-wide text-slate-400">
            Runtime · Memory / STM（§2.1）
          </h3>
          <ul class="grid grid-cols-1 gap-3 md:grid-cols-2">
            <li v-for="field in STM_MEMORY_CONFIG_FIELDS" :key="field.configKey">
              <MemoryRuntimeConfigFieldRow
                :field="field"
                :model-value="draftValues[field.configKey]!"
                :env-default="envDefaults[field.configKey]"
                :bundle-override="isBundleOverride(field.configKey)"
                :dirty="!valuesEqual(field, draftValues[field.configKey], savedValues[field.configKey])"
                @update:model-value="draftValues[field.configKey] = $event"
              />
            </li>
          </ul>
        </div>

        <div class="space-y-3">
          <h3 class="text-xs font-medium uppercase tracking-wide text-slate-400">
            会话并发 · SESSION_*（§2.2）
          </h3>
          <ul class="grid grid-cols-1 gap-3 md:grid-cols-2">
            <li v-for="field in SESSION_MEMORY_CONFIG_FIELDS" :key="field.configKey">
              <MemoryRuntimeConfigFieldRow
                :field="field"
                :model-value="draftValues[field.configKey]!"
                :env-default="envDefaults[field.configKey]"
                :bundle-override="isBundleOverride(field.configKey)"
                :dirty="!valuesEqual(field, draftValues[field.configKey], savedValues[field.configKey])"
                @update:model-value="draftValues[field.configKey] = $event"
              />
            </li>
          </ul>
        </div>

        <div class="space-y-3">
          <h3 class="text-xs font-medium uppercase tracking-wide text-slate-400">
            只读澄清 · READ_*（§2.3）
          </h3>
          <ul class="grid grid-cols-1 gap-3 md:grid-cols-2">
            <li v-for="field in READ_MEMORY_CONFIG_FIELDS" :key="field.configKey">
              <MemoryRuntimeConfigFieldRow
                :field="field"
                :model-value="draftValues[field.configKey]!"
                :env-default="envDefaults[field.configKey]"
                :bundle-override="isBundleOverride(field.configKey)"
                :dirty="!valuesEqual(field, draftValues[field.configKey], savedValues[field.configKey])"
                @update:model-value="draftValues[field.configKey] = $event"
              />
            </li>
          </ul>
        </div>
      </div>

      <div
        v-if="hasDirty"
        class="flex flex-wrap items-center gap-3 border-t border-slate-800/80 pt-4"
      >
        <UiButton type="button" variant="primary" :disabled="saving" @click="saveDirty">
          {{ saving ? '保存中…' : `保存变更（${dirtyKeys.length}）` }}
        </UiButton>
        <UiButton type="button" variant="ghost" :disabled="saving" @click="revertDraft">
          撤销未保存
        </UiButton>
        <p class="text-xs text-slate-500">保存后立即热生效，无需重启 Agent API。</p>
      </div>
    </template>
  </section>
</template>
