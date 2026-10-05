import { shuffled, weightedSampleWithoutReplacement } from './random'
import type { CastPick, Game, GamesFile, Player, Rng, SessionSettings } from './types'

export type ProbMethod = 'linear' | 'exponential'

/**
 * Pick probabilities from play/host counts: weights are exp-softmaxed over unmasked entries only
 * (faithful port of GameSession.compute_probs, including the softmax over raw weights).
 */
export function computeProbs(
  counts: readonly number[],
  mask: readonly boolean[],
  method: ProbMethod = 'linear',
  factor = 25,
  lambda = 0.5,
): number[] {
  const weights = counts.map((c) => (method === 'linear' ? factor / (c + 1) : Math.exp(-lambda * c)))
  const probs = weights.map(() => 0)
  const max = Math.max(...weights.filter((_, i) => mask[i]))
  const exps = weights.map((w, i) => (mask[i] ? Math.exp(w - max) : 0)) // shift by max for stability
  const sum = exps.reduce((s, e) => s + e, 0)
  if (sum > 0) exps.forEach((e, i) => (probs[i] = e / sum))
  return probs
}

export interface SessionData {
  games: Game[]
  cast: string[]
  prompts: string[]
}

/** Serializable session progress, used to survive a page reload. */
export interface SessionState {
  gameSequence: number[]
  counts: Record<string, { played: number; hosted: number }>
  sessionStarted: boolean
  sessionFinished: boolean
  startTime: number | null
  step: number | null
  nbrGamesPlayed: number | null
  currentGameIdx: number | null
  previousGameIdx: number | null
}

export interface SessionOptions {
  rng?: Rng
  now?: () => number // epoch ms
}

export function buildGames(file: GamesFile): Game[] {
  return Object.keys(file)
    .sort((a, b) => Number(a) - Number(b))
    .map((k) => ({
      ...file[k],
      prompt: file[k].prompt ?? null,
      exclude: file[k].exclude ?? [],
      host_include: file[k].host_include ?? [],
      host_exclude: file[k].host_exclude ?? [],
      status: 'unplayed' as const,
    }))
}

/** Parse a newline-separated text file; unlike the Python loader, blank lines are dropped. */
export function parseLines(text: string): string[] {
  return text
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter((l) => l.length > 0)
}

/** Game session logic: sequence, cast picking, timing. No UI concerns. */
export class GameSession {
  readonly games: Game[]
  readonly cast: Player[]
  readonly prompts: string[]
  readonly gameCategories: string[]
  readonly settings: SessionSettings
  gameSequence: number[] = []
  shuffledCategories: string[] = []

  sessionStarted = false
  sessionFinished = false
  startTime: number | null = null
  step: number | null = null
  nbrGamesPlayed: number | null = null
  currentGameIdx: number | null = null
  previousGameIdx: number | null = null

  private rng: Rng
  private now: () => number

  constructor(data: SessionData, settings: SessionSettings, opts: SessionOptions = {}) {
    this.rng = opts.rng ?? Math.random
    this.now = opts.now ?? Date.now
    this.settings = settings
    this.games = data.games.map((g) => ({ ...g }))
    this.prompts = data.prompts
    this.gameCategories = [...new Set(this.games.map((g) => g.category))].sort()

    const names = data.cast
    this.cast = names.map((name) => ({
      name,
      nbrGamesPlayed: 0,
      nbrGamesHosted: 0,
      gameExclusionList: this.games.filter((g) => g.exclude.includes(name)).map((g) => g.name),
    }))

    // Drop names that are not in the current cast from include/exclude lists
    for (const g of this.games) {
      g.host_include = g.host_include.filter((n) => names.includes(n))
      g.host_exclude = g.host_exclude.filter((n) => names.includes(n))
      g.exclude = g.exclude.filter((n) => names.includes(n))
    }

    this.createGameSequence()
  }

  get nbrGames(): number {
    return this.games.length
  }

  snapshot(): SessionState {
    return {
      gameSequence: [...this.gameSequence],
      counts: Object.fromEntries(this.cast.map((p) => [p.name, { played: p.nbrGamesPlayed, hosted: p.nbrGamesHosted }])),
      sessionStarted: this.sessionStarted,
      sessionFinished: this.sessionFinished,
      startTime: this.startTime,
      step: this.step,
      nbrGamesPlayed: this.nbrGamesPlayed,
      currentGameIdx: this.currentGameIdx,
      previousGameIdx: this.previousGameIdx,
    }
  }

