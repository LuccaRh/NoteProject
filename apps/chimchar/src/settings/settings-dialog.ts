// Imports
import {
    getSettings,
    listModels,
    removeKey,
    saveSettings,
} from './api.ts'

import type { ModelOption, Settings, SettingsUpdate } from './api.ts'


// Global variables
type Elements = {
    dialog: HTMLDialogElement
    form: HTMLFormElement
    apiKey: HTMLInputElement
    keyState: HTMLElement
    removeKey: HTMLButtonElement
    model: HTMLSelectElement
    maxTokens: HTMLInputElement
    showWorkspace: HTMLInputElement
    status: HTMLElement
    save: HTMLButtonElement
    cancel: HTMLButtonElement
}


// Code
/** Pop-up with the settings of the account. */
export class SettingsDialog {
    els: Elements
    onSaved: (settings: Settings) => void
    models: ModelOption[] = []

    /** Wire the form; each open reads the settings again. */
    constructor(els: Elements, onSaved: (settings: Settings) => void) {

        this.els = els
        this.onSaved = onSaved
        els.form.addEventListener('submit', event => {
            event.preventDefault()
            void this.save()
        })
        els.apiKey.addEventListener('input', event => {
            const { inputType } = event as InputEvent

            if (inputType === 'insertFromPaste') void this.saveKey()
        })
        els.apiKey.addEventListener('change', () => void this.saveKey())
        els.cancel.addEventListener('click', () => els.dialog.close())
        els.removeKey.addEventListener('click', () => void this.forgetKey())
        els.model.addEventListener('change', () => this.limitTokens())
    }

    /** Show the pop-up, ready to save once the settings arrive. */
    async open(): Promise<void> {

        this.els.apiKey.value = ''
        this.els.status.textContent = 'Loading'
        this.els.save.disabled = true
        this.els.dialog.showModal()

        try {
            // Without the models, the settings can still be read and saved
            const [settings, models] = await Promise.all([
                getSettings(),
                listModels().catch(() => []),
            ])
            this.models = models
            this.fill(settings)
            this.els.status.textContent = ''
            this.els.save.disabled = false
        } catch (error) {
            this.els.status.textContent = 'Server unreachable, try again'
            console.error(error)
        }
    }

    /** Put the saved settings in the form. */
    fill(settings: Settings): void {

        const models = this.models
            .map(model => new Option(model.name, model.id))

        // The saved model stays in the list even with the models unknown
        if (!this.models.some(model => model.id === settings.model)) {
            models.unshift(new Option(settings.model, settings.model))
        }

        this.els.model.replaceChildren(...models)
        this.els.model.value = settings.model
        this.els.maxTokens.value = String(settings.max_tokens)
        this.els.showWorkspace.checked = settings.show_workspace
        this.showKey(settings)
        this.limitTokens()
    }

    /** Say which key is saved, never the key itself. */
    showKey(settings: Settings): void {

        this.els.keyState.textContent = settings.has_key
            ? `Saved key ending in ${settings.key_end}`
            : 'No key saved'
        this.els.removeKey.hidden = !settings.has_key
    }

    /** Keep the tokens under the limit of the model picked. */
    limitTokens(): void {

        const model = this.models.find(m => m.id === this.els.model.value)
        const limit = model?.max_tokens

        this.els.maxTokens.max = limit ? String(limit) : ''

        if (limit && Number(this.els.maxTokens.value) > limit) {
            this.els.maxTokens.value = String(limit)
        }
    }

    /** What the form holds; the key only when one was typed. */
    values(): SettingsUpdate {

        const update: SettingsUpdate = {
            model: this.els.model.value,
            max_tokens: Number(this.els.maxTokens.value),
            show_workspace: this.els.showWorkspace.checked,
        }
        const apiKey = this.els.apiKey.value.trim()

        if (apiKey) update.api_key = apiKey

        return update
    }

    /** Save a new key and show its models, with the pop-up still open. */
    async saveKey(): Promise<void> {

        const update = this.values()

        if (!update.api_key || this.els.apiKey.disabled) return

        this.els.apiKey.disabled = true
        this.els.save.disabled = true
        this.els.status.textContent = 'Checking the key'

        try {
            const settings = await saveSettings(update)
            this.models = await listModels()
            this.els.apiKey.value = ''
            this.fill(settings)
            this.onSaved(settings)
            this.els.status.textContent = ''
        } catch (error) {
            this.els.status.textContent = String((error as Error).message)
        } finally {
            this.els.apiKey.disabled = false
            this.els.save.disabled = false
        }
    }

    /** Save the form; close on success, say why if not. */
    async save(): Promise<void> {

        const update = this.values()
        const apiKey = update.api_key

        this.els.save.disabled = true
        this.els.status.textContent = apiKey ? 'Checking the key' : ''

        try {
            const settings = await saveSettings(update)
            this.els.apiKey.value = ''
            this.els.dialog.close()
            this.onSaved(settings)
        } catch (error) {
            this.els.status.textContent = String((error as Error).message)
        } finally {
            this.els.save.disabled = false
        }
    }

    /** Ask, then forget the saved key. */
    async forgetKey(): Promise<void> {

        if (!confirm('Remove the saved key?')) return

        try {
            await removeKey()
            this.showKey(await getSettings())
            this.els.status.textContent = ''
        } catch (error) {
            this.els.status.textContent = String((error as Error).message)
        }
    }
}
