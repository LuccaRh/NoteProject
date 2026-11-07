// Code
/** The theme in use, the empty string being the default one. */
export function currentTheme(): string {

    return document.documentElement.dataset.theme ?? ''
}

/** Switch the theme now and keep it in this browser. */
export function chooseTheme({ theme }: { theme: string }): void {

    document.documentElement.dataset.theme = theme
    localStorage.setItem('theme', theme)
}
