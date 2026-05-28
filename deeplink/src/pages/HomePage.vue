<!--
作者: 杨永的Agent
日期: 2026-05-12
修改功能: 「开启助手」跳转 onboarding 多步流程首屏 `onboarding-validate`
日期: 2026-05-12
修改功能: 样式类 coolbit- 改为 dl-；首页主标题去交易所化
日期: 2026-05-12
修改功能: 对齐 product-doc/Web HomePage（无顶栏底栏，仅主内容）
日期: 2026-05-11
修改功能: 「开启助手」前 URL 若有 tg_* 已由全局路由写入 session 预填，本页仅占位不写逻辑
日期: 2026-05-15
修改功能: 路由跳转显式吞掉 Promise 拒绝，避免控制台未处理的 navigation 异常
-->
<script setup lang="ts">
import { ArrowRightOutlined, ThunderboltOutlined } from '@ant-design/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

function goOnboarding() {
  void router.push({ name: 'onboarding-validate' }).catch(() => {
    /* 导航被取消或重复进入同一路由等，无需向用户抛错 */
  })
}
</script>

<template>
  <div class="dl-home-layout">
    <header class="dl-home-hero dl-home-hero--centered">
      <span class="dl-home-badge">体验版</span>
      <div class="dl-home-hero-icon" aria-hidden="true">
        <ThunderboltOutlined />
      </div>
      <h1 class="dl-page-title dl-home-title">AI 交易助手</h1>
      <p class="dl-home-lead">
        通过 Telegram 与 AI 助手对话，完成<strong>交易所内</strong>的交易与查询；问答、分析类任务同样计入账单流水。
      </p>
    </header>

    <a-card :bordered="false" class="dl-home-card dl-home-card__cta">
      <p class="dl-home-steps-hint">
        <span class="dl-home-steps-hint__emph">一键开通</span>
        <span class="dl-home-steps-hint__sep">→</span>
        <span>绑定 Telegram</span>
        <span class="dl-home-steps-hint__sep">→</span>
        <span>对话中使用</span>
      </p>
      <a-button
        type="primary"
        size="large"
        block
        class="dl-home-primary-btn"
        @click="goOnboarding"
      >
        <span class="inline-flex w-full items-center justify-center gap-2">
          <span>开启助手</span>
          <ArrowRightOutlined />
        </span>
      </a-button>
    </a-card>
  </div>
</template>
