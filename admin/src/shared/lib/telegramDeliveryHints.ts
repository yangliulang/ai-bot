/** 根据 Telegram getWebhookInfo 的 last_error_message 给出控制台侧排查提示 */

export function telegramDeliveryHints(raw: string | null | undefined): string[] {
  const msg = raw?.trim()
  if (!msg) return []
  const low = msg.toLowerCase()
  const hints: string[] = []

  if (low.includes('404') || /\bnot found\b/.test(low)) {
    hints.push(
      '公网回调返回了 404：请确认网关是否把 /webhook/telegram/ 反代到 Agent（8080），而非 Deeplink SPA。',
    )
    hints.push(
      '若调整了 PUBLIC_BASE_URL，请执行「使用默认 URL 注册 / 更新」或核对自定义 HTTPS 地址。',
    )
  }

  if (low.includes('wrong response from the webhook') && hints.length === 0) {
    hints.push(
      'Telegram 认为 HTTP 响应不符合预期。请核对 TLS、反向代理是否对 POST 返回 200。',
    )
  }

  if (low.includes('ssl') || low.includes('certificate') || low.includes('tls')) {
    hints.push(
      '证书或 TLS 异常：确认 fullchain（含中间证）已部署，Telegram 可通过 443 访问该主机。',
    )
  }

  if (low.includes('timeout') || low.includes('timed out')) {
    hints.push(
      '请求超时：放宽网关超时；确认服务端 Webhook 先 200 再后台处理（默认 BackgroundTasks）。',
    )
  }

  return hints
}
