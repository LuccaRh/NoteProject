// Imports
import { showGlobe } from '../themes/globe.ts'


// Code
/** The theme in use, the empty string being the default one. */
export function currentTheme(): string {

    return document.documentElement.dataset.theme ?? ''
}

/** Start the moving parts of the theme in use and stop the others. */
export function runTheme(): void {

    showGlobe({ on: currentTheme() === 'liquid' })
}

/** Switch the theme now and keep it in this browser. */
export function chooseTheme({ theme }: { theme: string }): void {

    document.documentElement.dataset.theme = theme
    localStorage.setItem('theme', theme)
    runTheme()
}
