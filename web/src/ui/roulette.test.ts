import { describe, expect, it } from 'vitest'
import { buildSpinSchedule } from './roulette'

const opts = { count: 8, from: null, target: 5, skip: new Set<number>(), laps: 3, durationMs: 3000 }

describe('buildSpinSchedule', () => {
  it('ends on the target after the requested laps', () => {
    const s = buildSpinSchedule(opts)
    expect(s.at(-1)!.idx).toBe(5)
    expect(s).toHaveLength(3 * 8 + 5 + 1)
    expect(s[0].idx).toBe(0)
  })

  it('goes clockwise and skips played bubbles', () => {
    const s = buildSpinSchedule({ ...opts, from: 2, target: 6, skip: new Set([0, 3, 4]), laps: 1 })
    const eligible = [1, 2, 5, 6, 7]
    expect(s.map((x) => x.idx).every((i) => eligible.includes(i))).toBe(true)
    expect(s[0].idx).toBe(5)
    expect(s.at(-1)!.idx).toBe(6)
  })

  it('slows down: intervals never shrink and the last step is at the duration', () => {
    const s = buildSpinSchedule(opts)
    const gaps = s.slice(1).map((x, i) => x.delayMs - s[i].delayMs)
    for (let i = 1; i < gaps.length; i++) expect(gaps[i]).toBeGreaterThanOrEqual(gaps[i - 1] - 1e-9)
    expect(s.at(-1)!.delayMs).toBeCloseTo(3000)
  })

  it('handles a single remaining bubble and a one-bubble ring', () => {
    expect(buildSpinSchedule({ ...opts, count: 1, target: 0, laps: 0 })).toEqual([{ idx: 0, delayMs: 0 }])
    const s = buildSpinSchedule({ ...opts, skip: new Set([0, 1, 2, 3, 4, 6, 7]) })
    expect(s.at(-1)!.idx).toBe(5)
  })
})
