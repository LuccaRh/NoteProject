// Imports
import { listNotes } from './api.ts'

import type { Note } from './api.ts'


// Global variables
// Key of the top level in the children cache
const ROOT = 'root'

const CHEVRON = '<svg aria-hidden="true" width="12" height="12"'
    + ' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    + ' stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
    + '<path d="M9 6l6 6-6 6"/></svg>'


// Code
/** Sidebar: folders open on demand, one GET per folder the first time. */
export class Tree {
    children: Map<string, Note[]> = new Map()
    expanded: Set<string> = new Set()
    selected: Note | null = null
    list: HTMLUListElement

    /** Keep the list element the tree draws into. */
    constructor(list: HTMLUListElement) {

        this.list = list
    }

    /** Fetch the children of a folder (null = root) and redraw. */
    async load(parentId: string | null): Promise<void> {

        this.children.set(parentId ?? ROOT, await listNotes(parentId))
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

    /** Build the row of a note: a button with its name. */
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

        const open = document.createElement('button')
        open.className = 'node-open'

        if (note.is_folder) open.innerHTML = CHEVRON

        // textContent, never innerHTML: the title is user text
        const name = document.createElement('span')
        name.textContent = note.title || 'Untitled'
        open.append(name)
        open.addEventListener('click', () => void this.click(note))

        item.append(open)

        return item
    }

    /** Select a note, or open or close a folder (fetching it once). */
    async click(note: Note): Promise<void> {

        this.selected = note

        if (!note.is_folder) {
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
}
