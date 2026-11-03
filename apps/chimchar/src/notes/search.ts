// Imports
import { fold } from '../fold.ts'
import { listTree, searchNotes, searchTitles } from './api.ts'

import type { NotePath } from './api.ts'


// Global variables
type Elements = {
    dialog: HTMLDialogElement
    scope: HTMLElement
    scopePath: HTMLElement
    scopeClear: HTMLButtonElement
    input: HTMLInputElement
    results: HTMLUListElement
    modeAll: HTMLButtonElement
    modeTitles: HTMLButtonElement
}

// A note picked in the search: what main.ts needs to open it
export type Found = {
    id: string
    title: string
    folders: string[]
    // Words of the query, to mark in the note
    words: string[]
}

// Pause in typing before asking the server for the words in the bodies
const SEARCH_DELAY_MS = 200

// Rows shown at most; more words narrow the list down
const MAX_ROWS = 50

const FOLDER = '<svg aria-hidden="true" width="14" height="14"'
    + ' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    + ' stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    + '<path d="M3 6h6l2 2h10v11H3z"/></svg>'

const NOTE = '<svg aria-hidden="true" width="14" height="14"'
    + ' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    + ' stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    + '<path d="M14 3H6v18h12V7zM14 3v4h4"/></svg>'


// Code
/**
 * Quick switcher: notes by title or body, folders by name; or, in
 * titles only, notes and folders by a text in the title.
 * Picking a folder searches inside it; Backspace on an empty
 * field goes one folder up.
 */
export class Search {
    els: Elements
    onOpen: (found: Found) => void
    // The whole tree, fetched each time the pop-up opens
    entries: NotePath[] = []
    // Folder the search stays inside; null = everywhere
    scope: NotePath | null = null
    // Kept between openings, like the last folder of a file dialog
    titlesOnly: boolean = false
    rows: NotePath[] = []
    active: number = 0
    timer: number | undefined = undefined
    // Only the answer to the latest query is shown
    asked: number = 0

    /** Wire the field, the keys and the button that leaves the folder. */
    constructor(els: Elements, onOpen: (found: Found) => void) {

        this.els = els
        this.onOpen = onOpen
        els.input.addEventListener('input', () => this.update())
        els.input.addEventListener('keydown', event => this.key(event))
        els.modeAll.addEventListener('click', () => this.mode(false))
        els.modeTitles.addEventListener('click', () => this.mode(true))
        els.scopeClear.addEventListener('click', () => {
            this.enter(null)
            els.input.focus()
        })
        els.dialog.addEventListener('close', () => clearTimeout(this.timer))

        // A click on the backdrop lands on the dialog itself
        els.dialog.addEventListener('click', event => {

            if (event.target === els.dialog) els.dialog.close()
        })
    }

    /** Open the pop-up, searching inside a folder (null = everywhere). */
    async open(folderId: string | null): Promise<void> {

        this.entries = await listTree()
        const folder = this.entries.find(entry => entry.id === folderId)
        this.enter(folder ?? null)
        this.els.dialog.showModal()
    }

    /** Search inside a folder (null = everywhere) from an empty field. */
    enter(folder: NotePath | null): void {

        this.scope = folder
        this.els.input.value = ''
        this.els.scope.hidden = !folder
        this.els.scopePath.textContent = folder ? spaced(folder.path) : ''
        this.showMode()
    }

    /** Search everything (false) or only the titles (true). */
    mode(titlesOnly: boolean): void {

        this.titlesOnly = titlesOnly
        this.showMode()
        this.els.input.focus()
    }

    /** Press the button of the mode, word the placeholder, search again. */
    showMode(): void {

        const where = this.scope ? ' in this folder' : ''
        this.els.modeAll.ariaPressed = String(!this.titlesOnly)
        this.els.modeTitles.ariaPressed = String(this.titlesOnly)
        this.els.input.placeholder = this.titlesOnly
            ? `Search titles${where}...`
            : `Search notes and folders${where}...`
        this.update()
    }

    /**
     * Names match at once and the bodies come from the server after a
     * pause; in titles only, everything comes from the server.
     */
    update(): void {

        clearTimeout(this.timer)
        this.asked++
        const query = this.els.input.value.trim()
        const words = fold(query).split(/\s+/).filter(Boolean)
        const fromServer = this.titlesOnly && words.length > 0
        const byName = fromServer ? [] : this.entries.filter(entry =>
            this.inside(entry)
            && words.every(word => fold(this.relative(entry)).includes(word)))

        // A new query starts from the first row
        this.rows = []
        this.els.dialog.classList.toggle('searching', words.length > 0)
        this.show(byName)

        if (words.length === 0) return

        const asked = this.asked
        this.timer = window.setTimeout(
            () => void this.searchServer(query, byName, asked),
            SEARCH_DELAY_MS,
        )
    }

