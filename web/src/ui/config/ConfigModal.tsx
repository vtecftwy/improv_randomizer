import { useEffect, useState } from 'react'
import type { ProfilesFile } from '../../config/profiles'
import { validateConfig, type StoredConfig } from '../../config/store'
import { CastTab } from './CastTab'
import { DataTab } from './DataTab'
import { GamesTab } from './GamesTab'
import { PromptsTab } from './PromptsTab'

const TABS = ['Cast', 'Games', 'Prompts', 'Data'] as const
type Tab = (typeof TABS)[number]

interface Props {
  profiles: ProfilesFile
  profileKey: string
  initial: StoredConfig
  hasStored: boolean
  sessionStarted: boolean
  onSave: (cfg: StoredConfig) => void
  onReset: () => void
  onClose: () => void
}

export function ConfigModal({ profiles, profileKey, initial, hasStored, sessionStarted, onSave, onReset, onClose }: Props) {
  const [cfg, setCfg] = useState(initial)
  const [tab, setTab] = useState<Tab>('Cast')
  const [errors, setErrors] = useState<string[]>([])
  const dirty = JSON.stringify(cfg) !== JSON.stringify(initial)

  useEffect(() => {
    // Escape never discards unsaved edits; use Close for that.
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && !dirty && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose, dirty])

  const save = () => {
    const found = validateConfig(cfg)
    setErrors(found)
    if (found.length) return
    if (sessionStarted && !window.confirm('Saving restarts the current session. Continue?')) return
    onSave(cfg)
  }

  return (
    <div className="modal-backdrop">
      <div className="modal" role="dialog" aria-label="Configuration">
        <nav className="tabs">
          {TABS.map((t) => (
            <button key={t} className={t === tab ? 'active' : ''} onClick={() => setTab(t)}>
              {t}
            </button>
          ))}
        </nav>
        <div className="modal-body">
          {tab === 'Cast' && <CastTab cfg={cfg} update={setCfg} />}
          {tab === 'Games' && <GamesTab cfg={cfg} update={setCfg} />}
          {tab === 'Prompts' && <PromptsTab cfg={cfg} update={setCfg} />}
          {tab === 'Data' && (
            <DataTab cfg={cfg} update={setCfg} profiles={profiles} profileKey={profileKey} hasStored={hasStored} dirty={dirty} onReset={onReset} />
          )}
        </div>
        {errors.length > 0 && (
          <ul className="error">
            {errors.map((e) => (
              <li key={e}>{e}</li>
            ))}
          </ul>
        )}
        <div className="modal-footer">
          <button onClick={save} disabled={!dirty}>
            Save changes
          </button>
          <button onClick={() => (!dirty || window.confirm('Discard unsaved changes?')) && onClose()}>Close</button>
        </div>
      </div>
    </div>
  )
}
