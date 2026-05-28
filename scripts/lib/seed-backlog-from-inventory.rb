#!/usr/bin/env ruby
# frozen_string_literal: true

# 从 inventory.md §4（PP:INVENTORY_S4 标记内表格）生成 backlog.yaml
# 用法: ruby scripts/lib/seed-backlog-from-inventory.rb

require "yaml"

ROOT = ENV.fetch("PIPELINE_PROJECT_ROOT") { File.expand_path("../..", __dir__) }
MANIFEST = File.join(ROOT, "pipeline.project.yaml")

abort "缺少 #{MANIFEST}" unless File.file?(MANIFEST)
manifest = YAML.load_file(MANIFEST)

mode = manifest.dig("project", "onboarding", "mode") || "brownfield"
unless %w[brownfield continuing].include?(mode)
  warn "提示: mode=#{mode}；seed-backlog 主要用于 brownfield 首次建队列"
end

inventory_rel = manifest.dig("product", "inventory") || "handoff/product/inventory.md"
backlog_rel = manifest.dig("product", "backlog") || "handoff/product/backlog.yaml"
inventory_path = File.join(ROOT, inventory_rel)
backlog_path = File.join(ROOT, backlog_rel)

abort "缺少 #{inventory_path}" unless File.file?(inventory_path)

text = File.read(inventory_path)
m = text.match(/<!-- PP:INVENTORY_S4:BEGIN -->(.*?)<!-- PP:INVENTORY_S4:END -->/m)
abort "inventory 缺少 PP:INVENTORY_S4 标记" unless m

items = []
in_table = false
m[1].each_line(chomp: true) do |line|
  line = line.strip
  if line.include?("| 优先级 |") && line.include?("能力名")
    in_table = true
    next
  end
  next unless in_table
  next if line.empty? || line.start_with?("|---")
  next unless line.start_with?("|")

  cols = line.split("|").map(&:strip).reject(&:empty?)
  next if cols.size < 5
  next if cols[0] == "优先级"

  fid = cols[4]
  slug = fid.to_s.include?("--") ? fid.split("--", 2).last : cols[1].downcase.gsub(/[^a-z0-9]+/, "-")

  items << {
    "slug" => slug,
    "feature_id" => fid.match?(/^\d{4}-\d{2}-\d{2}--/) ? fid : nil,
    "priority" => cols[0],
    "title" => cols[1],
    "value" => cols[2],
    "depends_on" => cols[3] == "无" || cols[3].empty? ? [] : cols[3].split(/[,，]/).map(&:strip),
    "status" => "queued",
    "phase" => nil
  }
end

abort "inventory §4 未解析到行" if items.empty?

backlog = { "version" => 1, "items" => items }
File.write(backlog_path, backlog.to_yaml)
puts "✓ 已写入 #{backlog_rel}（#{items.size} 项 queued）"
puts "  下一步: /pipeline-product-plan 或 ./scripts/advance-phase.sh（continuing 模式下切片 phase）"
