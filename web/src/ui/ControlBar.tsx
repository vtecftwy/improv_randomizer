import { formatTime } from './formatTime'
import type { GameView } from './useGameSession'

interface Props {
  view: GameView
  muted: boolean
  onNext: () => void
  onConfig: () => void
  onToggleMute: () => void
  onReset: () => void
}

export function ControlBar({ view, muted, onNext, onConfig, onToggleMute, onReset }: Props) {
  const timeUp = view.started && view.timeLeftMs <= 0
  const label = timeUp ? 'GAME OVER!' : view.finished ? 'Done !' : view.started ? 'NEXT' : 'START'
  const warn = view.started && view.timeLeftMs <= 5 * 60_000

  return (
    <footer className="footer">
      <div className="footer-buttons">
        <button className="btn small" onClick={onConfig} tabIndex={-1}>
          Config
        </button>
        <button className="btn small" onClick={onToggleMute} tabIndex={-1}>
          Sound: {muted ? 'off' : 'on'}
        </button>
        {view.started && (
          <button
            className="btn small"
            tabIndex={-1}
            onClick={() => window.confirm('Discard the current session and start over?') && onReset()}
          >
            New
          </button>
        )}
      </div>
      <div>Number Games Played: {view.gamesPlayed}</div>
      <div className={`time${warn ? ' warn' : ''}`}>Time Left: {formatTime(view.timeLeftMs)}</div>
      <button className="btn main-btn" onClick={onNext} disabled={timeUp || view.finished || view.spinning} autoFocus>
        {label}
      </button>
    </footer>
  )
}
