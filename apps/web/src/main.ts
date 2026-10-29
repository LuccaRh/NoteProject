// Imports
import './style.css'
import { Tree } from './notes/tree.ts'


// Global variables
const serverStatus = byId<HTMLElement>('server-status')

const tree = new Tree(byId('tree'))


// Code
/** Return the element with this id, or throw if index.html lacks it. */
function byId<T extends HTMLElement>(id: string): T {

    const el = document.getElementById(id)

    if (!el) throw new Error(`index.html: missing #${id}`)

    return el as T
}

// Any request that failed and nobody caught ends up here
window.addEventListener('unhandledrejection', event => {
    serverStatus.textContent = 'Server unreachable'
    console.error(event.reason)
})

void tree.load(null).then(() => {
    serverStatus.textContent = ''
})
