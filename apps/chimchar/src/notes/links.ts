// Imports
import {
    autocompletion,
    insertCompletionText,
    pickedCompletion,
} from '@codemirror/autocomplete'
import { syntaxTree } from '@codemirror/language'
import { EditorView } from '@codemirror/view'
import { touches } from '../decorations/preview.ts'

import type {
    Completion,
    CompletionContext,
    CompletionResult,
} from '@codemirror/autocomplete'
import type { Extension } from '@codemirror/state'
import type { NotePath } from './api.ts'


// Global variables
export type Links = {
    // Everything the person can link to, read when [[ is typed
    entries: () => Promise<NotePath[]>
    // Open the note of a clicked link
    open: (id: string) => void
}

const OPENER = '[['

const SCHEME = 'note:'


// Code
/** Id of the note a link address points to; null for any other link. */
export function noteId(url: string): string | null {

    return url.startsWith(SCHEME) ? url.slice(SCHEME.length) : null
}

/** Keep the brackets of a title from ending the link text. */
function escaped(title: string): string {

    return title.replace(/[\\[\]]/g, '\\$&')
}

/** One line of the list: the title, its folders and the link to write. */
function option(entry: NotePath): Completion {

    const folders = entry.path.split('/')
    const title = folders.pop() || 'Untitled'
    const link = `[${escaped(title)}](${SCHEME}${entry.id})`

    return {
        label: title,
        detail: folders.join('/'),
        apply: (view, completion, from, to) => view.dispatch({
            ...insertCompletionText(
                view.state,
                link,
                from - OPENER.length,
                to,
            ),
            annotations: pickedCompletion.of(completion),
        }),
    }
}

/** Offer the notes after a [[; the words after it filter the list. */
async function suggest(
    context: CompletionContext,
    links: Links,
): Promise<CompletionResult | null> {

    const typed = context.matchBefore(/\[\[[^\]\n]*/)

    if (!typed) return null

    const entries = await links.entries()

    return {
        from: typed.from + OPENER.length,
        options: entries.filter(entry => !entry.is_folder).map(option),
        validFor: /^[^\]\n]*$/,
    }
}

/**
 * Id of the note linked at pos; null outside a note link, or when the
 * cursor is on it: the raw text shows, so a click there edits it.
 */
function linkedNote(view: EditorView, pos: number): string | null {

    let node = syntaxTree(view.state).resolveInner(pos, 1)

    while (node.name !== 'Link') {

        if (!node.parent) return null

        node = node.parent
    }

    const url = node.getChild('URL')

    if (!url || touches(view.state, node.from, node.to)) return null

    return noteId(view.state.sliceDoc(url.from, url.to))
}

/** Open the note under a left click, instead of placing the cursor. */
function click(event: MouseEvent, view: EditorView, links: Links): boolean {

    const onLink = (event.target as HTMLElement).closest('.md-link')
    const pos = view.posAtCoords(event)

    if (event.button !== 0 || !onLink || pos === null) return false

    const id = linkedNote(view, pos)

    if (!id) return false

    event.preventDefault()
    links.open(id)

    return true
}

/** Links between notes: [[ lists the notes, a click follows a link. */
export function noteLinks(links: Links): Extension {

    return [
        autocompletion({
            override: [context => suggest(context, links)],
            icons: false,
        }),
        EditorView.domEventHandlers({
            mousedown: (event, view) => click(event, view, links),
        }),
    ]
}

