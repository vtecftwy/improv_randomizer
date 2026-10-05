import { describe, expect, it } from 'vitest'
import { bubbleLayout } from './bubbleLayout'

describe('bubbleLayout', () => {
  it('puts the first bubble at 12 o\'clock and goes clockwise', () => {
    const [a, b, c, d] = bubbleLayout(4, 1000, 600, 960)
    expect(a.x).toBeCloseTo(500)
    expect(a.y).toBeCloseTo(300 - 280)
    expect(b.x).toBeCloseTo(500 + 280 * 1.5)
    expect(b.y).toBeCloseTo(300)
    expect(c.y).toBeCloseTo(300 + 280)
    expect(d.x).toBeCloseTo(500 - 280 * 1.5)
  })
})
