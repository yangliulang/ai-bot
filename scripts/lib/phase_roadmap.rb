# frozen_string_literal: true

# 解析 phase-N.md backlog 表、判断阶段是否可收束（roadmap done 或功能包 phase: done）
module PhaseRoadmap
  module_function

  def parse_phase_table(path)
    abort "找不到 phase 文件: #{path}" unless File.file?(path)

    rows = []
    in_table = false
    File.readlines(path, chomp: true, encoding: "UTF-8").each do |line|
      if line.start_with?("## 功能 backlog")
        in_table = false
        next
      end
      if line.include?("| 优先级 |") && line.include?("功能 ID")
        in_table = true
        next
      end
      next unless in_table
      break if line.strip.empty?
      next unless line.start_with?("|")
      next if line.match?(/^\|[\s\-:|]+\|$/)

      cols = line.split("|").map(&:strip).reject(&:empty?)
      next if cols.size < 4
      next if cols[0] == "优先级"

      rows << {
        priority: cols[0],
        feature_id: cols[1],
        title: cols[2],
        status: cols[3].to_s.strip,
        path: cols[4].to_s.strip,
        note: cols[5].to_s.strip
      }
    end
    rows
  end

  def feature_status_phase(root, feature_id)
    return nil if feature_id.nil? || feature_id.strip.empty?

    status_path = File.join(root, "handoff/features/#{feature_id}/status.yaml")
    return nil unless File.file?(status_path)

    File.readlines(status_path, chomp: true, encoding: "UTF-8").each do |line|
      next unless line.start_with?("phase:")

      return line.sub(/\Aphase:\s*/, "").strip
    end
    nil
  end

  def row_effectively_done?(root, row)
    return true if row[:status] == "done"

    feature_status_phase(root, row[:feature_id]) == "done"
  end

  def phase_close_readiness(root, active_phase)
    phase_path = File.join(root, "handoff/roadmap/phase-#{active_phase}.md")
    rows = parse_phase_table(phase_path)
    return { ready: false, reason: "empty", active_phase: active_phase, phase_path: phase_path, rows: [] } if rows.empty?

    pending = rows.reject { |r| row_effectively_done?(root, r) }
    {
      ready: pending.empty?,
      reason: pending.empty? ? "all_done" : "pending",
      active_phase: active_phase,
      phase_path: phase_path,
      rows: rows,
      pending: pending
    }
  end
end
