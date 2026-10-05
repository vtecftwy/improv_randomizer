import { buildGames, parseLines, type SessionData } from '../engine/session'
import type { GamesFile, SessionSettings } from '../engine/types'

export interface Profile extends SessionSettings {
  label: string
  folder: string
  cast: string
  games: string
  prompts: string
  backgroundImage: string
  spinLaps?: number
  spinDurationMs?: number
}

export interface ProfilesFile {
  defaultProfile: string
  profiles: Record<string, Profile>
}

const base = import.meta.env.BASE_URL

export const assetUrl = (path: string) => `${base}assets/${path}`

async function fetchOk(url: string): Promise<Response> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Failed to load ${url}: ${res.status}`)
  return res
}

export async function loadProfiles(): Promise<ProfilesFile> {
  return (await fetchOk(`${base}config/profiles.json`)).json()
}

export async function loadProfileData(profile: Profile): Promise<SessionData> {
  const dir = `${base}config/${profile.folder}`
  const [games, cast, prompts] = await Promise.all([
    fetchOk(`${dir}/${profile.games}`).then((r) => r.json() as Promise<GamesFile>),
    fetchOk(`${dir}/${profile.cast}`).then((r) => r.text()),
    fetchOk(`${dir}/${profile.prompts}`).then((r) => r.text()),
  ])
  return { games: buildGames(games), cast: parseLines(cast), prompts: parseLines(prompts) }
}
