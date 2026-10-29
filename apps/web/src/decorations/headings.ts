import { ViewPlugin, Decoration, EditorView } from '@codemirror/view'


import type { DecorationSet, ViewUpdate } from '@codemirror/view'


// one line decoration per heading level
const h1 = Decoration.line({ class: 'md-h1' })
const h2 = Decoration.line({ class: 'md-h2' })
const h3 = Decoration.line({ class: 'md-h3' })

export const headings = ViewPlugin.fromClass(
    class {
        decorations: DecorationSet

        // calculate when created
        constructor(view: EditorView) {
            this.decorations = this.build(view)
        }

        // recalculate when something changes
        update(u: ViewUpdate) {
            if (u.docChanged || u.viewportChanged) this.decorations =
                            this.build(u.view)
        }

        build(view: EditorView): DecorationSet {
            const decos = []

            // loop over each visible range
            for (const { from, to } of view.visibleRanges) {

                // loop lines in the range
                for (let pos = from; pos <= to; ) {

                    const line = view.state.doc.lineAt(pos)

                    // check if line has # at the beginning, followed by a space
                    const m = /^(#{1,3})\s/.exec(line.text)

                    if (m) {
                        const level = m[1].length
                        const deco = level === 1 ? h1
                            : level === 2 ? h2
                            : h3
                        decos.push(deco.range(line.from))
                    }

                    // jump the whole line
                    pos = line.to + 1
                }
            }
            return Decoration.set(decos)
        }
    },
    { decorations: v => v.decorations }
)
