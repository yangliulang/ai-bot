#!/usr/bin/env ruby
# frozen_string_literal: true

# 按 status.yaml skips 跳过当前门禁，推进至下一适用 phase（不写各角色交付物）
# 用法: ruby scripts/lib/pipeline-skip-apply.rb <feature_dir_or_status.yaml> [--dry-run]

require "yaml"
require "time"
require_relative "pipeline_skips"

ROOT = ENV.fetch("PIPELINE_PROJECT_ROOT") { File.expand_path("../..", __dir__) }
DRY = ARGV.include?("--dry-run")
input = ARGV.find { |a| !a.start_with?("--") }
abort "用法: pipeline-skip-apply.rb handoff/features/<id>/ [--dry-run]" unless input

status_path = if input.end_with?("status.yaml")
                File.expand_path(input)
              elsif input.start_with?("/")
                File.join(input, "status.yaml")
              else
                File.join(ROOT, input, "status.yaml")
              end
abort "找不到 #{status_path}" unless File.file?(status_path)

status = YAML.load_file(status_path)
has_blockers = !status["blockers"].nil? && !status["blockers"].empty?
info = PipelineSkips.skip_needed?(status, has_blockers: has_blockers)
abort "当前门禁无需跳过（检查 skips 与 phase/next）" unless info

task = info[:task]
target = info[:target]
now = Time.now.iso8601
feature = status["feature"] || File.basename(File.dirname(status_path))

status["phase"] = target[:phase]
status["next"] = target[:next]
status["owner"] = target[:owner]
status["blockers"] = []
status["updated_at"] = now
status["history"] ||= []
status["history"] << {
  "at" => now,
  "phase" => target[:phase],
  "by" => "commander",
  "note" => "pipeline-skip: 跳过 #{task}（skips: #{info[:skips].join(', ')}）"
}

if DRY
  puts "[dry-run] 将写入 #{status_path}:"
  puts status.to_yaml
else
  File.write(status_path, status.to_yaml)
  puts "✓ #{feature} 已跳过 #{task} → phase: #{target[:phase]}, next: #{target[:next]}"
  puts "  下一步: /pipeline-product-accept #{feature}" if target[:phase] == "ui_reviewed"
end
