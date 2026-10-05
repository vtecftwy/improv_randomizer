import { describe, expect, it } from 'vitest'
import { seededRng } from './random'
import { buildGames, computeProbs, GameSession, parseLines } from './session'
import type { GamesFile, SessionSettings } from './types'

const g = (name: string, category: string, extra: object = {}) => ({
  name,
  nbr_players: 0,
  nbr_audience: 0,
  category,
  prompt: null,
  exclude: [],
  host_include: [],
  host_exclude: [],
  ...extra,
})

const gamesFile: GamesFile = {
  '1': g('A1', 'A'),
  '2': g('A2', 'A'),
  '3': g('B1', 'B'),
  '4': g('B2', 'B'),
  '5': g('C1', 'C'),
  '6': g('C2', 'C'),
  '7': g('P1', 'All Play'),
  '8': g('H1', 'B', { nbr_players: 2, host_include: ['Ann'], exclude: ['Bob'] }),
}
const cast = ['Ann', 'Bob', 'Cat', 'Dan', 'Eve']
const settings: SessionSettings = { durationMinutes: 45, setPriorityCategory: true, priorityCategory: 'All Play' }

const make = (seed: number, now = () => 0) =>
  new GameSession({ games: buildGames(gamesFile), cast, prompts: ['p1', 'p2'] }, settings, { rng: seededRng(seed), now })

describe('computeProbs', () => {
  it('sums to 1 over unmasked entries and is 0 elsewhere', () => {
    const p = computeProbs([0, 1, 2, 3], [true, true, false, true])
    expect(p[2]).toBe(0)
    expect(p.reduce((s, x) => s + x, 0)).toBeCloseTo(1)
  })
  it('favours members with lower counts', () => {
    const p = computeProbs([0, 5], [true, true])
    expect(p[0]).toBeGreaterThan(p[1])
  })
})

describe('parseLines', () => {
  it('trims and drops blank lines', () => {
    expect(parseLines('a \r\n\r\n b\n')).toEqual(['a', 'b'])
  })
})

describe('game sequence', () => {
  it('contains every game exactly once', () => {
    for (let seed = 0; seed < 50; seed++) {
      const s = make(seed)
      expect([...s.gameSequence].sort((a, b) => a - b)).toEqual(s.games.map((_, i) => i))
    }
  })
  it('puts the priority category in third position of the first round', () => {
    for (let seed = 0; seed < 50; seed++) {
      const s = make(seed)
      expect(s.games[s.gameSequence[2]].category).toBe('All Play')
    }
  })
  it('has no consecutive same-category games in the first round', () => {
    for (let seed = 0; seed < 50; seed++) {
      const s = make(seed)
      const cats = s.gameSequence.slice(0, 4).map((i) => s.games[i].category)
      expect(new Set(cats).size).toBe(cats.length)
    }
  })
})

describe('pickCast', () => {
  it('never lets the host play, and honours include/exclude rules', () => {
    for (let seed = 0; seed < 100; seed++) {
      const s = make(seed)
      const game = s.games.find((x) => x.name === 'H1')!
      const pick = s.pickCast(game)
      expect(pick.hostName).toBe('Ann')
      expect(pick.playerNames).not.toContain('Ann')
      expect(pick.playerNames).not.toContain('Bob')
      expect(pick.playerNames).toHaveLength(2)
    }
  })
  it('uses the whole cast minus host when nbr_players is 0', () => {
    const s = make(1)
    const pick = s.pickCast(s.games[0])
    expect(pick.playerNames).toHaveLength(cast.length - 1)
  })
  it('balances hosting over a session-sized number of games', () => {
    const s = make(7)
    for (let i = 0; i < 20; i++) s.pickCast(s.games[0])
    const hosted = s.cast.map((p) => p.nbrGamesHosted)
    expect(Math.max(...hosted) - Math.min(...hosted)).toBeLessThanOrEqual(2)
  })
})

describe('session flow', () => {
  it('starts the clock on first pick and finishes after the last game', () => {
    let t = 1000
    const s = make(3, () => t)
    expect(s.timeLeftMs).toBe(45 * 60_000)
    const total = s.nbrGames
    for (let i = 0; i < total; i++) {
      s.pickNextGame()
      expect(s.sessionFinished).toBe(false)
      expect(s.currentGameIdx).not.toBeNull()
    }
    expect(s.startTime).toBe(1000)
    t += 60_000
    expect(s.timeLeftMs).toBe(44 * 60_000)
    s.pickNextGame()
    expect(s.sessionFinished).toBe(true)
    expect(s.currentGameIdx).toBeNull()
    t += 100 * 60_000
    expect(s.timeLeftMs).toBe(0)
  })
})
