import { describe, expect, it } from 'vitest'
import { applyImport, configFromDefaults, normalizeGame, sanitizeConfig, sessionDataFrom, toGamesFile, validateConfig } from './store'

const game = (name: string, extra: object = {}) => normalizeGame({ name, category: 'A', ...extra })
const base = {
  ...configFromDefaults({ cast: ['Ann', 'Bob', 'Cat'], games: [], prompts: ['p'] }),
  games: [game('G1'), game('G2', { host_include: ['Ann'] })],
}

describe('validateConfig', () => {
  it('accepts a sound config', () => {
    expect(validateConfig(base)).toEqual([])
  })

  it('flags duplicate names, unknown cast in rules and impossible hosts', () => {
    const cfg = { ...base, games: [game('G1'), game('G1'), game('G3', { exclude: ['Zed'] }), game('G4', { host_include: ['Ann'] })] }
    const errors = validateConfig({ ...cfg, disabledCast: ['Ann'] })
    expect(errors).toEqual(
      expect.arrayContaining([
        'Duplicate game name: G1',
        'Game "G3" refers to unknown cast member "Zed".',
        'Game "G4" has no possible host in the session cast.',
      ]),
    )
  })

  it('needs at least 2 cast members and 1 game in the session', () => {
    const errors = validateConfig({ ...base, disabledCast: ['Ann', 'Bob'], disabledGames: ['G1', 'G2'] })
    expect(errors).toEqual(expect.arrayContaining(['Select at least 2 cast members for the session.', 'Select at least 1 game for the session.']))
  })
})

describe('sessionDataFrom', () => {
  it('drops disabled cast and games', () => {
    const data = sessionDataFrom({ ...base, disabledCast: ['Bob'], disabledGames: ['G1'] })
    expect(data.cast).toEqual(['Ann', 'Cat'])
    expect(data.games.map((g) => g.name)).toEqual(['G2'])
  })
})

describe('import', () => {
  it('reads legacy games, cast and prompts files', () => {
    const games = JSON.stringify({ '2': { name: 'B', category: 'X' }, '1': { name: 'A', category: 'X', nbr_players: 2 } })
    const cfg = applyImport(base, [
      { name: 'ai2-games.json', text: games },
      { name: 'cast.txt', text: 'Zed\r\n\r\nYan\n' },
      { name: 'my-prompts.txt', text: 'one\ntwo' },
    ])
    expect(cfg.games.map((g) => g.name)).toEqual(['A', 'B'])
    expect(cfg.games[0].nbr_players).toBe(2)
    expect(cfg.cast).toEqual(['Zed', 'Yan'])
    expect(cfg.prompts).toEqual(['one', 'two'])
  })

  it('round-trips an exported bundle', () => {
    const cfg = applyImport(configFromDefaults({ cast: [], games: [], prompts: [] }), [{ name: 'x.json', text: JSON.stringify(base) }])
    expect(cfg).toEqual(base)
  })

  it('writes the Python games format and rejects junk', () => {
    expect(Object.keys(toGamesFile(base.games))).toEqual(['1', '2'])
    expect(sanitizeConfig('nope')).toBeNull()
  })
})
