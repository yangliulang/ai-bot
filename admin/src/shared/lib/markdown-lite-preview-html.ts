/**
 * Markdown Lite 安全预览 HTML（子集：标题/列表/加粗/斜体/围栏代码，无原始 HTML）
 *
 * 作者: 杨永的Agent
 * 日期: 2026-05-19
 * 修改功能: Prompt 编辑器预览 pane
 */

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function inlineFormat(s: string): string {
  let out = escapeHtml(s)
  out = out.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  out = out.replace(/\*(.+?)\*/g, '<em>$1</em>')
  out = out.replace(/`([^`]+)`/g, '<code>$1</code>')
  return out
}

export function markdownLiteToPreviewHtml(source: string): string {
  const trimmed = source.trim()
  if (!trimmed) return ''

  const parts = trimmed.split(/```/)
  const blocks: string[] = []

  for (let i = 0; i < parts.length; i++) {
    const chunk = parts[i] ?? ''
    if (i % 2 === 1) {
      const fence = chunk.replace(/^\w*\n?/, '')
      blocks.push(`<pre><code>${escapeHtml(fence.trimEnd())}</code></pre>`)
      continue
    }

    const lines = chunk.split('\n')
    let html = ''
    let inUl = false
    let inOl = false

    const closeLists = () => {
      if (inUl) {
        html += '</ul>'
        inUl = false
      }
      if (inOl) {
        html += '</ol>'
        inOl = false
      }
    }

    for (const line of lines) {
      const t = line.trimEnd()
      if (!t.trim()) {
        closeLists()
        continue
      }
      if (/^###\s+/.test(t)) {
        closeLists()
        html += `<h3>${inlineFormat(t.replace(/^###\s+/, ''))}</h3>`
        continue
      }
      if (/^##\s+/.test(t)) {
        closeLists()
        html += `<h2>${inlineFormat(t.replace(/^##\s+/, ''))}</h2>`
        continue
      }
      if (/^#\s+/.test(t)) {
        closeLists()
        html += `<h1>${inlineFormat(t.replace(/^#\s+/, ''))}</h1>`
        continue
      }
      if (/^[-*]\s+/.test(t)) {
        if (!inUl) {
          closeLists()
          html += '<ul>'
          inUl = true
        }
        html += `<li>${inlineFormat(t.replace(/^[-*]\s+/, ''))}</li>`
        continue
      }
      if (/^\d+\.\s+/.test(t)) {
        if (!inOl) {
          closeLists()
          html += '<ol>'
          inOl = true
        }
        html += `<li>${inlineFormat(t.replace(/^\d+\.\s+/, ''))}</li>`
        continue
      }
      closeLists()
      html += `<p>${inlineFormat(t)}</p>`
    }
    closeLists()
    blocks.push(html)
  }

  return blocks.join('')
}
