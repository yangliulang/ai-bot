#!/usr/bin/env ruby
# frozen_string_literal: true

# 将功能包重置为 planned，供 phase 返工开发（指挥官显式指定原 ID 时）
# 用法: ruby scripts/lib/feature-reopen.rb --feature 2026-05-25--greeting [--phase N] [--dry-run]

require "yaml"
require "date"

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

idx = ARGV.index("--feature")
abort "用法: feature-reopen.rb --feature FID [--phase N] [--dry-run]" unless idx && ARGV[idx + 1]

fid = ARGV[idx + 1]
manifest = load_manifest
phase_num = mget(manifest, "roadmap.active_phase", 1).to_i
pidx = ARGV.index("--phase")
phase_num = ARGV[pidx + 1].to_i if pidx && ARGV[pidx + 1]

status_path = File.join(ROOT, "handoff/features/#{fid}/status.yaml")
abort "找不到功能包 #{status_path}" unless File.file?(status_path)

today = Date.today.iso8601
history_entry = "  - at: \"#{today}\"\n    phase: planned\n    owner: product-agent\n    note: feature-reopen 返工重置"

text = File.read(status_path, encoding: "UTF-8")
text = text.sub(/phase:\s*.+/, "phase: planned")
text = text.sub(/owner:\s*.+/, "owner: product-agent")
text = text.sub(/next:\s*.+/, "next: product-agent")

if text.match?(/^blockers:/)
  text = text.sub(/blockers:\s*.+/, "blockers: []")
end

if text.match?(/^history:/)
  text = text.sub(/^(history:\s*\n)/, "\\1#{history_entry}\n")
else
  text += "\nhistory:\n#{history_entry}\n"
end

if DRY
  puts "[dry-run] 将更新 #{status_path} → planned"
else
  File.write(status_path, text)
  puts "✓ #{fid} status.yaml → planned"
end

phase_path = File.join(ROOT, "handoff/roadmap/phase-#{phase_num}.md")
if File.file?(phase_path)
  updated = false
  new_lines = File.readlines(phase_path, chomp: false, encoding: "UTF-8").map do |line|
    next line unless line.start_with?("|") && line.include?(fid) && line.match?(/\|\s*done\s*\|/)

    updated = true
    line.sub(/\|\s*done\s*\|/, "| planned |")
  end
  if updated
    if DRY
      puts "[dry-run] roadmap phase-#{phase_num} 行 #{fid} → planned"
    else
      File.write(phase_path, new_lines.join)
      puts "✓ phase-#{phase_num}.md 行 #{fid} → planned"
    end
  end
end

puts "  下一步: /pipeline-product-contract #{fid}（更新 brief/OpenAPI 后定稿）"
