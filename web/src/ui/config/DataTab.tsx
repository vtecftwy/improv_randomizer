import { useState } from 'react'
import type { ProfilesFile } from '../../config/profiles'
import { applyImport, toGamesFile } from '../../config/store'
import type { TabProps } from './CastTab'

function download(name: string, text: string, type = 'application/json') {
  const url = URL.createObjectURL(new Blob([text], { type }))
  const a = document.createElement('a')
  a.href = url
  a.download = name
  a.click()
  URL.revokeObjectURL(url)
}

interface Props extends TabProps {
  profiles: ProfilesFile
  profileKey: string
  hasStored: boolean
  dirty: boolean
  onReset: () => void
}

export function DataTab({ cfg, update, profiles, profileKey, hasStored, dirty, onReset }: Props) {
  const [message, setMessage] = useState('')

  const importFiles = async (files: FileList | null) => {
    if (!files?.length) return
    try {
      const texts = await Promise.all([...files].map(async (f) => ({ name: f.name, text: await f.text() })))
      update(applyImport(cfg, texts))
      setMessage(`Imported ${files.length} file(s). Review the tabs, then Save.`)
    } catch (e) {
      setMessage(`Import failed: ${(e as Error).message}`)
    }
  }

  return (
    <div className="data-tab">
      <label>
        Profile{' '}
        <select
          value={profileKey}
          onChange={(e) => {
            if (!dirty || window.confirm('Discard unsaved changes and switch profile?')) location.search = `?profile=${e.target.value}`
          }}
        >
          {Object.entries(profiles.profiles).map(([k, p]) => (
            <option key={k} value={k}>
              {p.label}
            </option>
          ))}
        </select>
      </label>

      <h3>Export</h3>
      <div className="row-actions">
        <button onClick={() => download(`chris-${profileKey}.json`, JSON.stringify(cfg, null, 2))}>Everything (JSON)</button>
        <button onClick={() => download('games.json', JSON.stringify(toGamesFile(cfg.games), null, 4))}>games.json</button>
        <button onClick={() => download('cast.txt', cfg.cast.join('\n'), 'text/plain')}>cast.txt</button>
        <button onClick={() => download('prompts.txt', cfg.prompts.join('\n'), 'text/plain')}>prompts.txt</button>
      </div>

      <h3>Import</h3>
      <p className="hint">An exported JSON, or the old games.json, cast.txt and prompts.txt files (file names containing "prompt" are read as prompts).</p>
      <input type="file" multiple accept=".json,.txt" onChange={(e) => importFiles(e.target.files)} />
      {message && <p className="hint">{message}</p>}

      <h3>Defaults</h3>
      <button disabled={!hasStored} onClick={() => window.confirm('Discard your custom configuration for this profile?') && onReset()}>
        Reset to default
      </button>
    </div>
  )
}
