#!/usr/bin/env ruby
# frozen_string_literal: true

# 指定 phase 对齐前：快照当前 backlog、切换 active_phase、清除未交付 planned（soft reset）
# 用法:
#   ruby scripts/lib/phase-realign-prepare.rb --phase N [--dry-run] [--no-switch] [--no-reset] [--note "变更说明"]
#
# 产出: handoff/roadmap/.realign/phase-N-<timestamp>.md（Agent 读此 + PRD 重写 phase-N.md）

require "yaml"
require "fileutils"
require "date"
require "time"
require_relative "phase_roadmap"

ROOT = ENV.fetch("PIPELINE_PROJECT_ROOT") { File.expand_path("../..", __dir__) }
MANIFEST = File.join(ROOT, "pipeline.project.yaml")
DRY = ARGV.include?("--dry-run")
NO_SWITCH = ARGV.include?("--no-switch")
NO_RESET = ARGV.include?("--no-reset")

def load_manifest
  abort "缺少 #{MANIFEST}" unless File.file?(MANIFEST)
  YAML.load_file(MANIFEST)
end

def mget(m, path, default = nil)
  val = path.split(".").reduce(m) { |acc, k| acc.is_a?(Hash) ? acc[k] : nil }
  val.nil? || (val.respond_to?(:empty?) && val.empty?) ? default : val
end

def phase_arg
  idx = ARGV.index("--phase")
  abort "用法: phase-realign-prepare.rb --phase N [--dry-run] [--no-switch] [--no-reset] [--note \"...\"]" unless idx && ARGV[idx + 1]

  ARGV[idx + 1].to_i
end

def note_arg
  idx = ARGV.index("--note")
  return nil unless idx && ARGV[idx + 1]

  ARGV[idx + 1]
end

def categorize_row(root, row)
  fid = row[:feature_id]
  pkg_phase = PhaseRoadmap.feature_status_phase(root, fid)
  roadmap_status = row[:status].to_s.strip

  if PhaseRoadmap.row_effectively_done?(root, row)
    return :done
  end
  if pkg_phase && pkg_phase != "planned"
    return :in_progress
  end
  if %w[contract_ready in_dev].include?(roadmap_status)
    return :in_progress
  end

  :planned
end

manifest = load_manifest
target_phase = phase_arg
commander_note = note_arg
prev_active = mget(manifest, "roadmap.active_phase", 1).to_i
prd_rel = mget(manifest, "project.prd.primary", "PRD-simple.md")
inventory_rel = mget(manifest, "product.inventory", "handoff/product/inventory.md")
backlog_rel = mget(manifest, "product.backlog", "handoff/product/backlog.yaml")

phase_path = File.join(ROOT, "handoff/roadmap/phase-#{target_phase}.md")
abort "找不到 #{phase_path}" unless File.file?(phase_path)

phase_rows = PhaseRoadmap.parse_phase_table(phase_path)
abort "phase-#{target_phase} backlog 表为空" if phase_rows.empty?

buckets = { done: [], in_progress: [], planned: [] }
phase_rows.each do |row|
  buckets[categorize_row(ROOT, row)] << row
end

ts = Time.now.strftime("%Y%m%d-%H%M%S")
realign_dir = File.join(ROOT, "handoff/roadmap/.realign")
FileUtils.mkdir_p(realign_dir) unless DRY

snapshot_path = File.join(realign_dir, "phase-#{target_phase}-#{ts}.md")
latest_link = File.join(realign_dir, "phase-#{target_phase}-latest.md")

lines = []
lines << "# Phase #{target_phase} 对齐快照"
lines << ""
lines << "> 生成: #{Time.now.iso8601} · `./scripts/phase-realign-prepare.sh --phase #{target_phase}`"
lines << "> PRD: `#{prd_rel}` · inventory: `#{inventory_rel}` · backlog: `#{backlog_rel}`"
lines << ""
lines << "## 指挥官变更说明"
lines << ""
lines << (commander_note.to_s.strip.empty? ? "（请在 Chat 中说明产品文档 / roadmap 变更点）" : commander_note.to_s.strip)
lines << ""
lines << "## 状态摘要"
lines << ""
lines << "| 类别 | 数量 | 说明 |"
lines << "|------|------|------|"
lines << "| done | #{buckets[:done].size} | 已交付；若文档变更影响，应对齐任务**新增返工功能 ID**，勿改原行 done |"
lines << "| in_progress | #{buckets[:in_progress].size} | 开发/定稿中；对齐时默认保留，或指挥官指定 reopen |"
lines << "| planned | #{buckets[:planned].size} | 未交付；prepare 后 soft reset 会 demote 到 backlog queued |"
lines << ""
lines << "## done（保留对照，返工请新建 ID）"
lines << ""
lines << "| 功能 ID | 功能名 | 备注 |"
lines << "|---------|--------|------|"
if buckets[:done].empty?
  lines << "| — | — | — |"
