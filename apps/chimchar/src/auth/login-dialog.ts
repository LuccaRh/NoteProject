// Imports
import { logIn } from './api.ts'


// Global variables
type Elements = {
    dialog: HTMLDialogElement
    form: HTMLFormElement
    email: HTMLInputElement
    password: HTMLInputElement
    status: HTMLElement
    submit: HTMLButtonElement
}


// Code
/** Pop-up with email and password, open until the login works. */
export class LoginDialog {
    els: Elements
    // Resolves the promise of open() once the login works
    done: () => void = () => {}

    /** Wire the form; Escape never closes it, there is nothing behind. */
    constructor(els: Elements) {

        this.els = els
        els.form.addEventListener('submit', event => {
            event.preventDefault()
            void this.submit()
        })
        els.form.addEventListener('input', () => this.updateSubmit())
        els.dialog.addEventListener('cancel', event => event.preventDefault())
    }

    /** Show the pop-up; resolves when the user is logged in. */
    open(): Promise<void> {

        this.els.status.textContent = ''
        this.updateSubmit()
        this.els.dialog.showModal()
        this.els.email.focus()

        return new Promise(resolve => {
            this.done = resolve
        })
    }

    /** Let the button work only with a valid email and a password. */
    updateSubmit(): void {

        this.els.submit.disabled = !this.els.form.checkValidity()
    }

    /** Send email and password; close on success, say why if not. */
    async submit(): Promise<void> {

        this.els.submit.disabled = true
        this.els.status.textContent = ''

        try {
            const ok = await logIn(
                this.els.email.value,
                this.els.password.value,
            )

            if (!ok) {
                this.els.status.textContent = 'Wrong email or password'
                this.els.password.select()

                return
            }
        } catch (error) {
            this.els.status.textContent = 'Server unreachable, try again'
            console.error(error)

            return
        } finally {
            this.updateSubmit()
        }

        this.els.password.value = ''
        this.els.dialog.close()
        this.done()
    }
}
