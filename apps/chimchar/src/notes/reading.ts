// Imports
import type { Page } from './page.ts'


// Global variables
const KEY = 'reading'


// Code
/** Make a button switch the notes between writing and reading. */
export function wireReading(
    { button, page }: { button: HTMLElement, page: Page },
): void {

    let reading = localStorage.getItem(KEY) === 'true'

    /** Apply the mode to the page and show it on the button. */
    const show = (): void => {

        page.setReading({ reading })
        button.ariaPressed = String(reading)
        button.ariaLabel = reading ? 'Reading' : 'Writing'
        button.title = button.ariaLabel
    }

    button.addEventListener('click', () => {
        reading = !reading
        localStorage.setItem(KEY, String(reading))
        show()
    })
    show()
}
