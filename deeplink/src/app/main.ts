/*
作者: 杨永的Agent
日期: 2026-05-12
修改功能: Ant Design Vue 注册；deeplink-shell CSS；Pinia + Router 挂载
 */
import 'ant-design-vue/dist/reset.css'

import '@/assets/deeplink-shell.css'
import '@/assets/main.css'

import Antd from 'ant-design-vue'
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from '@/app/App.vue'
import router from '@/app/router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(Antd)
app.mount('#app')
