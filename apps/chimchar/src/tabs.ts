// Global variables
export type Tab = {
    // A note tab uses the note id, so the same note never opens twice
    id: string
    kind: 'note' | 'chat'
    title: string
    panel: HTMLElement
    // Called each time the tab comes to the front
    show?: () => Promise<void> | void
    // Called before the tab goes away for good
    close?: () => void
}

const CROSS = '<svg aria-hidden="true" width="12" height="12"'
    + ' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    + ' stroke-width="2.2" stroke-linecap="round">'
    + '<path d="M6 6l12 12M18 6L6 18"/></svg>'


// Code
/** Bar of open tabs; only the panel of the active one shows. */
export class Tabs {
    tabs: Tab[] = []
    active: Tab | null = null
    bar: HTMLElement
    // Shown while no tab is open
    home: HTMLElement
    onEmpty: () => void

    /** Keep the bar, the panel shown with no tabs and what to do then. */
    constructor(bar: HTMLElement, home: HTMLElement, onEmpty: () => void) {

        this.bar = bar
        this.home = home
        this.onEmpty = onEmpty
    }

    /** Bring a tab to the front, adding it first when it is new. */
    open(tab: Tab): Promise<void> {

        const known = this.tabs.find(t => t.id === tab.id)

        if (!known) this.tabs.push(tab)

        return this.activate(known ?? tab)
    }

    /** Show a tab's panel and hide the others; resolves once it shows. */
    async activate(tab: Tab): Promise<void> {

        const changed = this.active !== tab
        this.active = tab
        this.showPanels()
        this.render()

        if (changed) await tab.show?.()
    }

    /** Remove a tab; the one next to it comes to the front. */
    close(tab: Tab): void {

        const index = this.tabs.indexOf(tab)

        if (index === -1) return

        tab.close?.()
        this.tabs.splice(index, 1)

        if (this.active !== tab) {
            this.render()

            return
        }

        const next = this.tabs[index] ?? this.tabs[index - 1]

        if (next) {
            void this.activate(next)

            return
        }

        this.active = null
        this.showPanels()
        this.render()
        this.onEmpty()
    }

    /** Close every tab the test picks. */
    closeWhere(test: (tab: Tab) => boolean): void {

        this.tabs.filter(test).forEach(tab => this.close(tab))
    }

    /** Change the title shown on a tab. */
    rename(id: string, title: string): void {

        const tab = this.tabs.find(t => t.id === id)

        if (!tab) return

        tab.title = title
        this.render()
    }

    /** Unhide only the active panel, or home with no tab open. */
    showPanels(): void {

        const shown = this.active?.panel ?? this.home
        const panels = new Set([this.home, ...this.tabs.map(t => t.panel)])
        panels.forEach(panel => {
            panel.hidden = panel !== shown
        })
    }

    /** Redraw the bar: one button per tab, with its close button. */
    render(): void {

        this.bar.hidden = this.tabs.length === 0
        this.bar.replaceChildren(...this.tabs.map(tab => this.button(tab)))
    }

    /** Build the button of one tab; middle click also closes it. */
    button(tab: Tab): HTMLElement {

        const item = document.createElement('div')
        item.className = `tab ${tab.kind}`
        item.role = 'tab'
        item.ariaSelected = String(tab === this.active)

        // textContent, never innerHTML: the title is user text
        const open = document.createElement('button')
        open.className = 'tab-open'
        open.textContent = tab.title || 'Untitled'
        open.title = tab.title
        open.addEventListener('click', () => void this.activate(tab))

        const close = document.createElement('button')
        close.className = 'tab-close'
        close.ariaLabel = `Close ${tab.title}`
        close.innerHTML = CROSS
        close.addEventListener('click', () => this.close(tab))

        item.addEventListener('auxclick', event => {

            if (event.button === 1) this.close(tab)
        })
        item.append(open, close)

        return item
    }
}
