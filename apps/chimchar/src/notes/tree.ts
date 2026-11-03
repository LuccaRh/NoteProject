// Imports
import { listNotes } from './api.ts'

import type { Note } from './api.ts'


// Global variables
export type Folder = {
    id: string
    // Titles from the top down to the folder, joined by " / "
    path: string
}

type Handlers = {
    open: (note: Note) => void
    rename: (note: Note, title: string) => void
    remove: (note: Note) => void
    search: (folder: Note) => void
}

// Key of the top level in the children cache
const ROOT = 'root'

// Folder that holds a workspace's rules, never a workspace itself
const WORKSPACE = '.workspace'

const CHEVRON = '<svg aria-hidden="true" width="12" height="12"'
    + ' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    + ' stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
    + '<path d="M9 6l6 6-6 6"/></svg>'

const MAGNIFIER = '<svg aria-hidden="true" width="14" height="14"'
    + ' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    + ' stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    + '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/></svg>'

const PENCIL = '<svg aria-hidden="true" width="14" height="14"'
    + ' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    + ' stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    + '<path d="M4 20h4L19 9l-4-4L4 16zM13 7l4 4"/></svg>'

const TRASH = '<svg aria-hidden="true" width="14" height="14"'
    + ' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    + ' stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    + '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/></svg>'


// Code
/** Sidebar: folders open on demand, one GET per folder the first time. */
export class Tree {
    children: Map<string, Note[]> = new Map()
    expanded: Set<string> = new Set()
    selected: Note | null = null
    editing: string | null = null
    list: HTMLUListElement
    handlers: Handlers

    /** Keep the list element and the actions main.ts handles. */
    constructor(list: HTMLUListElement, handlers: Handlers) {

        this.list = list
        this.handlers = handlers
    }

    /** Fetch the children of a folder (null = root) and redraw. */
    async load(parentId: string | null): Promise<void> {

        this.children.set(parentId ?? ROOT, await listNotes(parentId))
        this.render()
    }

    /** Look up a note among the folders already loaded. */
    find(id: string): Note | undefined {

        for (const notes of this.children.values()) {
            const note = notes.find(n => n.id === id)

            if (note) return note
        }

        return undefined
    }

    /** Titles of the folders above a note, top first. */
    path(note: Note): string[] {

        const titles: string[] = []
        let parent = note.parent_id ? this.find(note.parent_id) : undefined

        while (parent) {
            titles.unshift(parent.title || 'Untitled')
            parent = parent.parent_id ? this.find(parent.parent_id) : undefined
        }

        return titles
    }

    /** True when id is the folder itself or somewhere below it. */
    isInside(id: string, folderId: string): boolean {

        let note = this.find(id)

        while (note) {
            if (note.id === folderId) return true

            note = note.parent_id ? this.find(note.parent_id) : undefined
        }

        return false
    }

    /** Folders loaded so far, in tree order, without .workspace ones. */
    folders(parentId: string | null = null): Folder[] {

        const found: Folder[] = []

        for (const note of this.children.get(parentId ?? ROOT) ?? []) {

            if (!note.is_folder || note.title === WORKSPACE) continue

            const path = [...this.path(note), note.title || 'Untitled']
            found.push({
                id: note.id,
                path: path.join(' / '),
            })
            found.push(...this.folders(note.id))
        }

        return found
    }

    /** Folder where a new item goes: the selected one or its parent. */
    target(): string | null {

        if (!this.selected) return null

        return this.selected.is_folder
            ? this.selected.id
            : this.selected.parent_id
    }

    /** Put a new note in the tree, open its folder and select it. */
    async add(note: Note): Promise<void> {

        const parentId = note.parent_id

        // Fetching an unopened folder already brings the new note
        if (parentId && !this.children.has(parentId)) {
            this.expanded.add(parentId)
            await this.load(parentId)
        } else {
            const key = parentId ?? ROOT
            const notes = [...(this.children.get(key) ?? []), note]
            this.children.set(key, sorted(notes))
        }

        if (parentId) this.expanded.add(parentId)

        this.selected = note
        this.render()
    }

    /** Swap in the saved version of a note; re-sort on a new title. */
    update(note: Note): void {

        const key = note.parent_id ?? ROOT
        const notes = this.children.get(key) ?? []
        const index = notes.findIndex(n => n.id === note.id)

        if (index === -1) return

        const titleChanged = notes[index].title !== note.title
        notes[index] = note

        if (this.selected?.id === note.id) this.selected = note

        if (titleChanged) {
            this.children.set(key, sorted(notes))
            this.render()
        }
    }

