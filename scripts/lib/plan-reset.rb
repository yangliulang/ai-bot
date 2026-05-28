#!/usr/bin/env ruby
# frozen_string_literal: true

# 清除当前阶段未交付的规划（planned 等），保留 done；或 full 模式整阶段清空后重新规划
# 用法:
#   ruby scripts/lib/plan-reset.rb [--dry-run] [--force] [--mode soft|full] [--phase N]
#
# soft（默认）: 从 phase-N.md 移除未 done 的 backlog 行 → backlog.yaml 改回 queued；保留 done 行
# full: 将 done 行追加 inventory §2，phase 重置为空白模板，本阶段 in_phase 全部 → queued

require "yaml"
require "fileutils"
require "date"
require_relative "phase_roadmap"

ROOT = ENV.fetch("PIPELINE_PROJECT_ROOT") { File.expand_path("../..", __dir__) }
MANIFEST = File.join(ROOT, "pipeline.project.yaml")
DRY = ARGV.include?("--dry-run")
FORCE = ARGV.include?("--force")

def load_manifest
  abort "缺少 #{MANIFEST}" unless File.file?(MANIFEST)
  YAML.load_file(MANIFEST)
end

def mget(m, path, default = nil)
  val = path.split(".").reduce(m) { |acc, k| acc.is_a?(Hash) ? acc[k] : nil }
  val.nil? || (val.respond_to?(:empty?) && val.empty?) ? default : val
end

def mode_arg
  idx = ARGV.index("--mode")
  return "soft" unless idx && ARGV[idx + 1]

  m = ARGV[idx + 1].to_s
  abort "未知 --mode #{m}（soft|full）" unless %w[soft full].include?(m)

  m
end

def replace_inventory_section(inventory_path, marker, row_arrays, header_cols)
  text = File.read(inventory_path, encoding: "UTF-8")
  re = /<!-- PP:INVENTORY_#{marker}:BEGIN -->.*?<!-- PP:INVENTORY_#{marker}:END -->/m
  table = [
    "| #{header_cols.join(' | ')} |",
    "| #{header_cols.map { '---' }.join(' | ')} |"
  ]
  row_arrays.each { |r| table << "| #{r.join(' | ')} |" }
  block = "<!-- PP:INVENTORY_#{marker}:BEGIN -->\n\n#{table.join("\n")}\n\n<!-- PP:INVENTORY_#{marker}:END -->"
  if text.match?(re)
    text = text.sub(re, block)
  else
    warn "警告: inventory 缺少 PP:INVENTORY_#{marker} 标记，跳过该节"
    return
  end
  File.write(inventory_path, text) unless DRY
end

def append_inventory_s2(inventory_path, new_rows)
  return if new_rows.empty?

  text = File.read(inventory_path, encoding: "UTF-8")
  marker = "<!-- PP:INVENTORY_S2:END -->"
  unless text.include?(marker)
    warn "警告: inventory 缺少 PP:INVENTORY_S2 标记"
    return
  end

  lines = new_rows.map do |r|
    "| #{r[:title]} | #{r[:feature_id]} | phase #{r[:phase]} done | #{r[:note]}"
  end
  insertion = lines.join("\n") + "\n"
  text = text.sub(marker, "#{insertion}#{marker}")
  File.write(inventory_path, text) unless DRY
end

def package_phase(root, feature_id)
  PhaseRoadmap.feature_status_phase(root, feature_id)
end

def row_blocked?(root, row)
  return false if PhaseRoadmap.row_effectively_done?(root, row)

  pkg = package_phase(root, row[:feature_id])
  return true if pkg && pkg != "planned"

  %w[contract_ready in_dev].include?(row[:status].to_s.strip)
end

def archive_phase_file(phase_path, active_phase)
  archive_dir = File.join(File.dirname(phase_path), ".archive")
  FileUtils.mkdir_p(archive_dir) unless DRY
  ts = Time.now.strftime("%Y%m%d-%H%M%S")
  dest = File.join(archive_dir, "phase-#{active_phase}-#{ts}.md")
  if DRY
    puts "[dry-run] 归档 #{phase_path} → #{dest}"
  else
    FileUtils.cp(phase_path, dest)
    puts "✓ 已归档 #{File.basename(phase_path)} → handoff/roadmap/.archive/#{File.basename(dest)}"
  end
  dest
end

def write_reset_phase_file(path, phase_num, kept_rows, mode)
  today = Date.today.iso8601
  lines = []
  lines << "# Phase #{phase_num} — 迭代 #{phase_num}"
  lines << ""
  if mode == "full"
    lines << "> 由 `./scripts/plan-reset.sh --mode full` 重置；请 `/pipeline-product-plan` 重新规划。"
  else
    lines << "> 由 `./scripts/plan-reset.sh` 清除未交付项；done 行已保留。请 `/pipeline-product-plan` 补充本阶段规划。"
  end
  lines << ""
  lines << "## 阶段目标"
  lines << ""
  lines << "<!-- 请 product-agent 在 plan 时填写本阶段要证明什么 -->"
  lines << ""
  lines << "## 功能 backlog"
  lines << ""
  lines << "| 优先级 | 功能 ID | 功能名 | 状态 | 功能包路径 | 备注 |"
  lines << "|--------|---------|--------|------|------------|------|"
  kept_rows.each do |row|
    fid = row[:feature_id]
    feat_path = fid && !fid.to_s.empty? ? "handoff/features/#{fid}/" : "—"
    status = PhaseRoadmap.row_effectively_done?(ROOT, row) ? "done" : row[:status]
    lines << "| #{row[:priority]} | #{fid} | #{row[:title]} | #{status} | #{feat_path} | #{row[:note]} |"
  end
  lines << ""
  lines << "功能 ID 格式：`YYYY-MM-DD--kebab-slug`（双横线 `--`）。"
  lines << ""
  lines << "### 指挥官下一步"
  lines << ""
  lines << "```text"
  lines << "/pipeline-product-plan"
  lines << "```"
  lines << ""
  lines << "## 依赖与顺序"
  lines << ""
  lines << "<!-- plan 时补充 -->"
  lines << ""
  lines << "## 本阶段不做"
  lines << ""
  lines << "- （见 inventory §5）"
  lines << ""
  lines << "## 变更记录"
  lines << ""
  lines << "| 日期 | 变更 | 操作人 |"
  lines << "|------|------|--------|"
  lines << "| #{today} | plan-reset --mode #{mode} | plan-reset.rb |"
  lines << ""

  if DRY
    puts "[dry-run] 将写入 #{path}（保留 #{kept_rows.size} 行）"
  else
    File.write(path, lines.join("\n"))
  end
