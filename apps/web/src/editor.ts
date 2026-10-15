import { EditorView, basicSetup } from 'codemirror'
import { markdown } from '@codemirror/lang-markdown'

// export: makes the function available to other files
export function createEditor(parent: HTMLElement, onChange?: (text: string) => void): EditorView {
  return new EditorView({
    parent,
    doc: '# Hello world',
    extensions: [
      basicSetup,
      markdown(),
      EditorView.lineWrapping,
      EditorView.updateListener.of(update => {
        if (update.docChanged) onChange?.(update.state.doc.toString())
      }),
    ],
  })
}
