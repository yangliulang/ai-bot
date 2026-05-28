#!/usr/bin/env node
/**
 * 产品视角 · 需求与范围日报 → 飞书自定义机器人 Webhook
 * 对齐：specs/design/requirements-daily-report-feishu.md
 */

import crypto from 'node:crypto';
import { execFileSync, spawnSync } from 'node:child_process';
import https from 'node:https';
import { URL } from 'node:url';

const TZ = process.env.REPORT_TZ || 'Asia/Shanghai';
const INCLUDE_PRODUCT = !['0', 'false', 'no'].includes(
  String(process.env.INCLUDE_PRODUCT || 'true').toLowerCase(),
);
const TECH_APPENDIX = ['1', 'true', 'yes'].includes(
  String(process.env.INCLUDE_TECH_APPENDIX || '').toLowerCase(),
);
const DRY_RUN =
  ['1', 'true', 'yes'].includes(String(process.env.FEISHU_DRY_RUN || '').toLowerCase()) ||
  process.argv.includes('--dry-run');
const WEBHOOK = process.env.FEISHU_WEBHOOK_URL || '';
const SIGN_SECRET = process.env.FEISHU_WEBHOOK_SECRET || ''; // optional

const PATHS = ['specs/requirements/'];
if (INCLUDE_PRODUCT) PATHS.push('product/');

function todayInShanghai() {
  return new Date().toLocaleString('sv-SE', { timeZone: TZ }).slice(0, 10);
}

function addCalendarDays(yyyyMmDd, delta) {
  const [y, m, d] = yyyyMmDd.split('-').map(Number);
  const t = Date.UTC(y, m - 1, d) + delta * 864e5;
  return new Date(t).toISOString().slice(0, 10);
}

function reportDate() {
  const override = process.env.REPORT_DATE_OVERRIDE;
  if (override && /^\d{4}-\d{2}-\d{2}$/.test(override)) return override;
  return addCalendarDays(todayInShanghai(), -1);
}

function git(args) {
  const r = spawnSync('git', args, {
    encoding: 'utf8',
    maxBuffer: 20 * 1024 * 1024,
  });
  if (r.error) throw r.error;
  if (r.status !== 0) {
    throw new Error(`git ${args.join(' ')} failed: ${r.stderr || r.stdout}`);
  }
  return r.stdout;
}

/** @param {string} reportDay YYYY-MM-DD */
function gitLogRange(reportDay) {
  const since = `${reportDay} 00:00:00 +0800`;
  const until = `${reportDay} 23:59:59 +0800`;
  const pathArgs = ['--', ...PATHS];
  const fmt = '%H%x09%s';
  const out = git([
    'log',
    '--no-merges',
    '--since',
    since,
    '--until',
    until,
    `--pretty=format:${fmt}`,
    ...pathArgs,
  ]);
  const lines = out.split('\n').filter(Boolean);
  /** @type {Map<string, string>} */
  const byHash = new Map();
  for (const line of lines) {
    const tab = line.indexOf('\t');
    if (tab === -1) continue;
    const hash = line.slice(0, tab);
    const subj = line.slice(tab + 1).trim();
    if (!byHash.has(hash)) byHash.set(hash, subj);
  }
  return [...byHash.entries()].map(([hash, subject]) => ({ hash, subject }));
}

/** @param {string} reportDay */
function gitNameOnly(reportDay) {
  const since = `${reportDay} 00:00:00 +0800`;
  const until = `${reportDay} 23:59:59 +0800`;
  const pathArgs = ['--', ...PATHS];
  const out = git([
    'log',
    '--no-merges',
    '--since',
    since,
    '--until',
    until,
    '--name-only',
    '--pretty=format:',
    ...pathArgs,
  ]);
  return [...new Set(out.split('\n').map((s) => s.trim()).filter(Boolean))];
}

/** 将路径归并为产品可读「领域线索」（不逐文件铺陈） */
function bucketLabel(filePath) {
  if (filePath.startsWith('product/')) return '产品叙事（product）';
  const p = filePath.replace(/^specs\/requirements\//, '');
  if (p.startsWith('domains/')) return '域需求（domains）';
  if (p.startsWith('flows/')) return '主流程（flows）';
  if (p.startsWith('Runtime/')) return 'Runtime';
  if (p.startsWith('prompt-runtime/')) return 'PRS / Prompt 拼装';
  if (p.startsWith('skill-specs/')) return 'Skill 规格';
  if (p.startsWith('evals/')) return '评测（evals）';
  if (p.startsWith('integrations/')) return '外部集成';
  if (p.startsWith('standards/')) return '书写规范';
  if (p.startsWith('risk/')) return '风险横切';
  if (p.startsWith('observability/')) return '观测';
  if (p.startsWith('metrics/')) return '指标';
  if (p.startsWith('business/')) return '业务叙事';
  if (p.startsWith('admin-console/')) return '管理后台 IA';
  if (p.startsWith('market-narrative-runtime/')) return 'MNRA';
  if (p.startsWith('tools/')) return 'Tools';
  if (p.startsWith('prompts/')) return 'Prompts 库';
  return '需求索引 / 根目录文档';
}

function summarizeBuckets(files) {
  const counts = new Map();
  for (const f of files) {
    const b = bucketLabel(f);
    counts.set(b, (counts.get(b) || 0) + 1);
  }
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([label, n]) => `${label}（${n} 个文件触达）`);
}

function genFeishuSign(timestamp, secret) {
  const key = `${timestamp}\n${secret}`;
  return crypto.createHmac('sha256', key).update('').digest('base64');
}

function buildNoChangeMessage(reportDay) {
  return `【产品日报】${reportDay}（范围/需求侧）\n需求与范围文档侧无新增合并说明；用户侧无同步事项。`;
}

