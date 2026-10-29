// Imports
import './style.css'
import { createNote, updateNote } from './notes/api.ts'
import { Page } from './notes/page.ts'
import { Tree } from './notes/tree.ts'

import type { Note } from './notes/api.ts'


// Global variables
const serverStatus = byId<HTMLElement>('server-status')

const page = new Page(
    {
        page: byId('note'),
        empty: byId('empty'),
        path: byId('path'),
        status: byId('save-status'),
        title: byId('title'),
        editor: byId('editor'),
    }, 
    saved => tree.update(saved)
)

const tree = new Tree(
        byId('tree'), 
        {
                open: note => void page.open(note.id, tree.path(note)),
                rename: (note, title) => void rename(note, title),
        }
)


// Code
/** Return the element with this id, or throw if index.html lacks it. */
function byId<T extends HTMLElement>(id: string): T {

    const el = document.getElementById(id)

    if (!el) throw new Error(`index.html: missing #${id}`)

    return el as T
}

/** Rename a note; the open one goes through the page. */
async function rename(note: Note, title: string): Promise<void> {

    // The open note saves through the page, with its pending edits
    if (page.note?.id === note.id) {
        page.rename(title)

        return
    }

    tree.update(await updateNote(note.id, { title }))
}

/** Create a note (and open it) or a folder (and rename it). */
async function create(isFolder: boolean): Promise<void> {

    const note = await createNote({
        title: isFolder ? 'New folder' : 'Untitled',
        parent_id: tree.target(),
        is_folder: isFolder,
    })
    await tree.add(note)

    if (isFolder) {
        tree.startRename(note)

        return
    }

    await page.open(note.id, tree.path(note))
    byId<HTMLInputElement>('title').select()
}

// Any request that failed and nobody caught ends up here
window.addEventListener('unhandledrejection', event => {
    serverStatus.textContent = 'Server unreachable'
    console.error(event.reason)
})

// Leaving the tab: send what is still waiting for the pause
document.addEventListener('visibilitychange', () => {

    if (document.visibilityState === 'hidden') void page.flush()
})

byId('new-note').addEventListener('click', () => void create(false))
byId('new-folder').addEventListener('click', () => void create(true))

void tree.load(null).then(() => {
    serverStatus.textContent = ''
})
