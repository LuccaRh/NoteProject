// Imports
import {
    autocompletion,
    insertCompletionText,
    pickedCompletion,
} from '@codemirror/autocomplete'

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
}

const OPENER = '[['

const SCHEME = 'note:'


// Code
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

/** Links between notes: [[ lists the notes and writes the link. */
export function noteLinks(links: Links): Extension {

    return autocompletion({
        override: [context => suggest(context, links)],
        icons: false,
    })
}