function repositoryUrlForFooter() {
  const explicit =
    process.env.PRODUCT_BRIEF_REPO_URL || process.env.REPOSITORY_URL || '';
  if (explicit) return explicit;
  if (process.env.GITHUB_REPOSITORY) {
    return `${process.env.GITHUB_SERVER_URL || 'https://github.com'}/${process.env.GITHUB_REPOSITORY}`;
  }
  return '';
}

/**
 * @param {string} reportDay
 * @param {{ hash: string, subject: string }[]} commits
 * @param {string[]} files
 */
function buildMessage(reportDay, commits, files) {
  if (commits.length === 0) return buildNoChangeMessage(reportDay);

  const repoUrl = repositoryUrlForFooter();

  const lines = [];
  lines.push(`【产品日报】${reportDay}（范围/需求侧）`);
  lines.push('');
  lines.push('1）今日结论（摘要线索）');
  lines.push(
    '以下为统计日内合入主干相关路径的提交说明，供 Owner 用业务语言概括为对外口径（非最终文案）：',
  );
  const maxSubj = 12;
  for (const { subject } of commits.slice(0, maxSubj)) {
    lines.push(`· ${subject}`);
  }
  if (commits.length > maxSubj) lines.push(`· …共 ${commits.length} 条提交，其余请见仓库`);
  lines.push('');
  lines.push('2）范围与优先级');
  lines.push('· 暂无自动结论，请 Owner 根据上述线索补充「新增/扩大」「收缩/冻结」。');
  lines.push('');
  lines.push('3）对用户或交付的影响');
  lines.push('· 暂无自动摘要；无补充可写「无用户侧可见变更说明」。');
  lines.push('');
  lines.push('4）里程碑与收口');
  lines.push('· 暂无自动摘要；与 contract-closure / 里程碑相关请 Owner 一句话说明。');
  lines.push('');
  lines.push('5）阻塞与待决策');
  lines.push('· 无（请 Owner 按需覆盖）');
  lines.push('');
  lines.push('6）涉及范围线索（按桶统计，非文件清单）');
  for (const row of summarizeBuckets(files)) lines.push(`· ${row}`);
  lines.push('');
  lines.push('延伸阅读');
  if (repoUrl) lines.push(`· 仓库：${repoUrl}`);
  else lines.push('· （可选：配置 PRODUCT_BRIEF_REPO_URL 生成链接）');

  if (TECH_APPENDIX && files.length) {
    lines.push('');
    lines.push('—— 技术附录（仅排障，非产品正文） ——');
    const cap = 40;
    for (const f of files.slice(0, cap)) lines.push(`· ${f}`);
    if (files.length > cap) lines.push(`· …共 ${files.length} 个文件`);
  }

  return lines.join('\n');
}

function postFeishu(text) {
  const timestamp = String(Math.floor(Date.now() / 1000));
  /** @type {Record<string, unknown>} */
  const body = {
    msg_type: 'text',
    content: { text },
  };
  if (SIGN_SECRET) {
    body.timestamp = timestamp;
    body.sign = genFeishuSign(timestamp, SIGN_SECRET);
  }

  const payload = JSON.stringify(body);
  const url = new URL(WEBHOOK);

  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        hostname: url.hostname,
        path: url.pathname + url.search,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(payload),
        },
      },
      (res) => {
        let raw = '';
        res.on('data', (c) => {
          raw += c;
        });
        res.on('end', () => {
          if (!res.statusCode || res.statusCode < 200 || res.statusCode >= 300) {
            reject(new Error(`HTTP ${res.statusCode}: ${raw}`));
            return;
          }
          try {
            const j = JSON.parse(raw);
            if (typeof j.StatusCode === 'number' && j.StatusCode !== 0) {
              reject(new Error(`Feishu StatusCode=${j.StatusCode}: ${raw}`));
              return;
            }
            if ('code' in j && j.code !== 0 && j.code !== undefined) {
              reject(new Error(`Feishu code=${j.code}: ${raw}`));
              return;
            }
          } catch {
            // 非 JSON 也认为成功（部分网关仅返回 OK）
          }
          resolve(raw);
        });
      },
    );
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

async function postWithRetry(text, attempts = 3) {
  let last;
  for (let i = 0; i < attempts; i++) {
    try {
      return await postFeishu(text);
    } catch (e) {
      last = e;
      await new Promise((r) => setTimeout(r, (1 << i) * 2000));
    }
  }
  throw last;
}

function main() {
  let head = '';
  try {
    head = execFileSync('git', ['rev-parse', '--short', 'HEAD'], { encoding: 'utf8' }).trim();
  } catch {
    head = '';
  }

  const reportDay = reportDate();
  const commits = gitLogRange(reportDay);
  const files = gitNameOnly(reportDay);
  const text = buildMessage(reportDay, commits, files);

  // eslint-disable-next-line no-console
  console.log(`--- 产品日报草稿 (${reportDay}, HEAD=${head || 'n/a'}) ---\n${text}\n--- end ---`);

  if (DRY_RUN) {
    // eslint-disable-next-line no-console
    console.log('FEISHU_DRY_RUN=1 或 --dry-run：跳过 Webhook');
    process.exit(0);
  }
  if (!WEBHOOK) {
    // eslint-disable-next-line no-console
    console.error('缺少 FEISHU_WEBHOOK_URL，退出码 2');
    process.exit(2);
  }

  postWithRetry(text)
    .then((res) => {
      // eslint-disable-next-line no-console
      console.log('Webhook 响应:', res);
      process.exit(0);
    })
    .catch((err) => {
      // eslint-disable-next-line no-console
      console.error(err);
      process.exit(1);
    });
}

main();
