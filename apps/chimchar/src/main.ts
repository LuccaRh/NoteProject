// Imports
import './style.css'
import './themes/grid.css'
import './themes/retro.css'
import { isLoggedIn, logOut } from './auth/api.ts'
import { LoginDialog } from './auth/login-dialog.ts'
import { Chat } from './chat/chat.ts'
import { WorkspaceDialog } from './chat/workspace-dialog.ts'
import {
    createNote,
    deleteNote,
    getNote,
    listTree,
    updateNote,
} from './notes/api.ts'
import { Page } from './notes/page.ts'
import { Search } from './notes/search.ts'
import { Tree } from './notes/tree.ts'
import { getSettings } from './settings/api.ts'
import { SettingsDialog } from './settings/settings-dialog.ts'
import { SkillsTab } from './skills/skills-tab.ts'
import { Tabs } from './tabs.ts'

import type { Note } from './notes/api.ts'
import type { Found } from './notes/search.ts'
import type { Settings } from './settings/api.ts'


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
    {
        entries: () => search.visible(),
        open: id => void openLink(id),
    },
    saved => showSaved(saved)
)

const tree = new Tree(
        byId('tree'), 
        {
                open: note => void openNote(note, () => tree.path(note)),
                rename: (note, title) => void rename(note, title),
                remove: note => void remove(note),
                search: folder => void search.open(folder.id),
        }
)

const search = new Search(
    {
        dialog: byId('search-dialog'),
        scope: byId('search-scope'),
        scopePath: byId('search-scope-path'),
        scopeClear: byId('search-scope-clear'),
        input: byId('search-input'),
        results: byId('search-results'),
        modeAll: byId('search-mode-all'),
        modeTitles: byId('search-mode-titles'),
    },
    found => void openFound(found),
)

const workspaceDialog = new WorkspaceDialog(
    {
        dialog: byId('workspace-dialog'),
        form: byId('workspace-form'),
        folder: byId('workspace-folder'),
        description: byId('workspace-description'),
        status: byId('workspace-status'),
        create: byId('workspace-create'),
        cancel: byId('workspace-cancel'),
    },
    () => tree.folders(),
    folderId => void workspaceCreated(folderId),
)

const loginDialog = new LoginDialog({
    dialog: byId('login-dialog'),
    form: byId('login-form'),
    email: byId('login-email'),
    password: byId('login-password'),
    status: byId('login-status'),
    submit: byId('login-submit'),
})

const settingsDialog = new SettingsDialog(
    {
        dialog: byId('settings-dialog'),
        form: byId('settings-form'),
        apiKey: byId('settings-api-key'),
        keyState: byId('settings-key-state'),
        removeKey: byId('settings-remove-key'),
        model: byId('settings-model'),
        thinking: byId('settings-thinking'),
        maxTokens: byId('settings-max-tokens'),
        toolsMaxTurns: byId('settings-tools-max-turns'),
        showWorkspace: byId('settings-show-workspace'),
        theme: byId('settings-theme'),
        status: byId('settings-status'),
        close: byId('settings-close'),
    },
    settings => applySettings(settings),
)

// The note panel doubles as the empty page when no tab is open
const tabs = new Tabs(byId('tabs'), notePanel, () => void page.close())
const skills = new SkillsTab({
    parent: work,
    openNote: id => openLink(id),
    onNotesChanged: () => void notesChanged(),
})


// Code
/** Return the element with this id, or throw if index.html lacks it. */
function byId<T extends HTMLElement>(id: string): T {

    const el = document.getElementById(id)

    if (!el) throw new Error(`index.html: missing #${id}`)

    return el as T
}

/**
 * Open a note in its tab, or bring its tab back to the front.
 * folders: titles above the note, read each time the tab shows.
 */
function openNote(
    note: { id: string, title: string },
    folders: () => string[],
): Promise<void> {

    return tabs.open({
        id: note.id,
        kind: 'note',
        title: note.title,
        panel: notePanel,
        show: () => page.open(note.id, folders()),
    })
}

/** Open the note of a link; it may be deleted or someone else's. */
async function openLink(id: string): Promise<boolean> {

    try {
        const note = await getNote(id)
        await openNote(note, () => tree.path(note))

        return true
    } catch {
        page.say('Could not find this note')

        return false
    }
}

/** Open a note picked in the search, with its words marked. */
async function openFound(found: Found): Promise<void> {

    await openNote(found, () => found.folders)
    page.mark(found.words)
}

/** Open a new chat tab in a workspace folder (null = no workspace). */
function openChat(folderId: string | null): void {

    const id = crypto.randomUUID()
    const chat = new Chat({
        parent: work,
        folderId,
        folders: () => tree.folders(),
        onTitle: title => tabs.rename(id, title),
        onNotesChanged: () => void notesChanged(),
        openNote: id => openLink(id),
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

/** Open the tab of the skills, or bring it back to the front. */
function openSkills(): void {

    void tabs.open({
        id: 'skills',
        kind: 'skills',
        title: 'Skills',
        panel: skills.panel,
        show: () => skills.load(),
        close: () => { skills.panel.hidden = true },
    })
}

/** Show the new .workspace in the tree and open a chat in it. */
async function workspaceCreated(folderId: string): Promise<void> {

    await tree.load(folderId)
    openChat(folderId)
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
    await closeNotes(id => tree.isInside(id, note.id))
    await deleteNote(note.id)
    tree.delete(note)
}

/** Close the tabs of some notes, and the page if it shows one of them. */
async function closeNotes(test: (id: string) => boolean): Promise<void> {

    tabs.closeWhere(tab => tab.kind === 'note' && test(tab.id))

    if (page.note && test(page.note.id)) await page.close()
}

/** Show what the AI wrote: close what it deleted, fetch the rest again. */
async function notesChanged(): Promise<void> {

    const entries = await listTree()
    const ids = new Set(entries.map(entry => entry.id))
    await closeNotes(id => !ids.has(id))
    await tree.reload()
    await page.reload()
}

/** Show or hide the .workspace folders as the settings ask. */
function applySettings(settings: Settings): void {

    tree.showWorkspace(settings.show_workspace)
    search.workspaceShown = settings.show_workspace
}

/** Send pending edits, end the session and start again at the login. */
async function leave(): Promise<void> {

    await page.flush()
    await logOut()
    location.reload()
}

/** Ask for the login when there is no session, then load the tree. */
async function start(): Promise<void> {

    if (!(await isLoggedIn())) await loginDialog.open()

    await tree.load(null)
    serverStatus.textContent = ''

    // Notes work without lonzo: the folders just stay hidden
    getSettings().then(applySettings).catch(console.error)
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

    await openNote(note, () => tree.path(note))
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

// Ctrl+O, as in Obsidian: search everywhere
document.addEventListener('keydown', event => {

    if (!(event.ctrlKey || event.metaKey) || event.key !== 'o') return

    event.preventDefault()
    void search.open(null)
})

byId('search').addEventListener('click', () => void search.open(null))
byId('new-note').addEventListener('click', () => void create(false))
byId('new-folder').addEventListener('click', () => void create(true))
byId('new-chat').addEventListener('click', () => openChat(tree.target()))
byId('new-workspace').addEventListener('click', () => {
    workspaceDialog.open(tree.target())
})
byId('open-skills').addEventListener('click', openSkills)

byId('settings').addEventListener('click', () => {
    void settingsDialog.open()
})
byId('log-out').addEventListener('click', () => void leave())

void start()
