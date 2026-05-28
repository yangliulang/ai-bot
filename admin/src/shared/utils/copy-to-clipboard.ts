/*
作者: 杨永的Agent
日期: 2026-05-15
修改功能: `navigator.clipboard` 不可用或非安全上下文时用 **textarea + execCommand** 回退
*/

/** 写入系统剪贴板；失败时返回 `false`。 */
export async function copyTextToClipboard(text: string): Promise<boolean> {
  const s = text ?? ''
  if (typeof s !== 'string' || s.length === 0) return false

  if (
    typeof navigator !== 'undefined' &&
    navigator.clipboard &&
    typeof navigator.clipboard.writeText === 'function'
  ) {
    try {
      await navigator.clipboard.writeText(s)
      return true
    } catch {
      /* fallback below */
    }
  }

  if (typeof document === 'undefined') return false

  try {
    const ta = document.createElement('textarea')
    ta.value = s
    ta.setAttribute('readonly', '')
    ta.setAttribute('aria-hidden', 'true')
    ta.tabIndex = -1
    ta.style.position = 'fixed'
    ta.style.left = '0'
    ta.style.top = '0'
    ta.style.opacity = '0'
    ta.style.pointerEvents = 'none'
    document.body.appendChild(ta)
    ta.focus()
    ta.select()
    ta.setSelectionRange(0, s.length)
    const ok = document.execCommand('copy')
    document.body.removeChild(ta)
    return ok
  } catch {
    return false
  }
}
