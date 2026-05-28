import { describe, expect, it } from 'vitest'

import {
  executionMatchesCorrelationKeyword,
  executionMatchesStatus,
  parseExecutionStatusFilter,
} from '@/entities/runtime/execution-filters'

describe('parseExecutionStatusFilter', () => {
  it('maps legal status', () => {
    expect(parseExecutionStatusFilter('running')).toBe('RUNNING')
  })
  it('falls back to all', () => {
    expect(parseExecutionStatusFilter('nope')).toBe('all')
  })
})

describe('executionMatchesCorrelationKeyword', () => {
  const row = {
    executionId: 'exec-aa11',
    scenarioId: 'trade.spot.limit_order',
    userIdMasked: 'u-10482',
  }
  it('matches executionId substring', () => {
    expect(executionMatchesCorrelationKeyword(row, 'aa11')).toBe(true)
  })
  it('empty passes', () => {
    expect(executionMatchesCorrelationKeyword(row, '  ')).toBe(true)
  })
})

describe('executionMatchesStatus', () => {
  it('all passes', () => {
    expect(executionMatchesStatus('all', 'FAILED')).toBe(true)
  })
})
