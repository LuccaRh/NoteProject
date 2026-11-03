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

// One entry of the whole tree, with its titles joined by "/"
export type NotePath = {
    id: string
    path: string
    is_folder: boolean
}

// A note found by its words, only what is needed to open it
export type NoteMatch = {
    id: string
    title: string
}

// A note or folder found by a text in its title
export type TitleMatch = {
    id: string
    title: string
    is_folder: boolean
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

/** Everything at any depth, each with its path of titles. */
export function listTree(): Promise<NotePath[]> {

    return request('/tree')
}

/** Ask a search route for a text, only inside a folder if given. */
function search<T>(
    route: string,
    query: string,
    parentId: string | null,
): Promise<T[]> {

    const params = new URLSearchParams({ q: query })

    if (parentId) params.set('parent_id', parentId)

    return request(`/${route}?${params}`)
}

/** Notes whose title or body has the words; only inside a folder if given. */
export function searchNotes(
    query: string,
    parentId: string | null,
): Promise<NoteMatch[]> {

    return search('search', query, parentId)
}

/** Notes and folders whose title contains the text, even mid-word. */
export function searchTitles(
    query: string,
    parentId: string | null,
): Promise<TitleMatch[]> {

    return search('search-titles', query, parentId)
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
