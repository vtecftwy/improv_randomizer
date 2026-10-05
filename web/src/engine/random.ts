import type { Rng } from './types'

/** Seedable PRNG (mulberry32). */
export function seededRng(seed: number): Rng {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) >>> 0
    let t = a
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

/** Fisher-Yates shuffle returning a new array (equivalent of random.sample(x, len(x))). */
export function shuffled<T>(items: readonly T[], rng: Rng): T[] {
  const out = [...items]
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1))
    ;[out[i], out[j]] = [out[j], out[i]]
  }
  return out
}

/**
 * Draw `size` distinct indices with probabilities `probs`, without replacement
 * (equivalent of numpy.random.choice(..., replace=False, p=probs)). Result is sorted.
 */
export function weightedSampleWithoutReplacement(probs: readonly number[], size: number, rng: Rng): number[] {
  const weights = [...probs]
  const picked: number[] = []
  for (let n = 0; n < size; n++) {
    const total = weights.reduce((s, w) => s + w, 0)
    if (total <= 0) break
    let r = rng() * total
    let chosen = -1
    for (let i = 0; i < weights.length; i++) {
      if (weights[i] <= 0) continue
      chosen = i
      r -= weights[i]
      if (r < 0) break
    }
    picked.push(chosen)
    weights[chosen] = 0
  }
  return picked.sort((a, b) => a - b)
}
