import { describe, expect, it } from 'vitest'
import { removeCast, removeGame, renameCast, toggle, upsertGame } from './edit'
import { configFromDefaults, normalizeGame } from './store'

const cfg = {
  ...configFromDefaults({ cast: ['Ann', 'Bob'], games: [], prompts: [] }),
  games: [normalizeGame({ name: 'G1', exclude: ['Bob'], host_include: ['Ann', 'Bob'] })],
  disabledCast: ['Bob'],
  disabledGames: ['G1'],
}

describe('edit helpers', () => {
  it('renames a cast member everywhere', () => {
    const r = renameCast(cfg, 'Bob', 'Rob')
    expect(r.cast).toEqual(['Ann', 'Rob'])
    expect(r.disabledCast).toEqual(['Rob'])
    expect(r.games[0].exclude).toEqual(['Rob'])
    expect(r.games[0].host_include).toEqual(['Ann', 'Rob'])
  })

  it('removes a cast member from the rules too', () => {
    const r = removeCast(cfg, 'Bob')
    expect(r.cast).toEqual(['Ann'])
    expect(r.games[0].exclude).toEqual([])
    expect(r.games[0].host_include).toEqual(['Ann'])
  })

  it('keeps the session toggle when a game is renamed, and drops it when removed', () => {
    const r = upsertGame(cfg, 'G1', normalizeGame({ name: 'G9' }))
    expect(r.disabledGames).toEqual(['G9'])
    expect(removeGame(r, 'G9').disabledGames).toEqual([])
    expect(upsertGame(cfg, null, normalizeGame({ name: 'New' })).games).toHaveLength(2)
  })

  it('toggles list membership without duplicates', () => {
    expect(toggle(['a'], 'a', true)).toEqual(['a'])
    expect(toggle(['a'], 'a', false)).toEqual([])
  })
})
