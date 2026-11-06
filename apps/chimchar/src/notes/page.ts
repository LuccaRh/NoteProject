// Imports
import { createEditor } from '../editor.ts'
import { getNote, updateNote } from './api.ts'

import type { Editor } from '../editor.ts'
import type { Note, NoteUpdate } from './api.ts'
import type { Links } from './links.ts'


// Global variables
type Elements = {
    page: HTMLElement
    empty: HTMLElement
    path: HTMLElement
    status: HTMLElement
    title: HTMLInputElement
    editor: HTMLElement
}

// Pause in typing before the note goes to the server
const SAVE_DELAY_MS = 600

// Wait before trying again when the server did not answer
const RETRY_MS = 3000


// Code
/** The open note: title, body and saving on its own. */
export class Page {
    note: Note | null = null
    path: string[] = []
    // Fields changed since the last save
    dirty: NoteUpdate = {}
    timer: number | undefined = undefined
    // One save at a time, so an old body never arrives last
    saving: Promise<void> = Promise.resolve()
    els: Elements
    editor: Editor
    onSaved: (note: Note) => void

    /** Wire the editor and the title input to the autosave. */
    constructor(
        els: Elements,
        links: Links,
        onSaved: (note: Note) => void,
    ) {

        this.els = els
        this.onSaved = onSaved
        this.editor = createEditor(
            els.editor,
            links,
            body => this.change({ body }),
        )
        els.title.addEventListener('input', () => {
            this.change({ title: els.title.value })
            this.showPath()
        })

        // Enter in the title jumps to the start of the body
        els.title.addEventListener('keydown', event => {

            if (event.key !== 'Enter' || event.isComposing) return

            event.preventDefault()
            this.editor.view.dispatch({
                selection: {
                    anchor: 0,
                },
            })
            this.editor.view.focus()
        })
    }

    /** Save pending edits, then fetch a note and show it. */
    async open(id: string, path: string[]): Promise<void> {

        await this.flush()
        this.show(await getNote(id), path)
    }

    /** Show the server's version of the open note, unless edits wait. */
    async reload(): Promise<void> {

        const saving = this.saving
        await saving

        if (!this.note) return

        const note = await getNote(this.note.id)

        // Typed, or changed note, while fetching: the page stays as it is
        if (this.saving !== saving) return

        if (Object.keys(this.dirty).length > 0) return

        if (note.updated_at !== this.note.updated_at) {
            this.show(note, this.path)
        }
    }

    /** Put a note on the page. */
    show(note: Note, path: string[]): void {

        this.note = note
        this.path = path
        this.dirty = {}
        this.els.title.value = note.title
        this.editor.load(note.body)
        this.showPath()
        this.els.status.textContent = `Saved ${time(note.updated_at)}`
        this.els.page.hidden = false
        this.els.empty.hidden = true
    }

    /** Draw attention to the searched words in the open note. */
    mark(words: string[]): void {

        this.editor.mark(words)
    }

    /** Tell something about the open note where the saves show. */
    say(text: string): void {

        this.els.status.textContent = text
    }

    /** Save pending edits, then hide the note and show the empty page. */
    async close(): Promise<void> {

        const id = this.note?.id
        await this.flush()

        // Another note opened while saving: that one stays
        if (this.note?.id !== id) return

        clearTimeout(this.timer)
        this.note = null
        this.dirty = {}
        this.els.path.textContent = ''
        this.els.status.textContent = ''
        this.els.page.hidden = true
        this.els.empty.hidden = false
    }

    /** Rename from the sidebar while the note is open. */
    rename(title: string): void {

        this.els.title.value = title
        this.change({ title })
        this.showPath()
    }

    /** Mark fields as changed and save after a pause in typing. */
    change(fields: NoteUpdate): void {

        if (!this.note) return

        Object.assign(this.dirty, fields)
        this.els.status.textContent = 'Editing'
        clearTimeout(this.timer)
        this.timer = window.setTimeout(() => void this.flush(), SAVE_DELAY_MS)
    }

    /** Save now, queued after any save already on its way. */
    flush(): Promise<void> {

        clearTimeout(this.timer)
        this.saving = this.saving.then(() => this.save())

        return this.saving
    }

    /**
     * Send the changed fields to the server.
     * Never rejects: a failed save stays in dirty and is tried again.
     */
    async save(): Promise<void> {

        const note = this.note
        const fields = this.dirty

        if (!note || Object.keys(fields).length === 0) return

        this.dirty = {}
        this.els.status.textContent = 'Saving'

        try {
            const saved = await updateNote(note.id, fields)

            if (this.note?.id === saved.id) {
                this.note = saved
                this.els.status.textContent = Object.keys(this.dirty).length
                    ? 'Editing'
                    : `Saved ${time(saved.updated_at)}`
            }

            this.onSaved(saved)
        } catch {

            if (this.note?.id !== note.id) return

            this.dirty = { ...fields, ...this.dirty }
            this.els.status.textContent = 'Not saved, retrying'
            clearTimeout(this.timer)
            this.timer = window.setTimeout(() => void this.flush(), RETRY_MS)
        }
    }

    /** Show the folders and the title of the note on top. */
    showPath(): void {

        const title = this.els.title.value || 'Untitled'
        this.els.path.textContent = [...this.path, title].join(' / ')
    }
}

/** Format an ISO date as "at HH:MM" in local time. */
function time(iso: string): string {

    const at = new Date(iso)

    return 'at ' + at.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
    })
}
