import { useState } from 'react'
import { removeGame, toggle, upsertGame } from '../../config/edit'
import { normalizeGame } from '../../config/store'
import type { GameInfo } from '../../engine/types'
import type { TabProps } from './CastTab'

type RuleKey = 'exclude' | 'host_include' | 'host_exclude'

const RULES: { key: RuleKey; label: string }[] = [
  { key: 'exclude', label: 'Exclude from game' },
  { key: 'host_include', label: 'Only these can host' },
  { key: 'host_exclude', label: 'Cannot host' },
]

function GameForm({ cfg, original, onSave, onCancel }: { cfg: TabProps['cfg']; original: GameInfo | null; onSave: (g: GameInfo) => void; onCancel: () => void }) {
  const [g, setG] = useState<GameInfo>(original ?? normalizeGame({ name: '' }))
  const [error, setError] = useState('')
  const categories = [...new Set(cfg.games.map((x) => x.category))].sort()
  const set = (patch: Partial<GameInfo>) => setG({ ...g, ...patch })

  const save = () => {
    const game = normalizeGame(g)
    if (!game.name) return setError('Name is required.')
    if (cfg.games.some((x) => x.name === game.name && x.name !== original?.name)) return setError('A game with this name already exists.')
    onSave(game)
  }

  return (
    <div className="form">
      <label>
        Name <input value={g.name} onChange={(e) => set({ name: e.target.value })} />
      </label>
      <label>
        Players (0 = whole cast){' '}
        <input type="number" min={0} value={g.nbr_players} onChange={(e) => set({ nbr_players: Number(e.target.value) })} />
      </label>
      <label>
        Audience members <input type="number" min={0} value={g.nbr_audience} onChange={(e) => set({ nbr_audience: Number(e.target.value) })} />
      </label>
      <label>
        Category <input list="categories" value={g.category} onChange={(e) => set({ category: e.target.value })} />
        <datalist id="categories">
          {categories.map((c) => (
            <option key={c} value={c} />
          ))}
        </datalist>
      </label>
      <label>
        Fixed prompt (empty = random prompt)
        <textarea rows={3} value={g.prompt ?? ''} onChange={(e) => set({ prompt: e.target.value || null })} />
      </label>
      {RULES.map(({ key, label }) => (
        <fieldset key={key}>
          <legend>{label}</legend>
          {cfg.cast.map((n) => (
            <label key={n} className="check">
              <input type="checkbox" checked={g[key].includes(n)} onChange={(e) => set({ [key]: toggle(g[key], n, e.target.checked) })} />
              {n}
            </label>
          ))}
        </fieldset>
      ))}
      {error && <p className="error">{error}</p>}
      <div className="form-actions">
        <button onClick={save}>OK</button>
        <button onClick={onCancel}>Cancel</button>
      </div>
    </div>
  )
}

export function GamesTab({ cfg, update }: TabProps) {
  // `null` = closed, `{ name: null }` = adding a new game
  const [editing, setEditing] = useState<{ name: string | null } | null>(null)

  if (editing) {
    const original = cfg.games.find((g) => g.name === editing.name) ?? null
    return (
      <GameForm
        cfg={cfg}
        original={original}
        onCancel={() => setEditing(null)}
        onSave={(game) => {
          update(upsertGame(cfg, editing.name, game))
          setEditing(null)
        }}
      />
    )
  }

  return (
    <div>
      <p className="hint">Tick the games to include in this session.</p>
      <table className="games">
        <thead>
          <tr>
            <th />
            <th>Name</th>
            <th>Players</th>
            <th>Audience</th>
            <th>Category</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {cfg.games.map((g, i) => (
            <tr key={g.name + i}>
              <td>
                <input
                  type="checkbox"
                  checked={!cfg.disabledGames.includes(g.name)}
                  onChange={(e) => update({ ...cfg, disabledGames: toggle(cfg.disabledGames, g.name, !e.target.checked) })}
                />
              </td>
              <td>{g.name}</td>
              <td>{g.nbr_players}</td>
              <td>{g.nbr_audience}</td>
              <td>{g.category}</td>
              <td className="row-actions">
                <button onClick={() => setEditing({ name: g.name })}>Edit</button>
                <button onClick={() => window.confirm(`Remove "${g.name}"?`) && update(removeGame(cfg, g.name))}>Remove</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="add-row">
        <button onClick={() => setEditing({ name: null })}>Add game</button>
      </div>
    </div>
  )
}
