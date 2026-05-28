#!/usr/bin/env ruby
# frozen_string_literal: true

# 阶段收束：phase-N 全部 done → inventory §2 rollover → backlog 切片 → phase-(N+1)
# 用法: ruby scripts/lib/phase-advance.rb [--dry-run]

require "yaml"
require "fileutils"
require "date"
require_relative "phase_roadmap"

ROOT = ENV.fetch("PIPELINE_PROJECT_ROOT") { File.expand_path("../..", __dir__) }
MANIFEST = File.join(ROOT, "pipeline.project.yaml")
DRY = ARGV.include?("--dry-run")

def load_manifest
  abort "缺少 #{MANIFEST}" unless File.file?(MANIFEST)
  YAML.load_file(MANIFEST)
end

def save_manifest(data)
  return puts "[dry-run] 跳过写入 manifest" if DRY
  File.write(MANIFEST, data.to_yaml)
end

def mget(m, path, default = nil)
  val = path.split(".").reduce(m) { |acc, k| acc.is_a?(Hash) ? acc[k] : nil }
  val.nil? || (val.respond_to?(:empty?) && val.empty?) ? default : val
end

def priority_rank(p)
  { "P0" => 0, "P1" => 1, "P2" => 2, "P3" => 3 }[p.to_s.upcase] || 9
end

def parse_phase_table(path)
  PhaseRoadmap.parse_phase_table(path)
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

def write_phase_file(path, phase_num, items, prev_goal_hint)
  today = Date.today.iso8601
  lines = []
  lines << "# Phase #{phase_num} — 迭代 #{phase_num}"
  lines << ""
  lines << "> 由 `./scripts/advance-phase.sh` 自 backlog.yaml 切片生成；产品 Agent 可补充阶段目标。"
  lines << ""
  lines << "## 阶段目标"
  lines << ""
  lines << prev_goal_hint || "1. （请 product-agent 补充本阶段要证明什么）"
  lines << ""
  lines << "## 功能 backlog"
  lines << ""
  lines << "| 优先级 | 功能 ID | 功能名 | 状态 | 功能包路径 | 备注 |"
  lines << "|--------|---------|--------|------|------------|------|"
  items.each do |it|
    fid = it["feature_id"]
    feat_path = fid && !fid.empty? ? "handoff/features/#{fid}/" : "—"
    lines << "| #{it['priority']} | #{fid} | #{it['title']} | planned | #{feat_path} | 来自 backlog |"
  end
  lines << ""
  lines << "功能 ID 格式：`YYYY-MM-DD--kebab-slug`（双横线 `--`）。"
  lines << ""
  lines << "### 指挥官下一步"
  lines << ""
  first = items.find { |i| i["feature_id"] && !i["feature_id"].empty? }
  if first
    lines << "```text"
    lines << "/pipeline-product-contract #{first['feature_id']}"
    lines << "```"
  end
  lines << ""
  lines << "## 本阶段不做"
  lines << ""
  lines << "- （见 inventory §5）"
  lines << ""
  lines << "## 变更记录"
  lines << ""
  lines << "| 日期 | 变更 | 操作人 |"
  lines << "|------|------|--------|"
  lines << "| #{today} | advance-phase 创建 phase-#{phase_num} | phase-advance.rb |"
  lines << ""

  if DRY
    puts "[dry-run] 将写入 #{path}:\n#{lines.join("\n")[0, 500]}..."
  else
    File.write(path, lines.join("\n"))
  end
end

def ensure_feature_ids!(items)
  today = Date.today.iso8601
  items.each do |it|
    next if it["feature_id"] && !it["feature_id"].to_s.strip.empty?

    slug = it["slug"] || it["title"].to_s.downcase.gsub(/[^a-z0-9]+/, "-").gsub(/^-|-$/, "")
    it["feature_id"] = "#{today}--#{slug}"
  end
end

manifest = load_manifest
mode = mget(manifest, "project.onboarding.mode", "greenfield").to_s
inventory_rel = mget(manifest, "product.inventory", "handoff/product/inventory.md")
backlog_rel = mget(manifest, "product.backlog", "handoff/product/backlog.yaml")
roadmap_glob = mget(manifest, "roadmap.glob", "handoff/roadmap/phase-*.md")
active_phase = mget(manifest, "roadmap.active_phase", 1).to_i
capacity = mget(manifest, "roadmap.phase_capacity", 0).to_i

