import './style.css'
import { mountApp } from './ui/app'

const sidebar = document.getElementById('sidebar')
const editor = document.getElementById('editor')
if (!sidebar || !editor) throw new Error('index.html: falta #sidebar ou #editor')

void mountApp(sidebar, editor)
