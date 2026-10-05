import type { SessionState } from '../engine/session'
import type { GameView } from './useGameSession'

const KEY = 'chris.session.v1'

let discarded = false

export interface SavedSession {
  profileKey: string
  /** Detects a changed cast or game list, which would make the saved indices wrong. */
  fingerprint: string
  state: SessionState
  view: GameView
}

export const fingerprintOf = (cast: string[], gameNames: string[]) => `${cast.join('|')}#${gameNames.join('|')}`

export function saveSession(s: SavedSession): void {
  if (discarded) return
  try {
    localStorage.setItem(KEY, JSON.stringify(s))
  } catch {
    // Storage full or disabled: the session just won't survive a reload.
  }
}

export function loadSession(profileKey: string, fingerprint: string): SavedSession | null {
  try {
    const s = JSON.parse(localStorage.getItem(KEY) ?? 'null') as SavedSession | null
    if (!s || s.profileKey !== profileKey || s.fingerprint !== fingerprint) return null
    if (s.state.sessionFinished || s.view.finished) return null
    return s
  } catch {
    return null
  }
}

export function clearSession(): void {
  localStorage.removeItem(KEY)
}

/** Clears the saved session and stops timers from re-saving it before the page reloads. */
export function discardSession(): void {
  discarded = true
  clearSession()
}
