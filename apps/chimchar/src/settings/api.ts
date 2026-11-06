// Global variables
// Same origin: Caddy forwards /api/chat to lonzo, with the session cookie
const BASE = '/api/chat/settings'

export type Settings = {
    has_key: boolean
    key_end: string | null
    model: string
    max_tokens: number
    show_workspace: boolean
}

export type SettingsUpdate = {
    model: string
    max_tokens: number
    show_workspace: boolean
    api_key?: string
}

export type ModelOption = {
    id: string
    name: string
    max_tokens: number | null
}


// Code
/** Call the settings API; the error carries the reason from the server. */
async function request(path: string, init?: RequestInit): Promise<Response> {

    const res = await fetch(BASE + path, {
        ...init,
        headers: { 'Content-Type': 'application/json' },
    })

    if (res.ok) return res

    const body = await res.json().catch(() => null) as { detail?: unknown }
    const detail = body?.detail

    throw new Error(typeof detail === 'string' ? detail : 'Not saved')
}

/** The settings of the account; the key only by its last characters. */
export async function getSettings(): Promise<Settings> {

    const res = await request('')

    return await res.json() as Settings
}

/** Save the settings; without api_key, the saved key stays. */
export async function saveSettings(
    update: SettingsUpdate,
): Promise<Settings> {

    const res = await request('', {
        method: 'PUT',
        body: JSON.stringify(update),
    })

    return await res.json() as Settings
}

/** The models the key of the account can use. */
export async function listModels(): Promise<ModelOption[]> {

    const res = await request('/models')

    return await res.json() as ModelOption[]
}

/** Forget the key of the account. */
export async function removeKey(): Promise<void> {

    await request('/key', { method: 'DELETE' })
}
