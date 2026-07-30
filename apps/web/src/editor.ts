import {EditorView, basicSetup} from "codemirror";
import {markdown} from "@codemirror/lang-markdown";
import {headings} from "./decorations/headings.ts";


// export: libera função para outros arquivos
export function createEditor(
    parent: HTMLElement,
    onChange?: (text: string) => void
    ){
    return new EditorView({
        parent,
        doc: "# Olá mundo",
        extensions: [
            basicSetup,
            markdown(),
            EditorView.lineWrapping,
            headings,
            EditorView.updateListener.of((update) => {
                if (update.docChanged) onChange?.(update.state.doc.toString())
            }),
        ],
    });
}

