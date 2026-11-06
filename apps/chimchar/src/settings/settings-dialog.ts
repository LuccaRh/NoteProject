// Imports
import {
    getSettings,
    listModels,
    removeKey,
    saveSettings,
} from './api.ts'
import { chooseTheme, currentTheme } from './theme.ts'

import type {
    ModelOption,
    Settings,
    SettingsUpdate,
    Thinking,
} from './api.ts'


// Global variables
const THINKING_NAMES: Record<Thinking, string> = {
    adaptive: 'On',
    between_tools: 'Off, with progress notes',
    disabled: 'Off',
}

type Elements = {
    dialog: HTMLDialogElement
    form: HTMLFormElement
    apiKey: HTMLInputElement
    keyState: HTMLElement
    removeKey: HTMLButtonElement
    model: HTMLSelectElement
    thinking: HTMLSelectElement
    maxTokens: HTMLInputElement
    toolsMaxTurns: HTMLInputElement
    showWorkspace: HTMLInputElement
    theme: HTMLSelectElement
    status: HTMLElement
    close: HTMLButtonElement
}


// Code
/** Pop-up with the settings of the account. */
export class SettingsDialog {
    els: Elements
    onSaved: (settings: Settings) => void
    models: ModelOption[] = []
    loaded = false

    /** Wire the form; each open reads the settings again. */
    constructor(els: Elements, onSaved: (settings: Settings) => void) {

        this.els = els
        this.onSaved = onSaved
        els.form.addEventListener('change', event => {
            if (event.target !== els.apiKey) void this.save()
        })
        els.apiKey.addEventListener('input', event => {
            const { inputType } = event as InputEvent

            if (inputType === 'insertFromPaste') void this.saveKey()
        })
        els.apiKey.addEventListener('change', () => void this.saveKey())
        els.close.addEventListener('click', () => els.dialog.close())
        els.removeKey.addEventListener('click', () => void this.forgetKey())
        els.model.addEventListener('change', () => {
            this.limitTokens()
            this.limitThinking(els.thinking.value as Thinking)
        })
    }

    /** Show the pop-up; changes save once the settings arrive. */
    async open(): Promise<void> {

        this.els.apiKey.value = ''
        this.els.status.textContent = 'Loading'
        this.loaded = false
        this.els.theme.value = currentTheme()
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
            this.loaded = true
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
        this.els.toolsMaxTurns.value = String(settings.tools_max_turns)
        this.els.showWorkspace.checked = settings.show_workspace
        this.showKey(settings)
        this.limitTokens()
        this.limitThinking(settings.thinking)
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

    /** Offer the thinking of the model picked, the wanted one if it can. */
    limitThinking(wanted: Thinking): void {

        const model = this.models.find(m => m.id === this.els.model.value)
        const kinds = model?.thinking.length ? model.thinking : [wanted]

        this.els.thinking.replaceChildren(
            ...kinds.map(kind => new Option(THINKING_NAMES[kind], kind)),
        )
        this.els.thinking.value = kinds.includes(wanted) ? wanted : kinds[0]
    }

    /** What the form holds; the key only when one was typed. */
    values(): SettingsUpdate {

        const update: SettingsUpdate = {
            model: this.els.model.value,
            max_tokens: Number(this.els.maxTokens.value),
            tools_max_turns: Number(this.els.toolsMaxTurns.value),
            thinking: this.els.thinking.value as Thinking,
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
        }
    }

    /** Save the form as it changes, and say how it went. */
    async save(): Promise<void> {

        if (!this.loaded || this.els.apiKey.disabled) return

        chooseTheme({ theme: this.els.theme.value })

        if (!this.els.form.reportValidity()) return

        this.els.status.textContent = 'Saving'

        try {
            this.onSaved(await saveSettings(this.values()))
            this.els.status.textContent = 'Saved'
        } catch (error) {
            this.els.status.textContent = String((error as Error).message)
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
