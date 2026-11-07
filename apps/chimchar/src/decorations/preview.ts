// Imports
import { StateField } from '@codemirror/state'
import { syntaxTree } from '@codemirror/language'
import { Decoration, EditorView, WidgetType } from '@codemirror/view'

import type { EditorState, Range } from '@codemirror/state'
import type { DecorationSet } from '@codemirror/view'


// Global variables
const hidden = Decoration.replace({})

// Marks hidden only while the cursor is outside their parent node
const INLINE_MARKS = new Set([
    'EmphasisMark',
    'StrikethroughMark',
])


// Code
/** A small dot in place of the "-" of a list item */
class Bullet extends WidgetType {
    /**
     * Same look every time, so the editor keeps the old dot
     */
    eq(): boolean {
        return true
    }

    /**
     * The dot element
     */
    toDOM(): HTMLElement {
        const dot = document.createElement('span')
        dot.className = 'md-bullet'
        dot.textContent = '•'

        return dot
    }
}

/** The language name in place of the opening fence of a code block */
class FenceLabel extends WidgetType {
    label: string

    /**
     * Keeps the language name
     */
    constructor(label: string) {
        super()
        this.label = label
    }

    /**
     * Redraws only when the language changes
     */
    eq(other: FenceLabel): boolean {
        return other.label === this.label
    }

    /**
     * The label element
     */
    toDOM(): HTMLElement {
        const label = document.createElement('span')
        label.className = 'md-fence-label'
        label.textContent = this.label

        return label
    }
}

/** A GFM table drawn as an HTML table; a click puts the cursor back in */
class Table extends WidgetType {
    source: string

    /**
     * Keeps the table text, parsed on draw
     */
    constructor(source: string) {
        super()
        this.source = source
    }

    /**
     * Redraws only when the table text changes
     */
    eq(other: Table): boolean {
        return other.source === this.source
    }

    /**
     * The table element, header first, cells aligned by the delimiter row
     */
    toDOM(view: EditorView): HTMLElement {
        const wrap = document.createElement('div')
        wrap.className = 'md-table'
        const table = document.createElement('table')
        wrap.append(table)
        const [header, delimiter, ...rows] = this.source.split('\n')
        const aligns = splitRow(delimiter ?? '').map(alignOf)

        for (const [index, line] of [header, ...rows].entries()) {
            const tr = table.insertRow()

            for (const [column, text] of splitRow(line).entries()) {
                const cell = document.createElement(index ? 'td' : 'th')
                cell.style.textAlign = aligns[column] ?? ''
                renderInline(text, cell)
                tr.append(cell)
            }
        }

        wrap.addEventListener('mousedown', event => {
            event.preventDefault()
            view.dispatch({ selection: { anchor: view.posAtDOM(wrap) } })
            view.focus()
        })

        return wrap
    }
}

/**
 * Cells of a table row, without the outer pipes; "\|" stays in the cell
 */
function splitRow(line: string): string[] {
    const inner = line.trim().replace(/^\|/, '').replace(/(?<!\\)\|$/, '')

    return inner.split(/(?<!\\)\|/).map(cell => cell.trim())
}

/**
 * Text alignment of a column from its delimiter cell (":--:", "--:")
 */
function alignOf(cell: string): string {
    const left = cell.startsWith(':')
    const right = cell.endsWith(':')

    if (left && right) return 'center'

    return right ? 'right' : ''
}

/**
 * Appends the cell text to parent, with `code`, **bold** and *italic*
 */
