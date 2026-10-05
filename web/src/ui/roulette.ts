export interface SpinStep {
  idx: number
  /** Offset from the start of the spin, in ms. */
  delayMs: number
}

export interface SpinOptions {
  count: number
  /** Bubble the ring currently rests on, or null before the first game. */
  from: number | null
  target: number
  /** Bubbles that are skipped (already played). The target is always visited. */
  skip: ReadonlySet<number>
  laps: number
  durationMs: number
}

/**
 * Clockwise visit order ending on `target`, timed so that the bubble moves fast at first
 * and slows down towards the end.
 */
export function buildSpinSchedule({ count, from, target, skip, laps, durationMs }: SpinOptions): SpinStep[] {
  const ring: number[] = []
  for (let i = 0; i < count; i++) if (i === target || !skip.has(i)) ring.push(i)

  const n = ring.length
  const targetPos = ring.indexOf(target)
  const startPos = ring.findIndex((i) => i > (from ?? -1)) // first eligible bubble after `from`
  const start = startPos === -1 ? 0 : startPos
  const total = laps * n + ((((targetPos - start) % n) + n) % n) + 1
  if (total <= 1) return [{ idx: target, delayMs: 0 }]

  return Array.from({ length: total }, (_, k) => {
    const u = k / (total - 1)
    return { idx: ring[(start + k) % n], delayMs: durationMs * (0.3 * u + 0.7 * u ** 3) }
  })
}