else
  buckets[:done].each do |r|
    lines << "| #{r[:feature_id]} | #{r[:title]} | #{r[:note]} |"
  end
end
lines << ""
lines << "## in_progress（对齐时注意 blockers）"
lines << ""
lines << "| 功能 ID | roadmap 状态 | 包 phase | 备注 |"
lines << "|---------|--------------|----------|------|"
if buckets[:in_progress].empty?
  lines << "| — | — | — | — |"
else
  buckets[:in_progress].each do |r|
    pkg = PhaseRoadmap.feature_status_phase(ROOT, r[:feature_id]) || "—"
    lines << "| #{r[:feature_id]} | #{r[:status]} | #{pkg} | #{r[:note]} |"
  end
end
lines << ""
lines << "## planned（reset 后将 demote）"
lines << ""
lines << "| 功能 ID | 功能名 | 备注 |"
lines << "|---------|--------|------|"
if buckets[:planned].empty?
  lines << "| — | — | — |"
else
  buckets[:planned].each do |r|
    lines << "| #{r[:feature_id]} | #{r[:title]} | #{r[:note]} |"
  end
end
lines << ""
lines << "## Agent 对齐产出要求"
lines << ""
lines << "1. 重写 `handoff/roadmap/phase-#{target_phase}.md`：阶段目标、backlog 表、依赖、本阶段不做"
lines << "2. 新增 **`## 对齐说明`**：文档变更摘要、保留 / 返工 / 新增 / 推迟 对照表"
lines << "3. **返工**：文档变更影响已 done 能力时，**新建** `YYYY-MM-DD--slug`（可加 `-v2`），状态 `planned`，备注 `返工←原ID`；**勿**把原 done 行改回 planned"
lines << "4. 运行 `./scripts/sync-backlog-from-phase.sh --phase #{target_phase}`"
lines << "5. 对照 `handoff/pipeline/checklists/phase-realign.md`"
lines << ""

snapshot_text = lines.join("\n")

if DRY
  puts snapshot_text
  puts "---"
  puts "[dry-run] 将写入 #{snapshot_path}"
else
  File.write(snapshot_path, snapshot_text)
  File.write(latest_link, snapshot_text)
end

unless NO_SWITCH
  if DRY
    puts "[dry-run] manifest active_phase: #{prev_active} → #{target_phase}"
    puts "[dry-run] default_phase_file → handoff/roadmap/phase-#{target_phase}.md"
  else
    manifest["roadmap"] ||= {}
    manifest["roadmap"]["active_phase"] = target_phase
    manifest["roadmap"]["default_phase_file"] = "handoff/roadmap/phase-#{target_phase}.md"
    File.write(MANIFEST, manifest.to_yaml)
    puts "✓ active_phase → #{target_phase}（原 #{prev_active}）"
  end
end

unless NO_RESET
  if buckets[:in_progress].any? && !ARGV.include?("--force")
    warn "⚠ in_progress #{buckets[:in_progress].size} 项，跳过 plan-reset（仅快照；清除 planned 请加 --force）"
  else
    reset_cmd = ["ruby", File.join(ROOT, "scripts/lib/plan-reset.rb"), "--phase", target_phase.to_s]
    reset_cmd << "--dry-run" if DRY
    reset_cmd << "--force" if ARGV.include?("--force")
    puts "→ plan-reset (soft): #{reset_cmd.join(' ')}"
    abort "plan-reset 失败" unless system(*reset_cmd)
  end
end

puts "✓ 对齐快照: handoff/roadmap/.realign/phase-#{target_phase}-#{ts}.md"
puts "  最新: handoff/roadmap/.realign/phase-#{target_phase}-latest.md"
puts "  下一步: Agent 执行 product.phase-realign，对照 PRD 重写 phase-#{target_phase}.md"
