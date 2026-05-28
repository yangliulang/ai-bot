#!/usr/bin/env ruby
# frozen_string_literal: true

# 检查当前 status 是否应跳过下一正向步骤（Hook / 指挥官自检）
# 用法: ruby scripts/lib/pipeline-skip-check.rb <status.yaml> [--json]
# 退出码: 0 = 需要 skip；1 = 不需要

require "yaml"
require "json"
require_relative "pipeline_skips"

path = ARGV.find { |a| !a.start_with?("--") }
abort "用法: pipeline-skip-check.rb <status.yaml> [--json]" unless path
json_out = ARGV.include?("--json")

status = YAML.load_file(path)
has_blockers = !status["blockers"].nil? && !status["blockers"].empty?

info = PipelineSkips.skip_needed?(status, has_blockers: has_blockers)

if json_out
  if info
    puts JSON.generate(
      should_skip: true,
      task: info[:task],
      feature: status["feature"],
      target_phase: info[:target][:phase],
      target_next: info[:target][:next],
      skips: info[:skips]
    )
    exit 0
  else
    puts JSON.generate(should_skip: false)
    exit 1
  end
end

if info
  t = info[:target]
  puts "应跳过 #{info[:task]} → phase: #{t[:phase]}, next: #{t[:next]}（skips: #{info[:skips].join(', ')})"
  exit 0
end

exit 1
