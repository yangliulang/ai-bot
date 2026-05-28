<!--
作者: 杨永的Agent
日期: 2026-05-28
修改功能: MR-MEM-01 · 澄清会话协查折叠 + resume_classified 时间线块
作者: 杨永的Agent
日期: 2026-05-27
修改功能: 执行详情总览 · 治理四折叠（skill-scope / 拼装追溯 / Skill Spec / Canonical · FE_HANDOFF 2026-05-26）
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'

import {
  getAdminObservabilityExecutionTimeline,
  getScenarioSkillScope,
  type AdminAgentExecutionItem,
  type ScenarioSkillScopeResponse,
} from '@/shared/api/admin-observability'
import { AppError } from '@/shared/api/errors'
import {
  bindingToAssemblyLayers,
  isAnalysisStrategyBinding,
  parseSkillSpecReadFromTimeline,
  resolvePromptBindingForExecution,
} from '@/shared/lib/execution-prompt-assembly'
import {
  MEMORY_LTM_REVOKE_REQUESTED_EVENT,
  MEMORY_LTM_REVOKE_USER_HINT,
  MEMORY_RESUME_CLASSIFIED_EVENT,
  MEMORY_SESSION_CLEARED_EVENT,
  MEMORY_STM_CLEAR_USER_HINT,
  isWritePathScenario,
} from '@/shared/lib/write-path-display'
import {
  formatResolvedSlotsSoFar,
  pickLatestClarifySessionFromTimeline,
  pickLatestResumeClassifiedFromTimeline,
  zhClarifyLifecycleState,
  zhResumeClassifierDecision,
} from '@/shared/lib/clarify-session-display'
import { EXECUTION_DETAIL_COPY } from '@/shared/copy/execution-detail-copy'

const props = defineProps<{
  detail: AdminAgentExecutionItem
}>()

const skillScope = ref<ScenarioSkillScopeResponse | null>(null)
const skillScopeLoading = ref(false)
const skillScopeError = ref<string | null>(null)

const timelineLoading = ref(false)
const timelineError = ref<string | null>(null)

const scenarioId = computed(() => (props.detail.scenarioId ?? '').trim())
const executionId = computed(() => props.detail.executionId)

const timelineItems = ref<
  Awaited<ReturnType<typeof getAdminObservabilityExecutionTimeline>>['items']
>([])

const resolvedBinding = computed(() =>
  resolvePromptBindingForExecution({
    scenarioId: scenarioId.value,
    resolvedPromptBinding: props.detail.resolvedPromptBinding,
    timelineItems: timelineItems.value,
  }),
)

const assemblyLayers = computed(() => {
  const b = resolvedBinding.value
  return b ? bindingToAssemblyLayers(b) : []
})

const skillSpecRead = computed(() => parseSkillSpecReadFromTimeline(timelineItems.value))

const isWritePath = computed(() => isWritePathScenario(scenarioId.value))

const hasMemoryTimelineEvents = computed(() =>
  timelineItems.value.some(
    (ev) =>
      ev.eventName === MEMORY_SESSION_CLEARED_EVENT ||
      ev.eventName === MEMORY_LTM_REVOKE_REQUESTED_EVENT ||
      ev.eventName === MEMORY_RESUME_CLASSIFIED_EVENT,
  ),
)

const latestClarifySession = computed(() => pickLatestClarifySessionFromTimeline(timelineItems.value))

const latestResumeClassified = computed(() =>
  pickLatestResumeClassifiedFromTimeline(timelineItems.value),
)

const showClarifySessionProbe = computed(
  () => Boolean(latestClarifySession.value) || Boolean(latestResumeClassified.value),
)

const showMemoryProductHints = computed(() => isWritePath.value || hasMemoryTimelineEvents.value)

