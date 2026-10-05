import { shuffled } from '../engine/random'
import { SOUNDS } from '../engine/cues'

const MUTE_KEY = 'chris.muted'

/** Plays the app sounds; call from user gestures first so browsers allow playback. */
export class AudioManager {
  muted: boolean
  private cache = new Map<string, HTMLAudioElement>()
  private pool: string[] = []

  private urlFor: (file: string) => string

  constructor(urlFor: (file: string) => string) {
    this.urlFor = urlFor
    this.muted = localStorage.getItem(MUTE_KEY) === '1'
    const files = [SOUNDS.start, ...SOUNDS.next, SOUNDS.allPlayed, SOUNDS.lastMinute, SOUNDS.tick, SOUNDS.over]
    for (const f of files) {
      const a = new Audio(this.urlFor(f))
      a.preload = 'auto'
      this.cache.set(f, a)
    }
  }

  setMuted(muted: boolean): void {
    this.muted = muted
    localStorage.setItem(MUTE_KEY, muted ? '1' : '0')
  }

  play(file: string): void {
    const base = this.cache.get(file)
    if (this.muted || !base) return
    // A clone lets overlapping sounds (e.g. ticks) play independently.
    const a = base.cloneNode() as HTMLAudioElement
    a.play().catch(() => {}) // blocked until the first user gesture
  }

  /** Shuffled rotation through the game-next sounds, so none repeats until all were used. */
  playNext(): void {
    if (this.pool.length === 0) this.pool = shuffled(SOUNDS.next, Math.random)
    this.play(this.pool.pop()!)
  }
}
