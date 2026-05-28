/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  /** 为 true 时 Prompt 模块调用 `/api/v1/admin/prompt-packs*`；失败回退本地 mock */
  readonly VITE_USE_PROMPT_API: string;
  /** 为 true 且配置了 VITE_API_BASE_URL 时，执行记录列表调用 `GET /api/v1/admin/observability/executions` */
  readonly VITE_USE_OBSERVABILITY_API: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
