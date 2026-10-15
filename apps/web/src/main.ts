import './style.css'
import { createEditor } from './editor'

const editor = document.getElementById('editor')
if (!editor) throw new Error('index.html: missing #editor')

createEditor(editor)
