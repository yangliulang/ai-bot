<!--
作者: 杨永的Agent
日期: 2026-05-12
修改功能: 主内容区壳（dl- 前缀；无顶栏/侧栏/H5 Tab）；防钓鱼提示条置顶
日期: 2026-05-15
修改功能: ConfigProvider 增加 zh_CN，与全站中文文案一致并减少 Ant Design Vue 日期/分页等隐式英文回退
-->
<script setup lang="ts">
import { ConfigProvider } from 'ant-design-vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { RouterView } from 'vue-router'

import { deeplinkAntdTheme } from '@/theme/deeplinkAntdTheme'
import DeeplinkSafetyStrip from '@/shared/ui/DeeplinkSafetyStrip.vue'
</script>

<template>
  <div class="dl-deeplink-app antialiased">
    <DeeplinkSafetyStrip />
    <main class="dl-main dl-main--standalone">
      <div class="dl-main__inner">
        <ConfigProvider :locale="zhCN" :theme="deeplinkAntdTheme">
          <RouterView />
        </ConfigProvider>
      </div>
    </main>
  </div>
</template>