end

def demote_backlog_items!(backlog, feature_ids, active_phase)
  feature_ids.each do |fid|
    item = backlog["items"].find { |i| i["feature_id"] == fid }
    next unless item
    next if item["status"] == "done"

    item["status"] = "queued"
    item["phase"] = nil
  end

  backlog["items"].each do |item|
    next unless item["status"] == "in_phase"
    next unless item["phase"].to_i == active_phase

    fid = item["feature_id"]
    next if feature_ids.include?(fid)

    item["status"] = "queued"
    item["phase"] = nil
  end
end

manifest = load_manifest
reset_mode = mode_arg
active_phase = mget(manifest, "roadmap.active_phase", 1).to_i
phase_arg_idx = ARGV.index("--phase")
active_phase = ARGV[phase_arg_idx + 1].to_i if phase_arg_idx && ARGV[phase_arg_idx + 1]

inventory_rel = mget(manifest, "product.inventory", "handoff/product/inventory.md")
backlog_rel = mget(manifest, "product.backlog", "handoff/product/backlog.yaml")
phase_path = File.join(ROOT, "handoff/roadmap/phase-#{active_phase}.md")
inventory_path = File.join(ROOT, inventory_rel)
backlog_path = File.join(ROOT, backlog_rel)

abort "找不到 #{phase_path}" unless File.file?(phase_path)

phase_rows = PhaseRoadmap.parse_phase_table(phase_path)
abort "phase-#{active_phase} backlog 表为空，无需 reset" if phase_rows.empty?

blocked = phase_rows.select { |r| row_blocked?(ROOT, r) }
unless blocked.empty? || FORCE
  ids = blocked.map { |r| "#{r[:feature_id]}(pkg=#{package_phase(ROOT, r[:feature_id]) || '—'}, roadmap=#{r[:status]})" }
  abort "以下项已在开发/定稿中，无法清除规划（加 --force 强制 demote）：\n  #{ids.join("\n  ")}"
end

done_rows = phase_rows.select { |r| PhaseRoadmap.row_effectively_done?(ROOT, r) }
removable = phase_rows.reject { |r| PhaseRoadmap.row_effectively_done?(ROOT, r) }
removed_fids = removable.map { |r| r[:feature_id] }.compact

puts "mode=#{reset_mode} phase=#{active_phase} 保留 done=#{done_rows.size} 移除=#{removable.size}"

archive_phase_file(phase_path, active_phase)

backlog = if File.file?(backlog_path)
            YAML.load_file(backlog_path) || { "version" => 1, "items" => [] }
          else
            { "version" => 1, "items" => [] }
          end
backlog["items"] ||= []

if reset_mode == "full"
  s2_new = done_rows.map do |r|
    { title: r[:title], feature_id: r[:feature_id], phase: active_phase, note: r[:note] }
  end
  append_inventory_s2(inventory_path, s2_new) if File.file?(inventory_path) && !s2_new.empty?

  done_rows.each do |row|
    fid = row[:feature_id]
    item = backlog["items"].find { |i| i["feature_id"] == fid }
    if item
      item["status"] = "done"
      item["phase"] = active_phase
    else
      backlog["items"] << {
        "slug" => fid.split("--", 2).last,
        "feature_id" => fid,
        "priority" => row[:priority],
        "title" => row[:title],
        "value" => row[:note],
        "depends_on" => [],
        "status" => "done",
        "phase" => active_phase
      }
    end
  end

  demote_fids = phase_rows.map { |r| r[:feature_id] }.compact
  demote_backlog_items!(backlog, demote_fids, active_phase)
  kept = []
else
  demote_backlog_items!(backlog, removed_fids, active_phase)
  kept = done_rows
end

write_reset_phase_file(phase_path, active_phase, kept, reset_mode)

if File.file?(inventory_path)
  replace_inventory_section(
    inventory_path,
    "S4",
    [],
    %w[优先级 能力名 一句话用户价值 依赖 建议功能 ID]
  )
end

unless DRY
  File.write(backlog_path, backlog.to_yaml)
else
  puts "[dry-run] backlog 变更摘要：移除 #{removed_fids.size} 项 → queued"
  puts backlog.to_yaml if reset_mode == "soft" && !removed_fids.empty?
end

puts "✓ plan-reset 完成（mode=#{reset_mode}）"
if reset_mode == "soft" && !removed_fids.empty?
  puts "  已 demote: #{removed_fids.join(', ')}"
end
puts "  下一步: /pipeline-product-plan（附 PRD 或 roadmap 变更说明）"
puts "  plan 完成后: ./scripts/sync-backlog-from-phase.sh"