    /** Add what the server found (by words or by title) to the rows. */
    async searchServer(
        query: string,
        byName: NotePath[],
        asked: number,
    ): Promise<void> {

        const parentId = this.scope?.id ?? null
        const search = this.titlesOnly ? searchTitles : searchNotes
        const matches = await search(query, parentId).finally(() => {

            if (asked === this.asked) {
                this.els.dialog.classList.remove('searching')
            }
        })

        // The query changed while the server answered
        if (asked !== this.asked) return

        const shown = new Set(byName.map(entry => entry.id))
        const byWords = this.entries.filter(entry =>
            !shown.has(entry.id)
            && matches.some(match => match.id === entry.id))
        this.show([...byName, ...byWords])
    }

    /** True when an entry is below the folder being searched. */
    inside(entry: NotePath): boolean {

        return !this.scope || entry.path.startsWith(this.scope.path + '/')
    }

    /** Path of an entry from the folder being searched. */
    relative(entry: NotePath): string {

        return this.scope
            ? entry.path.slice(this.scope.path.length + 1)
            : entry.path
    }

    /** Draw the rows, folders first; keep the active one if still there. */
    show(entries: NotePath[]): void {

        const activeId = this.rows[this.active]?.id
        this.rows = sorted(entries).slice(0, MAX_ROWS)
        const index = this.rows.findIndex(entry => entry.id === activeId)
        this.active = Math.max(index, 0)

        if (this.rows.length === 0) {
            const empty = document.createElement('li')
            empty.className = 'search-empty'
            const searching = this.titlesOnly ? 'titles' : 'notes'
            empty.textContent = this.els.dialog.classList.contains('searching')
                ? `Searching the ${searching}...`
                : this.els.input.value.trim()
                    ? 'Nothing found'
                    : 'This folder is empty'
            this.els.results.replaceChildren(empty)

            return
        }

        this.els.results.replaceChildren(
            ...this.rows.map((entry, i) => this.row(entry, i)),
        )
    }

    /** One result: icon, name and the folders above it. */
    row(entry: NotePath, index: number): HTMLLIElement {

        const item = document.createElement('li')
        item.role = 'option'
        item.className = 'search-row'
        item.ariaSelected = String(index === this.active)
        item.innerHTML = entry.is_folder ? FOLDER : NOTE

        // textContent, never innerHTML: titles are user text
        const names = this.relative(entry).split('/')
        const name = document.createElement('span')
        name.className = 'search-name'
        name.textContent = names.pop() || 'Untitled'
        const where = document.createElement('span')
        where.className = 'search-where'
        where.textContent = names.join(' / ')
        item.append(name, where)

        // mousedown keeps the focus in the field
        item.addEventListener('mousedown', event => {
            event.preventDefault()
            this.pick(entry)
        })
        item.addEventListener('mousemove', () => this.select(index))

        return item
    }

    /** Mark a row as the one Enter picks, and scroll it into view. */
    select(index: number): void {

        const items = this.els.results.children
        items[this.active]?.setAttribute('aria-selected', 'false')
        this.active = index
        items[index]?.setAttribute('aria-selected', 'true')
        items[index]?.scrollIntoView({ block: 'nearest' })
    }

    /** A folder narrows the search to it; a note opens and closes it. */
    pick(entry: NotePath): void {

        if (entry.is_folder) {
            this.enter(entry)

            return
        }

        const names = entry.path.split('/')
        const title = names.pop() ?? ''
        this.els.dialog.close()
        this.onOpen({
            id: entry.id,
            title,
            folders: names,
            // The title already shows what was found
            words: this.titlesOnly ? [] : terms(this.els.input.value),
        })
    }

    /**
     * Arrows move, Enter picks, Backspace on an empty field goes up,
     * Alt+T switches titles only on and off.
     */
    key(event: KeyboardEvent): void {

        if (event.isComposing) return

        if (event.altKey && event.key.toLowerCase() === 't') {
            event.preventDefault()
            this.mode(!this.titlesOnly)

            return
        }

        const count = this.rows.length

        if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
            event.preventDefault()
            const step = event.key === 'ArrowDown' ? 1 : -1

            if (count) this.select((this.active + step + count) % count)

            return
        }

        if (event.key === 'Enter') {
            event.preventDefault()
            const entry = this.rows[this.active]

            if (entry) this.pick(entry)

            return
        }

        if (event.key === 'Backspace' && !this.els.input.value && this.scope) {
            event.preventDefault()
            this.enter(this.parent(this.scope))
        }
    }

    /** The folder right above an entry; null at the top. */
    parent(entry: NotePath): NotePath | null {

        const path = entry.path.split('/').slice(0, -1).join('/')
        const found = this.entries.find(other => other.path === path)

        return found ?? null
    }
}

/** Folders first, then by path, like the tree. */
function sorted(entries: NotePath[]): NotePath[] {

    return [...entries].sort((a, b) =>
        Number(b.is_folder) - Number(a.is_folder)
        || a.path.localeCompare(b.path))
}

/** Words as the server reads them: no quotes, no -excluded, no "or". */
function terms(query: string): string[] {

    return query.replaceAll('"', '').split(/\s+/).filter(word =>
        word && !word.startsWith('-') && word.toLowerCase() !== 'or')
}

/** A path of titles as the page shows it: "a / b". */
function spaced(path: string): string {

    return path.split('/').join(' / ')
}
