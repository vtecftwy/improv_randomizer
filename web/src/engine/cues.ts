export const SOUNDS = {
  start: 'game-start.mp3',
  next: ['game-next-0.mp3', 'game-next-1.mp3', 'game-next-2.mp3', 'game-next-3.mp3'],
  allPlayed: 'game-all-played.mp3',
  lastMinute: 'game-last-minute.mp3',
  tick: 'game-tick-sound.mp3',
  over: 'game-over.mp3',
}

export interface CueState {
  fiveMinPlayed: boolean
  overPlayed: boolean
}

/** Initial cue state for a session that may already be partly elapsed (e.g. after a reload). */
export const initialCueState = (timeLeftMs: number): CueState => ({
  fiveMinPlayed: timeLeftMs <= 5 * 60_000,
  overPlayed: timeLeftMs <= 0,
})

/**
 * Sounds due at this countdown tick (GameSpace.countdown): the 5-minute alarm once inside the
 * 4:30-5:00 window, a tick each second in the last minute, and game over once at zero.
 */
export function countdownCues(timeLeftMs: number, state: CueState): { sounds: string[]; state: CueState } {
  const sounds: string[] = []
  const next = { ...state }
  if (!next.fiveMinPlayed && timeLeftMs >= 270_000 && timeLeftMs <= 300_000) {
    sounds.push(SOUNDS.lastMinute)
    next.fiveMinPlayed = true
  }
  if (timeLeftMs > 0 && timeLeftMs <= 60_000) sounds.push(SOUNDS.tick)
  if (timeLeftMs <= 0 && !next.overPlayed) {
    sounds.push(SOUNDS.over)
    next.overPlayed = true
  }
  return { sounds, state: next }
}