inventory_path = File.join(ROOT, inventory_rel)
backlog_path = File.join(ROOT, backlog_rel)
phase_path = File.join(ROOT, "handoff/roadmap/phase-#{active_phase}.md")

if mode == "greenfield"
  puts "模式 greenfield：首次 phase-close 将把本阶段 done 项写入 inventory/backlog，并切换为 continuing。"
end

phase_rows = parse_phase_table(phase_path)
abort "phase-#{active_phase} backlog 为空" if phase_rows.empty?

not_done = phase_rows.reject { |r| PhaseRoadmap.row_effectively_done?(ROOT, r) }
unless not_done.empty?
  abort "phase-#{active_phase} 尚有未 done 项: #{not_done.map { |r| r[:feature_id] }.join(', ')}"
end

# Load or init backlog
backlog = if File.file?(backlog_path)
            YAML.load_file(backlog_path) || {}
          else
            { "version" => 1, "items" => [] }
          end
backlog["items"] ||= []

# Mark phase items done in backlog; build s2 append list
s2_new = []
phase_rows.each do |row|
  fid = row[:feature_id]
  item = backlog["items"].find { |i| i["feature_id"] == fid || i["slug"] == fid.split("--", 2).last }
  if item
    item["status"] = "done"
    item["phase"] = active_phase
    item["feature_id"] = fid
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
  s2_new << { title: row[:title], feature_id: fid, phase: active_phase, note: row[:note] }
end

append_inventory_s2(inventory_path, s2_new) if File.file?(inventory_path)

# Next phase slice from queued
queued = backlog["items"].select { |i| i["status"] == "queued" }
queued.sort_by! { |i| [priority_rank(i["priority"]), backlog["items"].index(i)] }
queued = queued.first(capacity) if capacity.positive?

if queued.empty?
  puts "阶段 #{active_phase} 已收束；backlog 无 queued 项。请在 #{backlog_rel} 添加待办后重跑，或手动 product.plan。"
  manifest["project"] ||= {}
  manifest["project"]["onboarding"] ||= {}
  manifest["project"]["onboarding"]["mode"] = "continuing"
  save_manifest(manifest)
  File.write(backlog_path, backlog.to_yaml) unless DRY
  exit 0
end

ensure_feature_ids!(queued)
queued.each do |it|
  it["status"] = "in_phase"
  it["phase"] = active_phase + 1
end

next_phase = active_phase + 1
next_phase_path = File.join(ROOT, "handoff/roadmap/phase-#{next_phase}.md")

write_phase_file(next_phase_path, next_phase, queued, "1. 本阶段自 backlog.yaml 切片交付以下能力。")

# Update inventory §4
if File.file?(inventory_path)
  s4_rows = queued.map do |it|
    dep = it["depends_on"].nil? || it["depends_on"].empty? ? "无" : it["depends_on"].join(", ")
    [it["priority"], it["title"], it["value"], dep, it["feature_id"]]
  end
  replace_inventory_section(
    inventory_path,
    "S4",
    s4_rows,
    %w[优先级 能力名 一句话用户价值 依赖 建议功能 ID]
  )
end

File.write(backlog_path, backlog.to_yaml) unless DRY

manifest["roadmap"] ||= {}
manifest["roadmap"]["active_phase"] = next_phase
manifest["roadmap"]["default_phase_file"] = "handoff/roadmap/phase-#{next_phase}.md"
manifest["project"] ||= {}
manifest["project"]["onboarding"] ||= {}
manifest["project"]["onboarding"]["mode"] = "continuing"

save_manifest(manifest)

puts "✓ phase-#{active_phase} 已收束 → phase-#{next_phase}.md"
puts "  mode → continuing"
puts "  backlog: #{queued.size} 项进入本阶段"
puts "  下一步: /pipeline-product-plan 审 diff，或 /pipeline-product-contract #{queued.first['feature_id']}"