    /** Remove a note from the tree; unselect it if it was inside. */
    delete(note: Note): void {

        const key = note.parent_id ?? ROOT
        const notes = this.children.get(key) ?? []
        this.children.set(key, notes.filter(n => n.id !== note.id))

        if (this.selected && this.isInside(this.selected.id, note.id)) {
            this.selected = null
        }

        this.render()
    }

    /** Turn the row of a note into a name input. */
    startRename(note: Note): void {

        this.editing = note.id
        this.render()
    }

    /** Redraw the whole list from the loaded folders. */
    render(): void {

        this.list.replaceChildren(...this.rows(null, 0))
    }

    /** Rows of a folder and of its open subfolders, in order. */
    rows(parentId: string | null, depth: number): HTMLLIElement[] {

        const items: HTMLLIElement[] = []

        for (const note of this.children.get(parentId ?? ROOT) ?? []) {
            items.push(this.row(note, depth))

            if (note.is_folder && this.expanded.has(note.id)) {
                items.push(...this.rows(note.id, depth + 1))
            }
        }

        return items
    }

    /** Build the row of a note: name, search (folders), rename, delete. */
    row(note: Note, depth: number): HTMLLIElement {

        const item = document.createElement('li')
        item.role = 'treeitem'
        item.className = 'node'
        item.ariaLevel = String(depth + 1)
        item.ariaSelected = String(note.id === this.selected?.id)
        item.style.setProperty('--depth', String(depth))

        if (note.is_folder) {
            item.classList.add('folder')
            item.ariaExpanded = String(this.expanded.has(note.id))
        }

        if (this.editing === note.id) {
            item.append(this.renameInput(note))

            return item
        }

        const open = document.createElement('button')
        open.className = 'node-open'

        if (note.is_folder) open.innerHTML = CHEVRON

        // textContent, never innerHTML: the title is user text
        const name = document.createElement('span')
        name.textContent = note.title || 'Untitled'
        open.append(name)
        open.addEventListener('click', () => void this.click(note))
        open.addEventListener('dblclick', () => this.startRename(note))

        const rename = iconButton(PENCIL, `Rename ${note.title}`)
        rename.addEventListener('click', () => this.startRename(note))

        const remove = iconButton(TRASH, `Delete ${note.title}`)
        remove.addEventListener('click', () => this.handlers.remove(note))

        item.append(open)

        if (note.is_folder) {
            const search = iconButton(MAGNIFIER, `Search in ${note.title}`)
            search.addEventListener('click', () => this.handlers.search(note))
            item.append(search)
        }

        item.append(rename, remove)

        return item
    }

    /** Open a note, or open or close a folder (fetching it once). */
    async click(note: Note): Promise<void> {

        this.selected = note

        if (!note.is_folder) {
            this.handlers.open(note)
            this.render()

            return
        }

        if (this.expanded.has(note.id)) {
            this.expanded.delete(note.id)
        } else {
            this.expanded.add(note.id)

            if (!this.children.has(note.id)) await this.load(note.id)
        }

        this.render()
    }

    /** Name input: Enter or blur saves, Escape gives up. */
    renameInput(note: Note): HTMLInputElement {

        const input = document.createElement('input')
        input.className = 'node-rename'
        input.value = note.title
        input.ariaLabel = 'Name'
        let done = false

        // Enter and blur save, Escape gives up; done stops a second call
        const finish = (save: boolean): void => {

            if (done) return

            done = true
            this.editing = null
            const title = input.value.trim()

            if (save && title && title !== note.title) {
                this.handlers.rename(note, title)
            }

            this.render()
        }

        input.addEventListener('keydown', event => {

            if (event.key === 'Enter') finish(true)

            if (event.key === 'Escape') finish(false)
        })
        input.addEventListener('blur', () => finish(true))
        requestAnimationFrame(() => {
            input.focus()
            input.select()
        })

        return input
    }
}

/** Sort like the server: folders first, then by title. */
function sorted(notes: Note[]): Note[] {

    return notes.sort((a, b) =>
        Number(b.is_folder) - Number(a.is_folder)
        || a.title.localeCompare(b.title))
}

/** Small row button with an icon and an accessible label. */
function iconButton(svg: string, label: string): HTMLButtonElement {

    const button = document.createElement('button')
    button.className = 'node-action'
    button.ariaLabel = label
    button.title = label
    button.innerHTML = svg

    return button
}
