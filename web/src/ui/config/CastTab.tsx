import { useState } from 'react'
import { removeCast, renameCast, toggle } from '../../config/edit'
import type { StoredConfig } from '../../config/store'

export interface TabProps {
  cfg: StoredConfig
  update: (cfg: StoredConfig) => void
}

export function CastTab({ cfg, update }: TabProps) {
  const [name, setName] = useState('')
  const add = () => {
    const n = name.trim()
    if (n && !cfg.cast.includes(n)) update({ ...cfg, cast: [...cfg.cast, n] })
    setName('')
  }

  return (
    <div>
      <p className="hint">Tick the cast members who are present in this session.</p>
      <ul className="rows">
        {cfg.cast.map((n) => (
          <li key={n}>
            <label>
              <input
                type="checkbox"
                checked={!cfg.disabledCast.includes(n)}
                onChange={(e) => update({ ...cfg, disabledCast: toggle(cfg.disabledCast, n, !e.target.checked) })}
              />
              {n}
            </label>
            <span className="row-actions">
              <button
                onClick={() => {
                  const to = window.prompt('New name', n)?.trim()
                  if (to && to !== n && !cfg.cast.includes(to)) update(renameCast(cfg, n, to))
                }}
              >
                Rename
              </button>
              <button onClick={() => window.confirm(`Remove ${n} from the cast?`) && update(removeCast(cfg, n))}>Remove</button>
            </span>
          </li>
        ))}
      </ul>
      <form
        className="add-row"
        onSubmit={(e) => {
          e.preventDefault()
          add()
        }}
      >
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="New cast member" />
        <button type="submit">Add</button>
      </form>
    </div>
  )
}
