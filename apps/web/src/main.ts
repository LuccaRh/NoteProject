import "./style.css";
import { createEditor } from "./editor";

// Referência ao elemento real do DOM
const container = document.getElementById("editor");

// Altera o elemento diretamente no DOM
const editor = createEditor(container);
console.log(editor);
