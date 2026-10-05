import { useCallback, useEffect, useRef, useState } from 'react'
import type { Profile } from '../config/profiles'
import { countdownCues, initialCueState, SOUNDS } from '../engine/cues'
import { GameSession, type SessionData } from '../engine/session'
import type { AudioManager } from './audio'
import { clearSession, discardSession, fingerprintOf, loadSession, saveSession } from './persistence'
import { buildSpinSchedule } from './roulette'

export interface GameView {
  currentIdx: number | null
  /** Bubble lit by the roulette while it spins. */
  spinningIdx: number | null
  spinning: boolean
  playedIdxs: number[]
  host: string
  players: string
  audience: number
  prompt: string
  gamesPlayed: number
  started: boolean
  finished: boolean
  timeLeftMs: number
}

const emptyView = (durationMs: number): GameView => ({
  currentIdx: null,
  spinningIdx: null,
  spinning: false,
  playedIdxs: [],
  host: '',
  players: '',
  audience: 0,
  prompt: '',
  gamesPlayed: 0,
  started: false,
  finished: false,
  timeLeftMs: durationMs,
})

/** Builds the session, resuming a saved one for the same profile and config if it is still running. */
function createSession(data: SessionData, profile: Profile, profileKey: string) {
  const session = new GameSession(data, profile)
  const fingerprint = fingerprintOf(data.cast, data.games.map((g) => g.name))
  const saved = loadSession(profileKey, fingerprint)
  if (saved) {
    session.restore(saved.state)
    if (session.timeLeftMs > 0) {
      return { session, fingerprint, view: { ...saved.view, spinning: false, spinningIdx: null, timeLeftMs: session.timeLeftMs } }
    }
    clearSession()
    return { session: new GameSession(data, profile), fingerprint, view: emptyView(session.durationMs) }
  }
  return { session, fingerprint, view: emptyView(session.durationMs) }
}

/** Binds a GameSession to React state; mirrors GameSpace.click_next. */
export function useGameSession(data: SessionData, profile: Profile, profileKey: string, audio: AudioManager) {
  // The session is a mutable engine object, so it lives in a ref rather than state.
  const [init] = useState(() => createSession(data, profile, profileKey))
  const session = init.session
  const [view, setView] = useState<GameView>(init.view)
  // Session mutations must not run inside a state updater (StrictMode runs those twice).
  const viewRef = useRef(view)
  const timersRef = useRef<ReturnType<typeof setTimeout>[]>([])
  const cuesRef = useRef(initialCueState(init.view.timeLeftMs))

  const commit = useCallback(
    (v: GameView) => {
      viewRef.current = v
      setView(v)
      if (v.finished) clearSession()
      else if (v.started && !v.spinning) {
        saveSession({ profileKey, fingerprint: init.fingerprint, state: session.snapshot(), view: v })
      }
    },
    [session, profileKey, init.fingerprint],
  )

  useEffect(() => {
    const timers = timersRef.current
    return () => timers.forEach(clearTimeout)
  }, [])

  const timeUp = view.started && view.timeLeftMs <= 0

  useEffect(() => {
    if (!view.started || view.finished || timeUp) return
    const id = setInterval(() => {
      const left = session.timeLeftMs
      const cues = countdownCues(left, cuesRef.current)
      cuesRef.current = cues.state
      cues.sounds.forEach((s) => audio.play(s))
      commit({ ...viewRef.current, timeLeftMs: left })
      if (left <= 0) clearSession()
    }, 1000)
    return () => clearInterval(id)
  }, [view.started, view.finished, timeUp, session, audio, commit])

  const next = useCallback(() => {
    const v = viewRef.current
    if (v.finished || v.spinning) return
    const played = v.currentIdx === null ? v.playedIdxs : [...v.playedIdxs, v.currentIdx]

    // All games played: close the session
    if (session.sessionStarted && (session.step ?? 0) >= session.nbrGames) {
      session.sessionFinished = true
      audio.play(SOUNDS.allPlayed)
      commit({ ...v, currentIdx: null, playedIdxs: played, gamesPlayed: session.nbrGames, finished: true })
      return
    }

    if (session.sessionStarted) audio.playNext()
    else audio.play(SOUNDS.start)

    session.pickNextGame()
    const idx = session.currentGameIdx!
    const game = session.games[idx]
    const pick = session.pickCast(game)
    const revealed: GameView = {
      ...v,
      started: true,
      currentIdx: idx,
      spinningIdx: null,
      spinning: false,
      playedIdxs: played,
      host: pick.hostName,
      players: pick.playerNames.join(', '),
      audience: game.nbr_audience,
      prompt: session.pickPrompt(game) ?? '',
      gamesPlayed: session.nbrGamesPlayed ?? 0,
      timeLeftMs: session.timeLeftMs,
    }

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const steps = reduceMotion
      ? []
      : buildSpinSchedule({
          count: session.nbrGames,
          from: v.currentIdx,
          target: idx,
          skip: new Set(played),
          laps: profile.spinLaps ?? 3,
          durationMs: profile.spinDurationMs ?? 3000,
        })
    if (steps.length <= 1) {
      commit(revealed)
      return
    }

    // The result is already drawn; the spin only delays showing it.
    commit({
      ...v,
      started: true,
      currentIdx: null,
      spinningIdx: null,
      spinning: true,
      playedIdxs: played,
      host: '',
      players: '',
      audience: 0,
      prompt: '',
      timeLeftMs: session.timeLeftMs,
    })
    steps.forEach((step, i) => {
      const last = i === steps.length - 1
      timersRef.current.push(
        setTimeout(
          () =>
            commit(
              last
                ? { ...revealed, timeLeftMs: session.timeLeftMs }
                : { ...viewRef.current, spinningIdx: step.idx },
            ),
          step.delayMs,
        ),
      )
    })
  }, [session, commit, profile, audio])

  /** Discard the saved session and start over. */
  const reset = useCallback(() => {
    discardSession()
    window.location.reload()
  }, [])

  return { session, view, next, reset }
}
