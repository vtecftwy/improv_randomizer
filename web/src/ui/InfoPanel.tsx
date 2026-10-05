import type { Game } from '../engine/types'
import type { GameView } from './useGameSession'

export function InfoPanel({ games, view }: { games: Game[]; view: GameView }) {
  const game = view.currentIdx === null ? null : games[view.currentIdx]
  return (
    <aside className="info">
      <div className="game-name">{game?.name ?? 'Game to play'}</div>
      <h2>Players:</h2>
      <p>
        {view.players}
        {view.audience > 0 && (
          <>
            <br />
            Audience members: {view.audience}
          </>
        )}
      </p>
      <h2>Host:</h2>
      <p>{view.host}</p>
      <h2>Prompt:</h2>
      <p>{view.prompt}</p>
    </aside>
  )
}
