// Global variables
// Same origin: the Vite proxy (dev) or the server (build) forwards /api
const BASE = '/api/notes'

export type Note = {
    id: string
    parent_id: string | null
    is_folder: boolean
    title: string
    body: string
    created_at: string
    updated_at: string
}


// Code
/** Call the notes API through the /api proxy; throw on error. */
async function request<T>(path: string, init?: RequestInit): Promise<T> {

    const res = await fetch(BASE + path, {
        ...init,
        headers: { 'Content-Type': 'application/json' },
    })

    if (!res.ok) {
        throw new Error(`${init?.method ?? 'GET'} ${path}: ${res.status}`)
    }

    return (res.status === 204 ? undefined : await res.json()) as T
}

/** List the children of a folder; null lists the root. */
export function listNotes(parentId: string | null): Promise<Note[]> {

    return request(parentId ? `?parent_id=${parentId}` : '')
}
