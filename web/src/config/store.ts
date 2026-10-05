import { parseLines, type SessionData } from '../engine/session'
import type { Game, GameInfo, GamesFile } from '../engine/types'

/** Complete user configuration for one profile; replaces the bundled defaults when present. */
export interface StoredConfig {
  version: 1
  cast: string[]
  games: GameInfo[]
  prompts: string[]
  /** Items left out of the session; stored negatively so newly added items are enabled. */
  disabledCast: string[]
  disabledGames: string[]
}

const key = (profileKey: string) => `chris.config.v1:${profileKey}`

const strings = (v: unknown): string[] => (Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : [])
const count = (v: unknown): number => (typeof v === 'number' && Number.isFinite(v) && v >= 0 ? Math.floor(v) : 0)

export function normalizeGame(g: Partial<GameInfo>): GameInfo {
  return {
    name: String(g.name ?? '').trim(),
    nbr_players: count(g.nbr_players),
    nbr_audience: count(g.nbr_audience),
    category: String(g.category ?? '').trim(),
    prompt: g.prompt ? String(g.prompt) : null,
    exclude: strings(g.exclude),
    host_include: strings(g.host_include),
    host_exclude: strings(g.host_exclude),
    description: g.description ?? null,
    tips: g.tips ?? null,
    ...(g.uid ? { uid: g.uid } : {}),
  }
}

export function configFromDefaults(data: SessionData): StoredConfig {
  return {
    version: 1,
    cast: [...data.cast],
    games: data.games.map(normalizeGame),
    prompts: [...data.prompts],
    disabledCast: [],
    disabledGames: [],
  }
}

/** Only the enabled cast and games go into a session. */
export function sessionDataFrom(cfg: StoredConfig): SessionData {
  return {
    cast: cfg.cast.filter((n) => !cfg.disabledCast.includes(n)),
    games: cfg.games.filter((g) => !cfg.disabledGames.includes(g.name)).map((g): Game => ({ ...g, status: 'unplayed' })),
    prompts: cfg.prompts,
  }
}

/** Human-readable problems that would break or confuse a session. */
export function validateConfig(cfg: StoredConfig): string[] {
  const errors: string[] = []
  const names = new Set<string>()
  for (const g of cfg.games) {
    if (!g.name) errors.push('A game has no name.')
    else if (names.has(g.name)) errors.push(`Duplicate game name: ${g.name}`)
    names.add(g.name)
    for (const list of [g.exclude, g.host_include, g.host_exclude]) {
      for (const n of list) if (!cfg.cast.includes(n)) errors.push(`Game "${g.name}" refers to unknown cast member "${n}".`)
    }
  }
  if (new Set(cfg.cast).size !== cfg.cast.length) errors.push('Duplicate cast names.')
  const cast = cfg.cast.filter((n) => !cfg.disabledCast.includes(n))
  const games = cfg.games.filter((g) => !cfg.disabledGames.includes(g.name))
  if (cast.length < 2) errors.push('Select at least 2 cast members for the session.')
  if (games.length < 1) errors.push('Select at least 1 game for the session.')
  for (const g of games) {
    const hosts = g.host_include.length ? g.host_include : cast.filter((n) => !g.host_exclude.includes(n))
    if (!hosts.some((h) => cast.includes(h))) errors.push(`Game "${g.name}" has no possible host in the session cast.`)
  }
  return errors
}

export function sanitizeConfig(raw: unknown): StoredConfig | null {
  if (!raw || typeof raw !== 'object') return null
  const r = raw as Record<string, unknown>
  if (!Array.isArray(r.games)) return null
  return {
    version: 1,
    cast: strings(r.cast),
    games: r.games.map((g) => normalizeGame(g as Partial<GameInfo>)),
    prompts: strings(r.prompts),
    disabledCast: strings(r.disabledCast),
    disabledGames: strings(r.disabledGames),
  }
}

export function loadStored(profileKey: string): StoredConfig | null {
  try {
    return sanitizeConfig(JSON.parse(localStorage.getItem(key(profileKey)) ?? 'null'))
  } catch {
    return null
  }
}

export function saveStored(profileKey: string, cfg: StoredConfig): void {
  localStorage.setItem(key(profileKey), JSON.stringify(cfg))
}

export function clearStored(profileKey: string): void {
  localStorage.removeItem(key(profileKey))
}

/** Same format as the Python games JSON: string-keyed dict starting at "1". */
export function toGamesFile(games: GameInfo[]): GamesFile {
  return Object.fromEntries(games.map((g, i) => [String(i + 1), g]))
}

export function gamesFromFile(file: GamesFile): GameInfo[] {
  return Object.keys(file)
    .sort((a, b) => Number(a) - Number(b))
    .map((k) => normalizeGame(file[k]))
}

export interface ImportFile {
  name: string
  text: string
}

/**
 * Apply imported files on top of `base`. Accepts a full export bundle, or the legacy files:
 * a games JSON, a cast text file, and a prompts text file (name contains "prompt").
 */
export function applyImport(base: StoredConfig, files: ImportFile[]): StoredConfig {
  let cfg = { ...base }
  for (const f of files) {
    if (f.name.toLowerCase().endsWith('.json')) {
      const raw = JSON.parse(f.text) as Record<string, unknown>
      const bundle = sanitizeConfig(raw)
      if (bundle) cfg = bundle
      else cfg = { ...cfg, games: gamesFromFile(raw as unknown as GamesFile) }
    } else if (/prompt/i.test(f.name)) {
      cfg = { ...cfg, prompts: parseLines(f.text) }
    } else {
      cfg = { ...cfg, cast: parseLines(f.text) }
    }
  }
  return cfg
}
