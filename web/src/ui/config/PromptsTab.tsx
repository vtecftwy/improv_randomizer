import { useState } from 'react'
import type { TabProps } from './CastTab'

export function PromptsTab({ cfg, update }: TabProps) {
  const [text, setText] = useState('')
  const add = () => {
    const p = text.trim()
    if (p && !cfg.prompts.includes(p)) update({ ...cfg, prompts: [...cfg.prompts, p] })
    setText('')
  }

  return (
    <div>
      <p className="hint">Used by games that have no fixed prompt.</p>
      <ul className="rows">
        {cfg.prompts.map((p, i) => (
          <li key={p + i}>
            <span>{p}</span>
            <span className="row-actions">
              <button
                onClick={() => {
                  const to = window.prompt('Edit prompt', p)?.trim()
                  if (to) update({ ...cfg, prompts: cfg.prompts.map((x, j) => (j === i ? to : x)) })
                }}
              >
                Edit
              </button>
              <button onClick={() => update({ ...cfg, prompts: cfg.prompts.filter((_, j) => j !== i) })}>Remove</button>
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
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="New prompt" />
        <button type="submit">Add</button>
      </form>
    </div>
  )
}
