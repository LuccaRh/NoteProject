// Imports
import './style.css'
import { Chat } from './chat/chat.ts'
import { createNote, deleteNote, updateNote } from './notes/api.ts'
import { Page } from './notes/page.ts'
import { Tree } from './notes/tree.ts'
import { Tabs } from './tabs.ts'

import type { Note } from './notes/api.ts'


// Global variables
const serverStatus = byId<HTMLElement>('server-status')
const notePanel = byId('note-panel')
const work = byId('work')

const page = new Page(
    {
        page: byId('note'),
        empty: byId('empty'),
        path: byId('path'),
        status: byId('save-status'),
        title: byId('title'),
        editor: byId('editor'),
    }, 
    saved => showSaved(saved)
)

const tree = new Tree(
        byId('tree'), 
        {
                open: note => void openNote(note),
                rename: (note, title) => void rename(note, title),
                remove: note => void remove(note),
        }
)

// The note panel doubles as the empty page when no tab is open
const tabs = new Tabs(byId('tabs'), notePanel, () => void page.close())


// Code
/** Return the element with this id, or throw if index.html lacks it. */
function byId<T extends HTMLElement>(id: string): T {

    const el = document.getElementById(id)

    if (!el) throw new Error(`index.html: missing #${id}`)

    return el as T
}

/** Open a note in its tab, or bring its tab back to the front. */
function openNote(note: Note): Promise<void> {

    return tabs.open({
        id: note.id,
        kind: 'note',
        title: note.title,
        panel: notePanel,
        show: () => page.open(note.id, tree.path(note)),
    })
}

/** Open a new chat tab in a workspace folder (null = no workspace). */
function openChat(folderId: string | null): void {

    const id = crypto.randomUUID()
    const chat = new Chat({
        parent: work,
        folderId,
        folders: () => tree.folders(),
        onTitle: title => tabs.rename(id, title),
    })
    void tabs.open({
        id,
        kind: 'chat',
        title: chat.workspaceName(),
        panel: chat.panel,
        show: () => chat.question.focus(),
        close: () => chat.panel.remove(),
    })
}

/** Show a saved note in the tree and on its tab. */
function showSaved(note: Note): void {

    tree.update(note)
    tabs.rename(note.id, note.title)
}

/** Rename a note; the open one goes through the page. */
async function rename(note: Note, title: string): Promise<void> {

    // The open note saves through the page, with its pending edits
    if (page.note?.id === note.id) {
        page.rename(title)

        return
    }

    showSaved(await updateNote(note.id, { title }))
}

/** Ask, delete a note or folder, and close it if it was open. */
async function remove(note: Note): Promise<void> {

    const what = note.is_folder
        ? 'this folder and everything in it'
        : 'this note'

    if (!confirm(`Delete ${what}? "${note.title}"`)) return

    // Close first, so pending edits never go to a deleted note
    const inside = (id: string): boolean => tree.isInside(id, note.id)
    tabs.closeWhere(tab => tab.kind === 'note' && inside(tab.id))

    if (page.note && inside(page.note.id)) await page.close()

    await deleteNote(note.id)
    tree.delete(note)
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

    await openNote(note)
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
byId('new-chat').addEventListener('click', () => openChat(tree.target()))

void tree.load(null).then(() => {
    serverStatus.textContent = ''
})