const canonicalFromTimeline = computed(() => {
  for (const ev of timelineItems.value) {
    const op =
      typeof ev.summary.canonicalOp === 'string' ? ev.summary.canonicalOp.trim() : ''
    const venue = typeof ev.summary.venue === 'string' ? ev.summary.venue.trim() : ''
    if (op || venue) return { canonicalOp: op || '—', venue: venue || '—' }
  }
  return null
})

async function loadSkillScope(sid: string) {
  skillScopeLoading.value = true
  skillScopeError.value = null
  skillScope.value = null
  try {
    skillScope.value = await getScenarioSkillScope(sid)
  } catch (e) {
    skillScopeError.value = e instanceof AppError ? e.message : '加载 Skill 范围失败'
  } finally {
    skillScopeLoading.value = false
  }
}

async function loadTimeline(id: string) {
  timelineLoading.value = true
  timelineError.value = null
  try {
    const res = await getAdminObservabilityExecutionTimeline(id)
    timelineItems.value = res.items ?? []
  } catch (e) {
    timelineItems.value = []
    timelineError.value = e instanceof AppError ? e.message : '加载时间线失败'
  } finally {
    timelineLoading.value = false
  }
}

watch(
  scenarioId,
  (sid) => {
    if (!sid) {
      skillScope.value = null
      skillScopeError.value = null
      return
    }
    void loadSkillScope(sid)
  },
  { immediate: true },
)

watch(
  executionId,
  (id) => {
    if (!id) return
    void loadTimeline(id)
  },
  { immediate: true },
)

function zhSkillScopeMode(mode: string): string {
  const map: Record<string, string> = {
    write_skill: '写路径 · 主 Skill',
    read_only: '读侧 · 无写 Skill',
    unmapped_write: '写路径 · 未映射',
  }
  return map[mode] ?? mode
}
</script>

