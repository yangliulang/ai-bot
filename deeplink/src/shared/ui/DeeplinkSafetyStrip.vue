<!--
作者: 杨永的Agent
日期: 2026-05-12
修改功能: Deeplink 顶部防钓鱼提示条（不编造域名，仅原则性文案）
-->
<script setup lang="ts">
defineProps<{
  /** 显式展示当前页由产品文案提供的「官方核验」短链或说明时再用 */
  verifiedLabel?: string
}>()
</script>

<template>
  <div
    class="border-b border-slate-200/90 bg-slate-100/90 px-4 py-2 text-center text-xs leading-snug text-slate-600 backdrop-blur-sm"
    role="status"
  >
    <template v-if="verifiedLabel">
      {{ verifiedLabel }}
    </template>
    <template v-else>
      请通过<strong class="font-medium text-slate-800">官方 App / 站内入口 / Bot 可信链接</strong>打开本页；勿在陌生站点输入账户或 API
      密钥。具体域名与参数以产品文档为准。
    </template>
  </div>
</template>
