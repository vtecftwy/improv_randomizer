import { useEffect, useState } from 'react'
import { assetUrl, loadProfileData, loadProfiles, type Profile, type ProfilesFile } from './config/profiles'
import { clearStored, configFromDefaults, loadStored, saveStored, sessionDataFrom, type StoredConfig } from './config/store'
import type { SessionData } from './engine/session'
import { AudioManager } from './ui/audio'
import { ConfigModal } from './ui/config/ConfigModal'
import { ControlBar } from './ui/ControlBar'
import { GameCanvas } from './ui/GameCanvas'
import { InfoPanel } from './ui/InfoPanel'
import { discardSession } from './ui/persistence'
import { useGameSession } from './ui/useGameSession'

interface Loaded {
  defaults: SessionData
  profiles: ProfilesFile
  profile: Profile
  profileKey: string
}

function Session({ defaults, profiles, profile, profileKey }: Loaded) {
  // The user's saved configuration, when present, replaces the bundled defaults.
  const [stored] = useState(() => loadStored(profileKey))
  const [config] = useState<StoredConfig>(() => stored ?? configFromDefaults(defaults))
  const [data] = useState(() => sessionDataFrom(config))

  const [audio] = useState(() => new AudioManager((f) => assetUrl(`audio/${f}`)))
  const [muted, setMuted] = useState(audio.muted)
  const [configOpen, setConfigOpen] = useState(false)
  const { session, view, next, reset } = useGameSession(data, profile, profileKey, audio)
  const timeUp = view.started && view.timeLeftMs <= 0

  useEffect(() => {
    document.title = 'C.H.R.I.S'
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Enter' || configOpen) return
      const tag = (e.target as HTMLElement).tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return
      e.preventDefault() // avoid a second activation of the focused button
      if (!timeUp) next()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [next, timeUp, configOpen])

  // A saved session indexes the old game list, so any config change starts a fresh session.
  const applyConfig = (apply: () => void) => {
    apply()
    discardSession()
    window.location.reload()
  }

  return (
    <div className="app">
      <div className="main">
        <GameCanvas
          games={session.games}
          view={view}
          backgroundUrl={assetUrl(`img/${profile.backgroundImage}`)}
        />
        <InfoPanel games={session.games} view={view} />
      </div>
      <ControlBar
        view={view}
        muted={muted}
        onNext={next}
        onReset={reset}
        onConfig={() => setConfigOpen(true)}
        onToggleMute={() => {
          audio.setMuted(!audio.muted)
          setMuted(audio.muted)
        }}
      />
      {configOpen && (
        <ConfigModal
          profiles={profiles}
          profileKey={profileKey}
          initial={config}
          hasStored={stored !== null}
          sessionStarted={view.started}
          onClose={() => setConfigOpen(false)}
          onSave={(cfg) => applyConfig(() => saveStored(profileKey, cfg))}
          onReset={() => applyConfig(() => clearStored(profileKey))}
        />
      )}
    </div>
  )
}

export default function App() {
  const [state, setState] = useState<Loaded | string | null>(null)

  useEffect(() => {
    const params = new URLSearchParams(location.search)
    loadProfiles()
      .then(async (profiles) => {
        const profileKey = params.get('profile') ?? profiles.defaultProfile
        const profile = profiles.profiles[profileKey]
        if (!profile) throw new Error(`Unknown profile "${profileKey}"`)
        setState({ defaults: await loadProfileData(profile), profiles, profile, profileKey })
      })
      .catch((e: Error) => setState(e.message))
  }, [])

  if (state === null) return <div className="app">Loading...</div>
  if (typeof state === 'string') return <div className="app">Error: {state}</div>
  return <Session {...state} />
}
