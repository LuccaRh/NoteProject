// Imports
import 'katex/dist/katex.min.css'
import DOMPurify from 'dompurify'
import katex from 'katex'
import { Marked } from 'marked'

import type { Tokens } from 'marked'


// Global variables
// $$formula$$, which may span lines
const DISPLAY_MATH = /^\$\$((?:\\[^]|[^$\\])+)\$\$/

// $formula$: no space inside the dollars, no digit after, so R$ 10 stays
const INLINE_MATH = /^\$(?=\S)((?:\\.|[^$\\\n])+)(?<=\S)\$(?!\d)/

const marked = new Marked({
    breaks: true,
    extensions: [{
        name: 'math',
        level: 'inline',
        start: source => source.indexOf('$'),
        tokenizer: readMath,
        renderer: drawMath,
    }],
})


// Code
/** Read the formula at the start of the text, if there is one. */
function readMath(source: string): Tokens.Generic | undefined {

    const display = DISPLAY_MATH.exec(source)
    const match = display ?? INLINE_MATH.exec(source)

    if (!match) return undefined

    return {
        type: 'math',
        raw: match[0],
        text: match[1],
        display: display !== null,
    }
}

/** Draw a formula; a broken one shows as red text and stops nothing. */
function drawMath(token: Tokens.Generic): string {

    return katex.renderToString(token.text, {
        displayMode: token.display,
        throwOnError: false,
    })
}

/**
 * Turn the Markdown of an answer into HTML that is safe to show; no
 * images, since loading one could send note text to another site.
 */
export function renderMarkdown(source: string): string {

    const html = marked.parse(source, { async: false })

    return DOMPurify.sanitize(html, { FORBID_TAGS: ['img'] })
}
