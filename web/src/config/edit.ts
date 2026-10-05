import type { GameInfo } from '../engine/types'
import type { StoredConfig } from './store'

const mapRules = (g: GameInfo, f: (list: string[]) => string[]): GameInfo => ({
  ...g,
  exclude: f(g.exclude),
  host_include: f(g.host_include),
  host_exclude: f(g.host_exclude),
})

export function renameCast(cfg: StoredConfig, from: string, to: string): StoredConfig {
  const swap = (l: string[]) => l.map((n) => (n === from ? to : n))
  return {
    ...cfg,
    cast: swap(cfg.cast),
    disabledCast: swap(cfg.disabledCast),
    games: cfg.games.map((g) => mapRules(g, swap)),
  }
}

/** Also strips the member from every game's rules so no dangling names remain. */
export function removeCast(cfg: StoredConfig, name: string): StoredConfig {
  const drop = (l: string[]) => l.filter((n) => n !== name)
  return {
    ...cfg,
    cast: drop(cfg.cast),
    disabledCast: drop(cfg.disabledCast),
    games: cfg.games.map((g) => mapRules(g, drop)),
  }
}

/** Replaces game `oldName` (or appends when null); keeps its session on/off state under the new name. */
export function upsertGame(cfg: StoredConfig, oldName: string | null, game: GameInfo): StoredConfig {
  const games = oldName === null ? [...cfg.games, game] : cfg.games.map((g) => (g.name === oldName ? game : g))
  const disabledGames = cfg.disabledGames.map((n) => (n === oldName ? game.name : n))
  return { ...cfg, games, disabledGames }
}

export function removeGame(cfg: StoredConfig, name: string): StoredConfig {
  return {
    ...cfg,
    games: cfg.games.filter((g) => g.name !== name),
    disabledGames: cfg.disabledGames.filter((n) => n !== name),
  }
}

export function toggle(list: string[], name: string, on: boolean): string[] {
  const without = list.filter((n) => n !== name)
  return on ? [...without, name] : without
}
