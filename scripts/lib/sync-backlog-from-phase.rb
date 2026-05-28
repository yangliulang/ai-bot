#!/usr/bin/env ruby
# frozen_string_literal: true

# product.plan 后：将 roadmap/phase-N.md backlog 表 merge 进 backlog.yaml
# 用法: ruby scripts/lib/sync-backlog-from-phase.rb [--phase N] [--dry-run]
#
# 规则：
# - 不降级已有 done
# - phase 表非 done 行 → backlog in_phase + 当前 phase 号
# - phase 表 done 行 → backlog done（缺项则追加）
# - 原 in_phase 且 phase=N 但不在本次 phase 表 → 改回 queued
# - 其他 queued/deferred 不在 phase 表 → 不动

require "yaml"
require "set"
require_relative "phase_roadmap"

ROOT = ENV.fetch("PIPELINE_PROJECT_ROOT") { File.expand_path("../..", __dir__) }
MANIFEST = File.join(ROOT, "pipeline.project.yaml")
DRY = ARGV.include?("--dry-run")

def load_manifest
  abort "缺少 #{MANIFEST}" unless File.file?(MANIFEST)
  YAML.load_file(MANIFEST)
end

def mget(m, path, default = nil)
  val = path.split(".").reduce(m) { |acc, k| acc.is_a?(Hash) ? acc[k] : nil }
  val.nil? || (val.respond_to?(:empty?) && val.empty?) ? default : val
end

def slug_from_fid(fid)
  fid.to_s.include?("--") ? fid.split("--", 2).last : fid.to_s
end

def find_item(items, fid)
  slug = slug_from_fid(fid)
  items.find { |i| i["feature_id"] == fid || i["slug"] == slug }
end

manifest = load_manifest
active_phase = mget(manifest, "roadmap.active_phase", 1).to_i

phase_arg_idx = ARGV.index("--phase")
active_phase = ARGV[phase_arg_idx + 1].to_i if phase_arg_idx && ARGV[phase_arg_idx + 1]

backlog_rel = mget(manifest, "product.backlog", "handoff/product/backlog.yaml")
backlog_path = File.join(ROOT, backlog_rel)
phase_path = File.join(ROOT, "handoff/roadmap/phase-#{active_phase}.md")

phase_rows = PhaseRoadmap.parse_phase_table(phase_path)
abort "phase-#{active_phase} backlog 表为空，无法同步" if phase_rows.empty?

backlog = if File.file?(backlog_path)
            YAML.load_file(backlog_path) || { "version" => 1, "items" => [] }
          else
            { "version" => 1, "items" => [] }
          end
backlog["items"] ||= []

phase_fids = phase_rows.map { |r| r[:feature_id] }.compact.to_set
added = 0
updated = 0
demoted = 0

phase_rows.each do |row|
  fid = row[:feature_id]
  next if fid.nil? || fid.to_s.strip.empty?

  done = PhaseRoadmap.row_effectively_done?(ROOT, row)
  item = find_item(backlog["items"], fid)

  if item
    if item["status"] == "done"
      next
    end

    item["feature_id"] = fid
    item["slug"] ||= slug_from_fid(fid)
    item["priority"] = row[:priority]
    item["title"] = row[:title]
    item["value"] = row[:note] unless row[:note].to_s.empty?
    item["depends_on"] ||= []

    if done
      item["status"] = "done"
      item["phase"] ||= active_phase
    else
      item["status"] = "in_phase"
      item["phase"] = active_phase
    end
    updated += 1
  else
    backlog["items"] << {
      "slug" => slug_from_fid(fid),
      "feature_id" => fid,
      "priority" => row[:priority],
      "title" => row[:title],
      "value" => row[:note].to_s.empty? ? row[:title] : row[:note],
      "depends_on" => [],
      "status" => done ? "done" : "in_phase",
      "phase" => active_phase
    }
    added += 1
  end
end

backlog["items"].each do |item|
  next unless item["status"] == "in_phase"
  next unless item["phase"].to_i == active_phase

  fid = item["feature_id"]
  next if fid && phase_fids.include?(fid)

  item["status"] = "queued"
  item["phase"] = nil
  demoted += 1
end

if DRY
  puts "[dry-run] 将写入 #{backlog_rel}：新增 #{added}，更新 #{updated}，移出本阶段 #{demoted}"
  puts backlog.to_yaml
else
  File.write(backlog_path, backlog.to_yaml)
  puts "✓ 已从 phase-#{active_phase}.md 同步 #{backlog_rel}"
  puts "  新增 #{added}，更新 #{updated}，移出本阶段 #{demoted}（→ queued）"
  puts "  done 项未降级；未出现在 phase 表的 queued 项保持不变"
end
