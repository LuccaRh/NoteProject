import {EditorView, basicSetup} from "codemirror";
import {markdown} from "@codemirror/lang-markdown";

// export: libera função para outros arquivos 
export function createEditor(parent: HTMLElement){
    return new EditorView({
        parent,
        doc: "# Olá mundo",
        extensions: [
            basicSetup,
            markdown(),
        ],
    });
}

