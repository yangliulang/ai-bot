import { describe, expect, it } from 'vitest'

import { isNonEmptyString } from '@/shared/lib/strings'

describe('isNonEmptyString', () => {
  it('returns false for blank strings', () => {
    expect(isNonEmptyString('')).toBe(false)
    expect(isNonEmptyString('   ')).toBe(false)
  })

  it('returns true for trimmed content', () => {
    expect(isNonEmptyString('tg')).toBe(true)
  })
})
