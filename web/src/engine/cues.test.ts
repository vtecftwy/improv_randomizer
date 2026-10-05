import { describe, expect, it } from 'vitest'
import { countdownCues, initialCueState, SOUNDS } from './cues'

const fresh = { fiveMinPlayed: false, overPlayed: false }

describe('countdownCues', () => {
  it('plays the 5-minute alarm once, inside the 4:30-5:00 window', () => {
    expect(countdownCues(400_000, fresh).sounds).toEqual([])
    const a = countdownCues(299_000, fresh)
    expect(a.sounds).toEqual([SOUNDS.lastMinute])
    expect(countdownCues(298_000, a.state).sounds).toEqual([])
  })

  it('ticks every second in the last minute', () => {
    expect(countdownCues(60_000, fresh).sounds).toEqual([SOUNDS.tick])
    expect(countdownCues(1_000, fresh).sounds).toEqual([SOUNDS.tick])
  })

  it('plays game over once at zero', () => {
    const a = countdownCues(0, fresh)
    expect(a.sounds).toEqual([SOUNDS.over])
    expect(countdownCues(0, a.state).sounds).toEqual([])
  })

  it('does not replay past cues after a reload', () => {
    expect(initialCueState(200_000)).toEqual({ fiveMinPlayed: true, overPlayed: false })
    expect(initialCueState(0).overPlayed).toBe(true)
  })
})
