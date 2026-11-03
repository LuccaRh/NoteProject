// Imports
import { StateEffect, StateField } from '@codemirror/state'
import { Decoration, EditorView } from '@codemirror/view'

import { fold } from '../fold.ts'

import type { Text } from '@codemirror/state'
import type { DecorationSet } from '@codemirror/view'


// Global variables
type Range = {
    from: number
    to: number
}

// Carries the ranges of the searched words into the editor state
const setFound = StateEffect.define<Range[]>()

const mark = Decoration.mark({ class: 'cm-found' })

// Letter or digit: a word only matches where one does not come before
const WORD_CHAR = /[\p{L}\p{N}]/u

/** Marks on the searched words; gone at the first edit. */
const marks = StateField.define<DecorationSet>({
    create: () => Decoration.none,
    update(marks, tr) {

        for (const effect of tr.effects) {

            if (!effect.is(setFound)) continue

            const ranges = effect.value.map(r => mark.range(r.from, r.to))

            return Decoration.set(ranges, true)
        }

        return tr.docChanged ? Decoration.none : marks
    },
    provide: field => EditorView.decorations.from(field),
})

// false: the click still moves the cursor
const dismiss = EditorView.domEventHandlers({
    mousedown: (_event, view) => clear(view),
    keydown: (event, view) => event.key === 'Escape' && clear(view),
})

/** The marks, and Esc or a click in the text to take them away. */
export const found = [marks, dismiss]


// Code
/**
 * Mark where the words start a word in the note; the cursor goes to
 * the first, so Esc reaches the editor.
 */
export function showFound(view: EditorView, words: string[]): void {

    const ranges = matches(view.state.doc, words)
    const first = ranges[0]

    if (!first) return

    view.dispatch({
        effects: [
            setFound.of(ranges),
            EditorView.scrollIntoView(first.from, { y: 'center' }),
        ],
        selection: {
            anchor: first.from,
        },
    })
    view.focus()
}

/** Take the marks away; false, so the event goes on as usual. */
function clear(view: EditorView): false {

    if (view.state.field(marks).size > 0) {
        view.dispatch({
            effects: setFound.of([]),
        })
    }

    return false
}

/** Where each word starts a word in the text, ignoring case and accents. */
function matches(doc: Text, words: string[]): Range[] {

    const text = fold(doc.toString())
    const ranges: Range[] = []

    for (const word of words.map(fold)) {
        let from = text.indexOf(word)

        while (from !== -1) {

            if (!WORD_CHAR.test(text[from - 1] ?? '')) {
                ranges.push({
                    from,
                    to: from + word.length,
                })
            }

            from = text.indexOf(word, from + word.length)
        }
    }

    return ranges.sort((a, b) => a.from - b.from)
}
