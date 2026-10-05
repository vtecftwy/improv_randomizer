/** Game definition, as stored in the games JSON files. */
export interface GameInfo {
  name: string
  nbr_players: number // 0 = whole cast
  nbr_audience: number
  category: string
  prompt: string | null // null = random prompt from the prompt list
  exclude: string[]
  host_include: string[]
  host_exclude: string[]
  description?: string | null
  tips?: string | null
  uid?: string
}

/** Games JSON file: string-keyed dict of games. */
export type GamesFile = Record<string, GameInfo>

export type GameStatus = 'unplayed' | 'playing' | 'played'

export interface Game extends GameInfo {
  status: GameStatus
}

export interface Player {
  name: string
  nbrGamesPlayed: number
  nbrGamesHosted: number
  gameExclusionList: string[]
}

export interface SessionSettings {
  durationMinutes: number
  setPriorityCategory: boolean
  priorityCategory: string
}

export interface CastPick {
  hostIdx: number
  hostName: string
  playerIdxs: number[]
  playerNames: string[]
}

/** Returns a float in [0, 1). Injected so tests can be deterministic. */
export type Rng = () => number
