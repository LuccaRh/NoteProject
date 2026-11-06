// Global variables
// Same origin: Caddy forwards /api/chat to lonzo, with the session cookie
const BASE = '/api/chat'

export type WorkspaceSkill = {
    id: string
    title: string
    summary: string
}

export type PublishedSkill = WorkspaceSkill & {
    user_id: string
    body: string
}

export type SkillSource = { skill_id: string } | { note_id: string }


// Code
/** Call the skills API; the error carries the reason from the server. */
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

/** The skills the person published, or the ones everyone else did. */
export async function listPublished(mine: boolean): Promise<PublishedSkill[]> {

    const res = await request(mine ? '/skills?owner=me' : '/skills')

    return await res.json() as PublishedSkill[]
}

/** The skills of a workspace, by the folder that holds it. */
export async function listWorkspaceSkills(
    folderId: string,
): Promise<WorkspaceSkill[]> {

    const res = await request(`/workspaces/${folderId}/skills`)

    return await res.json() as WorkspaceSkill[]
}

/** Copy a published skill or a skill note to a workspace. */
export async function addSkill(
    folderId: string,
    source: SkillSource,
): Promise<void> {

    await request(`/workspaces/${folderId}/skills`, {
        method: 'POST',
        body: JSON.stringify(source),
    })
}

/** Publish a skill note, or update what it published before. */
export async function publishSkill(noteId: string): Promise<void> {

    await request('/skills', {
        method: 'POST',
        body: JSON.stringify({ note_id: noteId }),
    })
}
