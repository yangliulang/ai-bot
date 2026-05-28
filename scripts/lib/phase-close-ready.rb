#!/usr/bin/env ruby
# frozen_string_literal: true

# 判断当前 active_phase 是否全部 done（可执行 phase-close）
# 用法: ruby scripts/lib/phase-close-ready.rb [--json]
# 退出码: 0 = 可收束；1 = 尚有未完成项或 phase 为空

require "yaml"
require "json"
require_relative "phase_roadmap"

ROOT = ENV.fetch("PIPELINE_PROJECT_ROOT") { File.expand_path("../..", __dir__) }
MANIFEST = File.join(ROOT, "pipeline.project.yaml")
JSON_OUT = ARGV.include?("--json")

def load_active_phase
  abort "缺少 #{MANIFEST}" unless File.file?(MANIFEST)
  m = YAML.load_file(MANIFEST)
  m.dig("roadmap", "active_phase") || 1
end

active_phase = load_active_phase.to_i
result = PhaseRoadmap.phase_close_readiness(ROOT, active_phase)

if JSON_OUT
  puts JSON.generate(
    ready: result[:ready],
    active_phase: result[:active_phase],
    pending_ids: (result[:pending] || []).map { |r| r[:feature_id] }
  )
  exit(result[:ready] ? 0 : 1)
end

if result[:ready]
  puts "phase-#{active_phase} 全部 done，可执行 /pipeline-product-phase-close"
  exit 0
end

case result[:reason]
when "empty"
  warn "phase-#{active_phase} backlog 为空"
when "pending"
  ids = result[:pending].map { |r| r[:feature_id] }.join(", ")
  warn "phase-#{active_phase} 尚有未完成项: #{ids}"
end
exit 1
