/**
 * 将 skill-spec Markdown §1～§6 解析为控制台可渲染结构（产品实现层，非文档索引）。
 */

export type SpecTable = {
  headers: string[];
  rows: string[][];
};

/** §3 确认章 prose 解析为分条规则（供控制台展示） */
export type ConfirmRule = {
  title: string;
  body: string;
};

export type SkillOperationView = {
  title?: string;
  businessLine?: string;
  skillId?: string;
  version?: string;
  scenarioId?: string;
  status?: string;
  requiredParams: SpecTable;
  validations: SpecTable;
  confirmation: SpecTable;
  unknown: SpecTable;
  refusals: SpecTable;
  apiText: string;
  /** §3 表格外的对话约束，已结构化 */
  confirmRules: ConfirmRule[];
  sectionNotes: Record<string, string>;
};

function stripMd(s: string): string {
  return s
    .replace(/\*\*/g, "")
    .replace(/`/g, "")
    .replace(/\[[^\]]*\]\([^)]*\)/g, "")
    .trim();
}

function parseTableBlock(block: string): SpecTable | null {
  const lines = block
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l.startsWith("|") && l.endsWith("|"));
  if (lines.length < 2) return null;

  const parseRow = (line: string) =>
    line
      .slice(1, -1)
      .split("|")
      .map((c) => stripMd(c.trim()));

  const headers = parseRow(lines[0]);
  const rows: string[][] = [];
  for (let i = 1; i < lines.length; i++) {
    if (/^\|[\s\-:|]+\|$/.test(lines[i])) continue;
    rows.push(parseRow(lines[i]));
  }
  if (!rows.length) return null;
  return { headers, rows };
}

function extractSection(body: string, headingPart: string): string {
  const re = new RegExp(
    `(?:^|\\n)## ${headingPart}[^\\n]*\\n([\\s\\S]*?)(?=\\n## |\\z)`,
  );
  const m = body.match(re);
  return m?.[1]?.trim() ?? "";
}

function firstTableInSection(section: string): SpecTable {
  const chunks = section.split(/\n\n+/);
  for (const chunk of chunks) {
    const t = parseTableBlock(chunk);
    if (t && t.rows.length) return t;
  }
  return { headers: [], rows: [] };
}

function proseAfterTables(section: string): string {
  return section
    .replace(/^##[^\n]*\n/, "")
    .split("\n")
    .filter((l) => !l.trim().startsWith("|"))
    .join("\n")
    .trim();
}

/** 将 §3 非表格 prose 拆成「标题 + 说明」分条 */
export function parseConfirmRules(prose: string): ConfirmRule[] {
  const text = prose.trim();
  if (!text) return [];

  const rules: ConfirmRule[] = [];
  const paragraphs = text.split(/\n\s*\n+/);

  for (const para of paragraphs) {
    const lines = para
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean);
    for (const line of lines) {
      const labeled = line.match(/^\*\*([^*]+)\*\*[：:]\s*(.*)$/);
      if (labeled) {
        rules.push({
          title: stripMd(labeled[1]),
          body: stripMd(labeled[2]),
        });
        continue;
      }
      const heading = line.match(/^\*\*([^*]+)\*\*\s*(.*)$/);
      if (heading) {
        let body = stripMd(heading[2]);
        body = body.replace(/^[（(][^）)]*[）)]\s*[：:]?\s*/, "").trim();
        rules.push({ title: stripMd(heading[1]), body });
        continue;
      }
      if (rules.length) {
        const last = rules[rules.length - 1];
        last.body = [last.body, stripMd(line)].filter(Boolean).join(" ");
      } else {
        rules.push({ title: "说明", body: stripMd(line) });
      }
    }
  }

  return rules.filter((r) => r.title.trim() || r.body.trim());
}

/** 运营向：规则标题 */
export function formatConfirmRuleTitle(raw: string): string {
  const t = raw.trim();
  if (/步骤\s*3|确认之前/i.test(t)) return "在用户确认之前";
  if (/MUST\s*可见|卡片.*可见|须.*可见/i.test(t)) return "确认卡须向用户展示";
  if (/第二张卡|建议价/i.test(t)) return "价格建议须单独确认";
  if (/数字一致性|卡面/i.test(t)) return "展示数字须与下单一致";
  return t
    .replace(/MUST/gi, "必须")
    .replace(/类型\s*A/gi, "二次确认")
    .replace(/\s+/g, " ")
    .trim();
}

/** 运营向：单条说明拆成短句 */
export function formatConfirmRuleLines(body: string): string[] {
  let t = body
    .replace(/call_exchange_write/gi, "代为下单")
    .replace(/FR-T12/gi, "价格偏离保护")
    .replace(/API\s*载荷/gi, "实际下单参数")
    .replace(/hallucination/gi, "编造成交或结果")
    .replace(/类型\s*A/gi, "二次确认")
    .replace(/[（(]\s*[）)]/g, "")
    .replace(/\s+/g, " ")
    .trim();
  if (!t) return [];
  return t
    .split(/[；;]/)
    .map((s) => s.trim())
    .filter(Boolean)
    .map((s) => s.replace(/^禁止\s*/, "不得").replace(/^\*\*|\*\*$/g, ""));
}

export function parseSkillOperationView(body: string): SkillOperationView {
  const metaSec = extractSection(body, "元数据");
  const metaTable = firstTableInSection(metaSec);

  const pickMeta = (key: string) => {
    const row = metaTable.rows.find((r) => r[0]?.includes(key));
    return row?.[1];
  };

  const s1 = extractSection(body, "1\\. Required");
  const s2 = extractSection(body, "2\\. Validation");
  const s3 = extractSection(body, "3\\. Confirmation");
  const s4 = extractSection(body, "4\\. UNKNOWN");
  const s5 = extractSection(body, "5\\. Refusal");
  const s6 = extractSection(body, "6\\. API");
  const confirmProse = proseAfterTables(s3);

  const h1 = body.match(/^#\s+Skill[^\n]*/m)?.[0];
  const biz = body.match(/\*\*业务\*\*[：:]\s*([^\n]+)/)?.[1];

  return {
    title: h1 ? stripMd(h1) : undefined,
    businessLine: biz ? stripMd(biz) : undefined,
    skillId: pickMeta("skillId"),
    version: pickMeta("skillSpecVersion"),
    scenarioId: pickMeta("scenarioId"),
    status: pickMeta("状态"),
    requiredParams: firstTableInSection(s1),
    validations: firstTableInSection(s2),
    confirmation: firstTableInSection(s3),
    unknown: firstTableInSection(s4),
    refusals: firstTableInSection(s5),
    apiText: proseAfterTables(s6) || s6,
    confirmRules: parseConfirmRules(confirmProse),
    sectionNotes: {
      confirm: confirmProse.slice(0, 800),
    },
  };
}

export function operationBrief(view: SkillOperationView): string {
  const req = view.requiredParams.rows.filter((r) =>
    (r[1] ?? "").includes("✓"),
  ).length;
  const confirm = view.confirmation.rows.length;
  const parts: string[] = [];
  if (req) parts.push(`${req} 项必填`);
  if (confirm) parts.push(`确认卡 ${confirm} 字段`);
  if (view.version) parts.push(view.version);
  return parts.join(" · ") || "—";
}
