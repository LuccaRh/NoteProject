import { EditorView, minimalSetup } from 'codemirror'
import { EditorState } from '@codemirror/state'
import { markdown } from '@codemirror/lang-markdown'
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language'
import { tags } from '@lezer/highlight'
import { headings } from './decorations/headings.ts'


export type Editor = {
    view: EditorView
    // Replaces the text without calling onChange, with a fresh undo history
    load: (text: string) => void
}

// Markdown colors on the dark page; the # and ** marks stay faint
const highlight = HighlightStyle.define([
    {
        tag: tags.heading,
        color: 'var(--text)',
    },
    {
        tag: tags.strong,
        fontWeight: '600',
        color: 'var(--text)',
    },
    {
        tag: tags.emphasis,
        fontStyle: 'italic',
    },
    {
        tag: tags.strikethrough,
        textDecoration: 'line-through',
    },
    {
        tag: [tags.link, tags.url],
        color: 'var(--muted)',
    },
    {
        tag: tags.monospace,
        fontFamily: 'var(--mono)',
    },
    {
        tag: tags.quote,
        color: 'var(--muted)',
    },
    {
        tag: [tags.processingInstruction, tags.meta],
        color: 'var(--faint)',
    },
])

const theme = EditorView.theme({
    '&': {
        color: 'var(--body)',
        backgroundColor: 'transparent',
    },
    '.cm-content': {
        fontFamily: 'var(--sans)',
        caretColor: 'var(--text)',
        padding: '0',
    },
    '.cm-line': { padding: '0' },
    // Thicker caret, easier to find on the dark page
    '.cm-cursor': {
        borderLeftWidth: '2px',
        borderLeftColor: 'var(--text)',
    },
    '&.cm-focused .cm-selectionBackground, .cm-selectionBackground': {
        backgroundColor: 'var(--selection)',
    },
}, { dark: true })

// export: makes the function available to other files
/** Markdown editor; onChange gets the text on every edit. */
export function createEditor(
    parent: HTMLElement,
    onChange?: (text: string) => void,
): Editor {
    const extensions = [
        minimalSetup,
        markdown(),
        syntaxHighlighting(highlight),
        theme,
        EditorView.lineWrapping,
        headings,
        EditorView.updateListener.of(update => {
            if (update.docChanged) onChange?.(update.state.doc.toString())
        }),
    ]
    const view = new EditorView({
        parent,
        extensions,
    })

    return {
        view,
        load: text => view.setState(
            EditorState.create({
                doc: text,
                extensions,
            }),
        ),
    }
}
