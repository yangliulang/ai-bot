/** 在选区两端包裹 Markdown 标记（无选区时插入占位并已选中） */
export function markdownLiteWrapSelection(
  value: string,
  start: number,
  end: number,
  wrapBefore: string,
  wrapAfter: string,
  emptyPlaceholder: string,
): { next: string; focusStart: number; focusEnd: number } {
  const hasSel = start !== end;
  const slice = hasSel ? value.slice(start, end) : emptyPlaceholder;
  const next = `${value.slice(0, start)}${wrapBefore}${slice}${wrapAfter}${value.slice(end)}`;
  const innerStart = start + wrapBefore.length;
  const innerEnd = innerStart + slice.length;
  return { next, focusStart: innerStart, focusEnd: innerEnd };
}

/** 在逻辑行行首插入前缀（若在列表项内容内，则插在列表前缀之后） */
export function markdownLiteInsertPrefixAtLogicalLineHead(
  value: string,
  caret: number,
  prefix: string,
): { next: string; focus: number } {
  const lineStart = value.lastIndexOf("\n", caret - 1) + 1;
  let lineEnd = value.indexOf("\n", caret);
  if (lineEnd < 0) lineEnd = value.length;

  let insertAt = lineStart;
  const line = value.slice(lineStart, lineEnd);
  const mo = /^(\s*)([-*]|\d+\.)\s+/.exec(line);
  if (mo) {
    insertAt = lineStart + mo[0].length;
  }

  const next = `${value.slice(0, insertAt)}${prefix}${value.slice(insertAt)}`;
  const focus = caret >= insertAt ? caret + prefix.length : insertAt + prefix.length;
  return { next, focus };
}