  restore(state: SessionState): void {
    this.gameSequence = [...state.gameSequence]
    for (const p of this.cast) {
      p.nbrGamesPlayed = state.counts[p.name]?.played ?? 0
      p.nbrGamesHosted = state.counts[p.name]?.hosted ?? 0
    }
    this.sessionStarted = state.sessionStarted
    this.sessionFinished = state.sessionFinished
    this.startTime = state.startTime
    this.step = state.step
    this.nbrGamesPlayed = state.nbrGamesPlayed
    this.currentGameIdx = state.currentGameIdx
    this.previousGameIdx = state.previousGameIdx
  }

  get durationMs(): number {
    return this.settings.durationMinutes * 60_000
  }

  /** Remaining time in ms, never negative. */
  get timeLeftMs(): number {
    if (this.startTime === null) return this.durationMs
    return Math.max(this.startTime + this.durationMs - this.now(), 0)
  }

  /**
   * Round-robin over shuffled categories, so consecutive games differ in category
   * (until the larger categories run out). Priority category goes in third position.
   */
  createGameSequence(): void {
    const { setPriorityCategory, priorityCategory } = this.settings
    let cats = shuffled(this.gameCategories, this.rng)
    if (setPriorityCategory && cats.includes(priorityCategory)) {
      cats = cats.filter((c) => c !== priorityCategory)
      cats.splice(2, 0, priorityCategory)
    }
    this.shuffledCategories = cats

    const perCat = new Map<string, number[]>()
    for (const cat of cats) {
      const idxs = this.games.flatMap((g, i) => (g.category === cat ? [i] : []))
      perCat.set(cat, shuffled(idxs, this.rng))
    }

    const sequence: number[] = []
    while ([...perCat.values()].some((l) => l.length > 0)) {
      for (const cat of cats) {
        const list = perCat.get(cat)!
        if (list.length > 0) sequence.push(list.pop()!)
      }
    }
    this.gameSequence = sequence
  }

  /** Pick host then players for a game, updating hosting/playing counters. */
  pickCast(game: Game): CastPick {
    const names = this.cast.map((p) => p.name)

    const possibleHosts = game.host_include.length
      ? game.host_include
      : names.filter((n) => !game.host_exclude.includes(n))
    const hostMask = names.map((n) => possibleHosts.includes(n))
    const probsHosting = computeProbs(
      this.cast.map((p) => p.nbrGamesHosted),
      hostMask,
    )
    const [hostIdx] = weightedSampleWithoutReplacement(probsHosting, 1, this.rng)
    if (hostIdx === undefined) throw new Error(`No possible host for game "${game.name}"`)
    this.cast[hostIdx].nbrGamesHosted += 1

    const playMask = this.cast.map((p) => !p.gameExclusionList.includes(game.name))
    playMask[hostIdx] = false
    const probsPlaying = computeProbs(
      this.cast.map((p) => p.nbrGamesPlayed),
      playMask,
    )
    const available = playMask.filter(Boolean).length
    const size = game.nbr_players > 0 ? Math.min(game.nbr_players, available) : available
    const playerIdxs = weightedSampleWithoutReplacement(probsPlaying, size, this.rng)
    for (const i of playerIdxs) this.cast[i].nbrGamesPlayed += 1

    return { hostIdx, hostName: names[hostIdx], playerIdxs, playerNames: playerIdxs.map((i) => names[i]) }
  }

  pickPrompt(game: Game): string | null {
    if (game.prompt) return game.prompt
    if (this.prompts.length === 0) return null
    return this.prompts[Math.floor(this.rng() * this.prompts.length)]
  }

  /** Advance to the next game; sets `sessionFinished` once the sequence is exhausted. */
  pickNextGame(): void {
    if (!this.sessionStarted) {
      this.sessionStarted = true
      this.startTime = this.now()
    }
    if (this.gameSequence.length > 0) {
      this.step = (this.step ?? 0) + 1
      this.nbrGamesPlayed = this.nbrGamesPlayed === null ? 0 : this.nbrGamesPlayed + 1
      this.previousGameIdx = this.currentGameIdx
      this.currentGameIdx = this.gameSequence.shift()!
    } else {
      this.nbrGamesPlayed = (this.nbrGamesPlayed ?? 0) + 1
      this.previousGameIdx = this.currentGameIdx
      this.currentGameIdx = null
      this.sessionFinished = true
    }
  }
}
