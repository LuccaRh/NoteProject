import { EditorState } from '@codemirror/state'
import { EditorView, basicSetup } from 'codemirror'
import { markdown } from '@codemirror/lang-markdown'
import { headings } from './decorations/headings.ts'

// export: libera função para outros arquivos
export function createEditor(parent: HTMLElement, onChange?: (text: string) => void): EditorView {
  return new EditorView({ parent, state: buildState('', onChange) })
}

/**
 * Troca a nota aberta.
 *
 * `setState` em vez de um `dispatch` que substitui o texto inteiro: o estado
 * novo vem com historico proprio, entao Ctrl+Z numa nota nao desfaz a edicao
 * da nota anterior.
 */
export function setDoc(view: EditorView, doc: string, onChange?: (text: string) => void): void {
  view.setState(buildState(doc, onChange))
}

function buildState(doc: string, onChange?: (text: string) => void): EditorState {
  return EditorState.create({
    doc,
    extensions: [
      basicSetup,
      markdown(),
      EditorView.lineWrapping,
      headings,
      EditorView.updateListener.of(update => {
        if (update.docChanged) onChange?.(update.state.doc.toString())
      }),
    ],
  })
}
