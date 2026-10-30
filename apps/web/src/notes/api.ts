// Global variables
// Same origin: Caddy forwards /api to the notes service
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

export type NoteCreate = {
    title: string
    body?: string
    parent_id?: string | null
    is_folder?: boolean
}

export type NoteUpdate = {
    title?: string
    body?: string
    parent_id?: string | null
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

/** Fetch one note by id. */
export function getNote(id: string): Promise<Note> {

    return request(`/${id}`)
}

/** Create a note or folder on the server. */
export function createNote(note: NoteCreate): Promise<Note> {

    return request('', {
        method: 'POST',
        body: JSON.stringify(note),
    })
}

/**
 * Change only the given fields of a note.
 * keepalive: the save still goes out if the tab closes.
 */
export function updateNote(id: string, fields: NoteUpdate): Promise<Note> {

    return request(`/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(fields),
        keepalive: true,
    })
}

/** Delete a note; a folder goes with everything inside it. */
export function deleteNote(id: string): Promise<void> {

    return request(`/${id}`, { method: 'DELETE' })
}
