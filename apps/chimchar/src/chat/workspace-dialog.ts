// Imports
import { createWorkspace, Refused } from './api.ts'

import type { Folder } from '../notes/tree.ts'


// Global variables
type Elements = {
    dialog: HTMLDialogElement
    form: HTMLFormElement
    folder: HTMLSelectElement
    description: HTMLTextAreaElement
    status: HTMLElement
    create: HTMLButtonElement
    cancel: HTMLButtonElement
}

// Text the description starts with: each part of a workspace, in order
const TEMPLATE = [
    'This is only a guide: write more than it asks, or delete it all '
        + 'and write your own.',
    '',
    'What this workspace is for:',
    '(e.g. studying calculus for the exam on December 10)',
    '',
    'How the answers should be:',
    '(e.g. short, an example first, in Portuguese)',
    '',
    'Facts that never change:',
    '(e.g. the course follows Stewart, 8th edition)',
    '',
    'Where things stand:',
    '(e.g. done with limits, starting derivatives)',
    '',
    'Sources to use:',
    '(e.g. the notes in the Lectures folder)',
].join('\n')


// Code
/** Pop-up that turns a folder into a workspace from one text. */
export class WorkspaceDialog {
    els: Elements
    folders: () => Folder[]
    onCreated: (folderId: string) => void
    // The AI takes a while; the dialog waits and stays open
    busy: boolean = false

    /** Wire the form; the description starts as the template. */
    constructor(
        els: Elements,
        folders: () => Folder[],
        onCreated: (folderId: string) => void,
    ) {

        this.els = els
        this.folders = folders
        this.onCreated = onCreated
        els.description.value = TEMPLATE
        els.form.addEventListener('submit', event => {
            event.preventDefault()
            void this.create()
        })
        els.cancel.addEventListener('click', () => els.dialog.close())

        // Escape closes the dialog, but not while the AI is writing
        els.dialog.addEventListener('cancel', event => {

            if (this.busy) event.preventDefault()
        })
    }

    /** Open the pop-up with a folder picked (the first one if none). */
    open(folderId: string | null): void {

        const folders = this.folders()
            .map(folder => new Option(folder.path, folder.id))
        this.els.folder.replaceChildren(...folders)

        if (folderId) this.els.folder.value = folderId

        this.els.status.textContent = folders.length
            ? ''
            : 'Create a folder first: a workspace lives in one.'
        this.els.create.disabled = folders.length === 0
        this.els.dialog.showModal()
    }

    /** Send the folder and the text; close once the AI is done. */
    async create(): Promise<void> {

        const folderId = this.els.folder.value
        const description = this.els.description.value.trim()

        if (this.busy || !folderId) return

        if (!description) {
            this.els.status.textContent = 'Write what the workspace is for.'

            return
        }

        this.wait(true)
        this.els.status.textContent = 'The AI is writing the workspace'

        try {
            await createWorkspace(folderId, description)
        } catch (error) {
            const refused = error instanceof Refused
            const text = 'Not created, try again'
            this.els.status.textContent = refused ? error.message : text
            console.error(error)

            return
        } finally {
            this.wait(false)
        }

        this.els.description.value = TEMPLATE
        this.els.dialog.close()
        this.onCreated(folderId)
    }

    /** Lock or unlock the form while the request is on its way. */
    wait(busy: boolean): void {

        this.busy = busy
        this.els.create.disabled = busy
        this.els.cancel.disabled = busy
        this.els.folder.disabled = busy
        this.els.description.readOnly = busy
    }
}