function renderInline(text: string, parent: HTMLElement): void {
    const parts = text.replace(/\\\|/g, '|')
        .split(/(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/)

    for (const part of parts) {
        let tag = ''
        let inner = part

        if (part.startsWith('`') && part.length > 1) {
            tag = 'code'
            inner = part.slice(1, -1)
        } else if (part.startsWith('**') && part.length > 3) {
            tag = 'strong'
            inner = part.slice(2, -2)
        } else if (part.startsWith('*') && part.length > 1) {
            tag = 'em'
            inner = part.slice(1, -1)
        }

        if (!tag) {
            parent.append(part)
            continue
        }

        const element = document.createElement(tag)
        element.textContent = inner
        parent.append(element)
    }
}

/**
 * Whether a cursor or selection touches from..to
 */
export function touches(state: EditorState, from: number, to: number): boolean {
    // Reading: no edit will come, so the marks stay hidden everywhere
    if (state.readOnly) return false

    return state.selection.ranges.some(r => r.from <= to && r.to >= from)
}

/**
 * Whether a cursor or selection is on any line of from..to
 */
function onLines(state: EditorState, from: number, to: number): boolean {
    const start = state.doc.lineAt(from).from
    const end = state.doc.lineAt(to).to

    return touches(state, start, end)
}

/**
 * Line classes and hidden marks for the whole note, from the syntax tree
 */
function build(state: EditorState): DecorationSet {
    const decos: Range<Decoration>[] = []
    const doc = state.doc

    /**
     * Adds a line class to every line of from..to
     */
    const lines = (from: number, to: number, name: string): void => {
        const last = doc.lineAt(to).number

        for (let n = doc.lineAt(from).number; n <= last; n++) {
            decos.push(Decoration.line({ class: name }).range(doc.line(n).from))
        }
    }

    /**
     * Hides from..to, plus one space right after it when there is one
     */
    const hide = (from: number, to: number): void => {
        const end = doc.sliceString(to, to + 1) === ' ' ? to + 1 : to

        if (from < end) decos.push(hidden.range(from, end))
    }

    syntaxTree(state).iterate({
        enter: node => {
            const name = node.name
            const parent = node.node.parent
            const heading = /^ATXHeading(\d)$/.exec(name)

            if (heading) {
                lines(node.from, node.to, `md-h${heading[1]}`)

                return
            }

            if (name === 'HeaderMark' && !onLines(state, node.from, node.to)) {
                hide(node.from, node.to)

                return
            }

            if (name === 'Blockquote') {
                lines(node.from, node.to, 'md-quote')

                return
            }

            if (name === 'QuoteMark' && !onLines(state, node.from, node.to)) {
                hide(node.from, node.to)

                return
            }

            if (name === 'InlineCode') {
                decos.push(
                    Decoration.mark({ class: 'md-code' })
                        .range(node.from, node.to),
                )

                return
            }

            if (name === 'CodeMark' && parent?.name === 'InlineCode') {

                if (!touches(state, parent.from, parent.to)) {
                    decos.push(hidden.range(node.from, node.to))
                }

                return
            }

            if (INLINE_MARKS.has(name) && parent) {

                if (!touches(state, parent.from, parent.to)) {
                    decos.push(hidden.range(node.from, node.to))
                }

                return
            }

            if (name === 'Link') {
                decos.push(
                    Decoration.mark({ class: 'md-link' })
                        .range(node.from, node.to),
                )

                return
            }

            const inLink = parent?.name === 'Link'
            const linkPart = ['LinkMark', 'URL', 'LinkTitle'].includes(name)

            if (inLink && linkPart && parent) {

                if (!touches(state, parent.from, parent.to)) {
                    decos.push(hidden.range(node.from, node.to))
                }

                return
            }

            const bullet = parent?.parent?.name === 'BulletList'

            if (name === 'ListMark' && bullet) {

                if (!onLines(state, node.from, node.to)) {
                    const widget = Decoration.replace({ widget: new Bullet() })
                    decos.push(widget.range(node.from, node.to))
                }

                return
            }

            if (name === 'HorizontalRule') {

                if (!onLines(state, node.from, node.to)) {
                    lines(node.from, node.to, 'md-hr')
                    decos.push(hidden.range(node.from, node.to))
                }

                return
            }

            if (name === 'FencedCode') {
                fencedCode(node.from, node.to)

                return false
            }

            if (name === 'Table') {
                table(node.from, node.to)

                return false
            }
        },
    })

    /**
     * Box around a code block; fences hidden while the cursor is outside
     */
    function fencedCode(from: number, to: number): void {
        const first = doc.lineAt(from)
        const last = doc.lineAt(to)
        lines(from, to, 'md-codeblock')
        decos.push(Decoration.line({ class: 'md-codeblock-first' })
            .range(first.from))
        decos.push(Decoration.line({ class: 'md-codeblock-last' })
            .range(last.from))

        if (onLines(state, from, to)) return

        const info = first.text.replace(/^\s*(`{3,}|~{3,})/, '').trim()
        const label = Decoration.replace({ widget: new FenceLabel(info) })
        decos.push(label.range(first.from, first.to))
        const closed = /^\s*(`{3,}|~{3,})\s*$/.test(last.text)

        if (closed && last.number > first.number) {
            decos.push(hidden.range(last.from, last.to))
        }
    }

    /**
     * The table as a widget, or monospace lines while the cursor is in it
     */
    function table(from: number, to: number): void {
        const start = doc.lineAt(from).from
        const end = doc.lineAt(to).to

        if (onLines(state, from, to)) {
            lines(from, to, 'md-table-source')

            return
        }

        const widget = new Table(doc.sliceString(start, end))
        const deco = Decoration.replace({ widget, block: true })
        decos.push(deco.range(start, end))
    }

    return Decoration.set(decos, true)
}

/** Markdown drawn as it reads: marks show only where the cursor is */
export const preview = StateField.define<DecorationSet>({
    create: build,
    update(decos, tr) {
        const parsed = syntaxTree(tr.state) !== syntaxTree(tr.startState)

        if (tr.docChanged || tr.selection || tr.reconfigured || parsed) {
            return build(tr.state)
        }

        return decos
    },
    provide: field => EditorView.decorations.from(field),
})