<template>
  <section class="rounded-lg border border-slate-800 bg-slate-900/35">
    <header class="border-b border-slate-800/90 px-4 py-3">
      <h2 class="text-sm font-semibold text-slate-200">Prompt 治理追溯</h2>
      <p class="mt-1 text-[11px] leading-relaxed text-slate-500">
        与产品 5176 原型对齐：Skill 范围、拼装层、Skill Spec 读侧、Canonical 摘要（数据来自 observability API）。
      </p>
    </header>

    <div class="divide-y divide-slate-800/80">
      <details class="group px-4 py-3" open>
        <summary class="cursor-pointer list-none text-sm font-medium text-slate-300 marker:content-none">
          <span class="inline-flex items-center gap-2">
            <span class="text-slate-500 transition group-open:rotate-90">▸</span>
            场景 · Skill 范围
          </span>
        </summary>
        <div class="mt-3 space-y-3 text-sm">
          <div class="text-right">
            <RouterLink
              class="text-xs text-sky-400/90 hover:text-sky-300 hover:underline"
              to="/ai/tool-registry"
            >
              技能与工具
            </RouterLink>
          </div>
          <p v-if="!scenarioId" class="text-slate-500">无 scenarioId，无法查询 Skill 范围。</p>
          <p v-else-if="skillScopeLoading" class="text-slate-500">加载 Skill 范围…</p>
          <p v-else-if="skillScopeError" class="text-rose-400/90">{{ skillScopeError }}</p>
          <template v-else-if="skillScope">
            <p class="text-xs leading-relaxed text-slate-400">{{ skillScope.narrative }}</p>
            <dl class="grid gap-2 text-xs sm:grid-cols-2">
              <div>
                <dt class="text-slate-500">mode</dt>
                <dd class="font-mono text-slate-300">{{ zhSkillScopeMode(skillScope.mode) }}</dd>
              </div>
              <div>
                <dt class="text-slate-500">策略包</dt>
                <dd class="break-all font-mono text-emerald-200/85">
                  <RouterLink
                    v-if="skillScope.promptStrategyPackId"
                    class="hover:underline"
                    :to="{
                      name: 'prompts.editor',
                      params: { promptPackId: skillScope.promptStrategyPackId },
                    }"
                  >
                    {{ skillScope.promptStrategyPackId
                    }}{{
                      skillScope.promptStrategyVersion
                        ? `@v${skillScope.promptStrategyVersion}`
                        : ''
                    }}
                  </RouterLink>
                  <span v-else>—</span>
                </dd>
              </div>
              <div v-if="skillScope.promptSkillScopeRef" class="sm:col-span-2">
                <dt class="text-slate-500">skillSpecRef</dt>
                <dd class="break-all font-mono text-slate-400">{{ skillScope.promptSkillScopeRef }}</dd>
              </div>
            </dl>
            <div v-if="skillScope.skills.length" class="overflow-x-auto rounded-md border border-slate-800">
              <table class="min-w-full text-left text-xs">
                <thead class="border-b border-slate-800 text-slate-500">
                  <tr>
                    <th class="px-3 py-2">skillId</th>
                    <th class="px-3 py-2">version</th>
                    <th class="px-3 py-2">contract</th>
                    <th class="px-3 py-2">role</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-800/80 text-slate-300">
                  <tr v-for="sk in skillScope.skills" :key="sk.skillId">
                    <td class="px-3 py-2 font-mono">{{ sk.skillId }}</td>
                    <td class="px-3 py-2 font-mono">{{ sk.skillSpecVersion ?? '—' }}</td>
                    <td class="px-3 py-2">
                      {{ sk.contractComplete === true ? '完整' : sk.contractComplete === false ? '缺项' : '—' }}
                    </td>
                    <td class="px-3 py-2">{{ sk.role ?? '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="text-xs text-slate-500">skills 为空（读侧或未映射写路径）。</p>
          </template>
        </div>
      </details>

      <details class="group px-4 py-3" open>
        <summary class="cursor-pointer list-none text-sm font-medium text-slate-300 marker:content-none">
          <span class="inline-flex items-center gap-2">
            <span class="text-slate-500 transition group-open:rotate-90">▸</span>
            Prompt 拼装追溯
          </span>
        </summary>
        <div class="mt-3 space-y-3 text-sm">
          <div class="text-right">
            <RouterLink
              class="text-xs text-sky-400/90 hover:text-sky-300 hover:underline"
              to="/prompts/strategy"
            >
              提示词治理
            </RouterLink>
          </div>
          <p v-if="!resolvedBinding" class="text-slate-500">
            无 resolvedPromptBinding；请查看时间线 Tab 中的
            <span class="font-mono text-slate-400">agent.prompt.binding_resolved</span>。
          </p>
          <template v-else>
            <p class="text-xs text-slate-500">
              场景键
              <span class="font-mono text-slate-400">{{
                resolvedBinding.scenarioId ?? (scenarioId || '—')
              }}</span>
              <span
                v-if="resolvedBinding.tradingPromptPackId"
                class="ml-2 inline-flex rounded border border-slate-700 px-1.5 py-0 text-[10px]"
              >
                {{ isAnalysisStrategyBinding(resolvedBinding) ? '分析槽' : '场景槽' }}
              </span>
            </p>
            <div class="overflow-x-auto rounded-md border border-slate-800">
              <table class="min-w-full text-left text-xs">
                <thead class="border-b border-slate-800 text-slate-500">
                  <tr>
                    <th class="px-3 py-2">层</th>
                    <th class="px-3 py-2">来源</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-800/80">
                  <tr v-for="row in assemblyLayers" :key="row.layer">
                    <td class="whitespace-nowrap px-3 py-2 text-slate-400">{{ row.layer }}</td>
                    <td class="px-3 py-2 font-mono text-slate-300">
                      <RouterLink
                        v-if="row.promptPackId"
                        class="text-emerald-200/90 hover:underline"
                        :to="{ name: 'prompts.editor', params: { promptPackId: row.promptPackId } }"
                      >
                        {{ row.source }}
                      </RouterLink>
                      <span v-else>{{ row.source }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
        </div>
      </details>

      <details class="group px-4 py-3">
        <summary class="cursor-pointer list-none text-sm font-medium text-slate-300 marker:content-none">
          <span class="inline-flex items-center gap-2">
            <span class="text-slate-500 transition group-open:rotate-90">▸</span>
            Skill Spec 读侧
          </span>
        </summary>
        <div class="mt-3 space-y-3 text-sm">
          <div class="text-right">
            <RouterLink
              class="text-xs text-sky-400/90 hover:text-sky-300 hover:underline"
              to="/ai/tool-registry"
            >
              技能规范
            </RouterLink>
          </div>
          <p v-if="timelineLoading" class="text-slate-500">加载时间线…</p>
          <p v-else-if="timelineError" class="text-rose-400/90">{{ timelineError }}</p>
          <p v-else-if="!skillSpecRead" class="text-xs text-slate-500">
            时间线中暂无
            <span class="font-mono text-slate-400">agent.skill.spec_read</span>
            （写路径执行后通常会出现）。
          </p>
          <dl v-else class="grid gap-2 rounded-md border border-slate-800 bg-slate-950/40 p-3 text-xs sm:grid-cols-2">
            <div>
              <dt class="text-slate-500">skillId</dt>
              <dd class="font-mono text-slate-200">{{ skillSpecRead.skillId }}</dd>
            </div>
            <div>
              <dt class="text-slate-500">skillSpecVersion</dt>
              <dd class="font-mono text-slate-300">{{ skillSpecRead.skillSpecVersion }}</dd>
            </div>
            <div>
              <dt class="text-slate-500">phase</dt>
              <dd>{{ skillSpecRead.phase ?? '—' }}</dd>
            </div>
            <div class="sm:col-span-2">
              <dt class="text-slate-500">specDigest</dt>
              <dd class="break-all font-mono text-slate-400">{{ skillSpecRead.specDigest ?? '—' }}</dd>
            </div>
          </dl>
        </div>
      </details>

      <details class="group px-4 py-3">
        <summary class="cursor-pointer list-none text-sm font-medium text-slate-300 marker:content-none">
          <span class="inline-flex items-center gap-2">
            <span class="text-slate-500 transition group-open:rotate-90">▸</span>
            Canonical 摘要
          </span>
        </summary>
        <div class="mt-3 space-y-2 text-sm">
          <p class="text-xs text-slate-500">
            从时间线 <span class="font-mono text-slate-400">summary.canonicalOp</span> /
            <span class="font-mono text-slate-400">venue</span> 提取（写路径 / 交易所步骤）。
          </p>
          <p v-if="timelineLoading" class="text-slate-500">加载时间线…</p>
          <p v-else-if="!canonicalFromTimeline" class="text-slate-500">本执行时间线暂无 Canonical 字段。</p>
          <dl v-else class="grid gap-2 text-xs sm:grid-cols-2">
            <div>
              <dt class="text-slate-500">canonicalOp</dt>
              <dd class="font-mono text-slate-300">{{ canonicalFromTimeline.canonicalOp }}</dd>
            </div>
            <div>
              <dt class="text-slate-500">venue</dt>
              <dd class="font-mono text-slate-300">{{ canonicalFromTimeline.venue }}</dd>
            </div>
          </dl>
        </div>
      </details>

      <details v-if="showClarifySessionProbe" class="group px-4 py-3">
        <summary class="cursor-pointer list-none text-sm font-medium text-slate-300 marker:content-none">
          <span class="inline-flex items-center gap-2">
            <span class="text-slate-500 transition group-open:rotate-90">▸</span>
            澄清会话协查（MR-MEM-01）
          </span>
        </summary>
        <div class="mt-3 space-y-3 text-xs leading-relaxed text-slate-400">
          <p class="text-[11px] text-slate-500">
            自时间线 summary 解析
            <span class="font-mono text-slate-400">lifecycleState</span> /
            <span class="font-mono text-slate-400">clarifyTurn</span> /
            <span class="font-mono text-slate-400">resolvedSlotsSoFar</span>；实时快照只读 API 就绪后可补拉取。
          </p>
          <div
            v-if="latestClarifySession"
            class="rounded-md border border-amber-800/40 bg-amber-950/20 px-3 py-2.5"
          >
            <p class="font-medium text-amber-100/90">ClarifySessionSnapshot</p>
            <dl class="mt-2 grid gap-2 sm:grid-cols-2">
              <div>
                <dt class="text-slate-500">lifecycleState</dt>
                <dd class="font-mono text-slate-300">
                  {{ zhClarifyLifecycleState(String(latestClarifySession.lifecycleState)) }}
                </dd>
              </div>
              <div v-if="latestClarifySession.clarifyTurn != null">
                <dt class="text-slate-500">clarifyTurn</dt>
                <dd class="font-mono text-slate-300">{{ latestClarifySession.clarifyTurn }}</dd>
              </div>
              <div class="sm:col-span-2">
                <dt class="text-slate-500">resolvedSlotsSoFar</dt>
                <dd class="font-mono text-slate-300">
                  {{ formatResolvedSlotsSoFar(latestClarifySession.resolvedSlotsSoFar) }}
                </dd>
              </div>
              <div v-if="latestClarifySession.pendingClarifyKind" class="sm:col-span-2">
                <dt class="text-slate-500">pendingClarifyKind</dt>
                <dd class="font-mono text-slate-300">{{ latestClarifySession.pendingClarifyKind }}</dd>
              </div>
            </dl>
          </div>
          <div
            v-if="latestResumeClassified"
            class="rounded-md border border-teal-800/40 bg-teal-950/20 px-3 py-2.5"
          >
            <p class="font-medium text-teal-100/90">agent.memory.resume_classified</p>
            <dl class="mt-2 grid gap-2 sm:grid-cols-2">
              <div>
                <dt class="text-slate-500">decision</dt>
                <dd class="font-mono text-slate-300">
                  {{ zhResumeClassifierDecision(latestResumeClassified.decision) }}
                </dd>
              </div>
              <div v-if="latestResumeClassified.confidence != null">
                <dt class="text-slate-500">confidence</dt>
                <dd class="font-mono text-slate-300">{{ latestResumeClassified.confidence }}</dd>
              </div>
              <div v-if="latestResumeClassified.episodePickReason" class="sm:col-span-2">
                <dt class="text-slate-500">episodePickReason</dt>
                <dd class="font-mono text-slate-300">{{ latestResumeClassified.episodePickReason }}</dd>
              </div>
            </dl>
          </div>
        </div>
      </details>

      <details v-if="showMemoryProductHints" class="group px-4 py-3">
        <summary class="cursor-pointer list-none text-sm font-medium text-slate-300 marker:content-none">
          <span class="inline-flex items-center gap-2">
            <span class="text-slate-500 transition group-open:rotate-90">▸</span>
            会话记忆（Telegram）
          </span>
        </summary>
        <div class="mt-3 space-y-3 text-xs leading-relaxed text-slate-400">
          <p class="text-[11px] text-slate-500">
            与 C 端回复一致；协查页 <span class="font-mono text-slate-400">stmL0Messages</span> 待只读 API 就绪后展示。
          </p>
          <div class="rounded-md border border-sky-800/40 bg-sky-950/20 px-3 py-2.5">
            <p class="font-medium text-sky-100/90">{{ EXECUTION_DETAIL_COPY.memoryStmHintTitle }}</p>
            <p class="mt-1.5">{{ MEMORY_STM_CLEAR_USER_HINT }}</p>
          </div>
          <div class="rounded-md border border-rose-800/40 bg-rose-950/20 px-3 py-2.5">
            <p class="font-medium text-rose-100/90">{{ EXECUTION_DETAIL_COPY.memoryLtmHintTitle }}</p>
            <p class="mt-1.5">{{ MEMORY_LTM_REVOKE_USER_HINT }}</p>
          </div>
        </div>
      </details>
    </div>
  </section>
</template>
