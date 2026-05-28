# frozen_string_literal: true

# 功能包流水线可跳过步骤（定稿时在 status.yaml → skips 声明）
module PipelineSkips
  module_function

  # 仅正向主路径步骤可声明跳过；返工任务（fix-*）不受 skips 影响
  SKIPPABLE = %w[
    frontend.integrate
    test.e2e
    designer.review
  ].freeze

  # 门禁：(phase, next) → 即将执行的正向 task_key
  GATE_TASK = {
    %w[backend_done test-agent] => "test.api",
    %w[tested frontend-agent] => "frontend.integrate",
    %w[frontend_done test-agent] => "test.e2e",
    %w[e2e_verified designer-agent] => "designer.review"
  }.freeze

  # 跳过若干步骤后落地的 (phase, next, owner)
  LAND_UI_REVIEWED = { phase: "ui_reviewed", next: "product-agent", owner: "product-agent" }.freeze

  def parse_skips(status)
    raw = status["skips"]
    return [] if raw.nil?

    list = case raw
           when Array then raw
           else []
           end
    list.map(&:to_s).select { |k| SKIPPABLE.include?(k) }.uniq
  end

  def pending_forward_task(phase, next_agent, has_blockers: false)
    return nil if has_blockers && phase == "frontend_done" && next_agent == "test-agent"

    GATE_TASK[[phase.to_s, next_agent.to_s]]
  end

  def skip_needed?(status, has_blockers: false)
    phase = status["phase"].to_s
    next_agent = status["next"].to_s
    skips = parse_skips(status)
    return nil if skips.empty?

    task = pending_forward_task(phase, next_agent, has_blockers: has_blockers)
    return nil if task.nil? || !skips.include?(task)

    target = resolve_skip_target(phase, next_agent, skips)
    return nil unless target

    { task: task, skips: skips, target: target }
  end

  def resolve_skip_target(phase, next_agent, skips)
    task = GATE_TASK[[phase.to_s, next_agent.to_s]]
    return nil unless task && skips.include?(task)

    case task
    when "frontend.integrate"
      # API-only：前端 + E2E + 设计一并跳过 → 产品验收门禁
      if (%w[frontend.integrate test.e2e designer.review] - skips).empty?
        LAND_UI_REVIEWED
      else
        nil # 仅跳过前端但保留 E2E/设计时无法自动跳，需指挥官调整 skips
      end
    when "test.e2e"
      if skips.include?("designer.review")
        LAND_UI_REVIEWED
      else
        { phase: "e2e_verified", next: "designer-agent", owner: "designer-agent" }
      end
    when "designer.review"
      LAND_UI_REVIEWED
    end
  end

  def infer_skips_from_coverage(coverage_path)
    return [] unless File.file?(coverage_path)

    text = File.read(coverage_path, encoding: "UTF-8")
    if text.match?(/含页面[^\n|]*\|\s*否/i) || text.match?(/含页面.*否/)
      %w[frontend.integrate test.e2e designer.review]
    else
      []
    end
  end

  def default_skips_for_api_only
    %w[frontend.integrate test.e2e designer.review]
  end
end
