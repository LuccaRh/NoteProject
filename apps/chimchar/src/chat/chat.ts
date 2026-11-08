// Imports
import { ask, getConversation, listConversations, Refused } from './api.ts'
import { renderMarkdown } from './markdown.ts'
import { noteId } from '../notes/links.ts'
import { SkillMenu, written } from './slash.ts'

import type { Folder } from '../notes/tree.ts'
import type { Block, Conversation } from './api.ts'


// Global variables
type Options = {
    // Where the panel goes: the work area, next to the note panel
    parent: HTMLElement
    folderId: string | null
    // Folders to pick a workspace from, read each time the list opens
    folders: () => Folder[]
    // Called when the tab should show a new title
    onTitle: (title: string) => void
    // Called after an answer in which the AI wrote to the notes
    onNotesChanged: () => void
    // Opens the note of a link; false when it does not exist
    openNote: (id: string) => Promise<boolean>
}

// Option of the workspace list that asks with no workspace
const NO_WORKSPACE = ''

// How close to the bottom still counts as following the answer
const FOLLOW_PX = 40

// What each tool of the AI does, and what to call its target without a name
const TOOL_STATUS: Record<string, [string, string]> = {
    search_notes: ['Searching', 'the notes'],
    search_titles: ['Searching', 'the titles'],
    list_folder: ['Opening', 'a folder'],
    read_note: ['Reading', 'a note'],
    load_skill: ['Using', 'a skill'],
    create_note: ['Creating', 'a note'],
    create_folder: ['Creating', 'a folder'],
    edit_note: ['Editing', 'a note'],
    delete_note: ['Deleting', 'a note'],
}

// The tools that change the notes
const WRITE_TOOLS = new Set([
    'create_note',
    'create_folder',
    'edit_note',
    'delete_note',
])


// Code
/** One chat tab: a workspace, its conversations and the open one. */
export class Chat {
    folderId: string | null
    conversationId: string | null = null
    // One question at a time per tab
    busy: boolean = false
    // Closes the request of the answer being written
    controller: AbortController | null = null
    // Pieces that arrive before the next frame share one redraw
    frame: number = 0
    options: Options
    panel: HTMLElement
    workspace: HTMLSelectElement
    list: HTMLUListElement
    messages: HTMLElement
    question: HTMLTextAreaElement
    menu: SkillMenu
    send: HTMLButtonElement

    /** Build the panel, wire its controls and load the conversations. */
    constructor(options: Options) {

        this.options = options
        this.folderId = options.folderId
        this.panel = element('section', 'chat-panel')
        this.workspace = element('select', 'chat-workspace')
        this.list = element('ul', 'conversations')
        this.messages = element('div', 'messages')
        this.question = element('textarea', 'question')
        this.menu = new SkillMenu(this.question, () => this.folderId)
        this.send = element('button', 'send')
        this.build()
        options.parent.append(this.panel)
        this.fillWorkspaces()
        void this.loadConversations()
    }

    /** Put the pieces of the panel together and wire their events. */
    build(): void {

        this.workspace.ariaLabel = 'Workspace'
        this.workspace.addEventListener('focus', () => this.fillWorkspaces())
        this.workspace.addEventListener('change', () => {
            this.folderId = this.workspace.value || null
            this.menu.forget()
            this.startConversation()
            void this.loadConversations()
        })

        const fresh = element('button', 'new-conversation')
        fresh.textContent = 'New conversation'
        fresh.addEventListener('click', () => this.startConversation())

        const head = element('header', 'chat-head')
        head.append(this.workspace, fresh)

        const side = element('nav', 'chat-side')
        side.ariaLabel = 'Conversations'
        side.append(this.list)

        this.messages.ariaLive = 'polite'
        this.messages.addEventListener('click', event => this.click(event))
        this.question.rows = 3
        this.question.placeholder = 'Ask something'
        this.question.ariaLabel = 'Question'
        this.send.type = 'submit'
        this.send.textContent = 'Send'

        const form = element('form', 'ask')
        const box = element('div', 'question-box')
        box.append(this.menu.list, this.menu.backdrop, this.question)
        form.append(box, this.send)
        form.addEventListener('submit', event => {
            event.preventDefault()

            if (this.busy) this.controller?.abort()
            else void this.askQuestion()
        })

        // Enter sends, Shift+Enter breaks the line
        this.question.addEventListener('keydown', event => {

            if (this.menu.key(event)) return

            if (event.key !== 'Enter' || event.shiftKey) return

            if (event.isComposing) return

            event.preventDefault()

            if (!this.busy) form.requestSubmit()
        })

        const main = element('div', 'chat-main')
        main.append(this.messages, form)

        const body = element('div', 'chat-body')
        body.append(side, main)
        this.panel.append(head, body)
        this.showEmpty()
    }

    /** Open the note of a clicked link, instead of following the address. */
    click(event: MouseEvent): void {

        const link = (event.target as HTMLElement).closest('a')
        const id = noteId(link?.getAttribute('href') ?? '')

        if (!link || !id) return

        event.preventDefault()
        void this.openLink(link, id)
    }

    /** Open a linked note; a link to nothing turns into plain text. */
    async openLink(link: HTMLAnchorElement, id: string): Promise<void> {

        if (await this.options.openNote(id)) return

        link.replaceWith(`${link.textContent} (note not found)`)
    }

    /** Name of the workspace, for the tab when no conversation is open. */
    workspaceName(): string {

        const folder = this.options.folders()
            .find(f => f.id === this.folderId)

        return folder ? folder.path.split(' / ').at(-1) ?? '' : 'No workspace'
    }

    /** Refill the workspace list from the folders the tree knows. */
    fillWorkspaces(): void {

        const none = new Option('No workspace', NO_WORKSPACE)
        const folders = this.options.folders()
            .map(folder => new Option(folder.path, folder.id))
        this.workspace.replaceChildren(none, ...folders)
        this.workspace.value = this.folderId ?? NO_WORKSPACE
    }

    /** Fetch the conversations of the workspace and redraw the list. */
    async loadConversations(): Promise<void> {

        const folderId = this.folderId
        const conversations = await listConversations(folderId)

        // The workspace changed while the list was coming
        if (this.folderId !== folderId) return

        this.list.replaceChildren(...conversations.map(c => this.row(c)))
        this.markCurrent()
    }

    /** One conversation in the list; a click opens it. */
    row(conversation: Conversation): HTMLLIElement {

        const open = element('button', 'conversation')
        open.textContent = conversation.title
        open.title = conversation.title
        open.dataset.id = conversation.id
        open.addEventListener('click', () => {
            void this.openConversation(conversation.id)
        })

        const item = element('li', 'conversation-row')
        item.append(open)

        return item
    }

    /** Show a saved conversation; the next question goes on in it. */
    async openConversation(id: string): Promise<void> {

        if (this.busy) return

        const conversation = await getConversation(id)
        this.conversationId = id
        this.messages.replaceChildren()

        for (const message of conversation.messages) {
            const content = text(message.content)

            // A turn of tool calls and their results has nothing to show
            if (!content) continue

            const bubble = this.bubble(message.role)

            if (message.role === 'user') bubble.textContent = written(content)
            else bubble.innerHTML = renderMarkdown(content)
        }

        this.scrollToEnd()
        this.options.onTitle(conversation.title)
        this.markCurrent()
    }

    /** Clear the page; the next question starts a new conversation. */
    startConversation(): void {

        if (this.busy) return

        this.conversationId = null
        this.showEmpty()
        this.options.onTitle(this.workspaceName())
        this.markCurrent()
        this.question.focus()
    }

    /** Send the question and write the answer in as it arrives. */
    async askQuestion(): Promise<void> {

        const question = this.question.value.trim()

        if (!question || this.busy) return

        this.busy = true
        this.send.textContent = 'Cancel'
        this.question.value = ''
        this.messages.querySelector('.chat-empty')?.remove()
        this.bubble('user').textContent = question
        const answer = this.bubble('assistant')
        this.scrollToEnd()
        answer.classList.add('streaming')
        const status = element('p', 'chat-status')
        answer.after(status)
        let source = ''
        let wrote = false
        const isNew = this.conversationId === null
        const { signal } = this.controller = new AbortController()

        try {
            await ask(
                {
                    question: await this.menu.expand(question),
                    folder_id: this.folderId,
                    conversation_id: this.conversationId,
                },
                {
                    start: id => {
                        this.conversationId = id
                    },
                    text: piece => {
                        status.textContent = ''
                        source += piece
                        this.frame ||= requestAnimationFrame(() => {
                            this.frame = 0
                            this.show(answer, source)
                        })
                    },
                    tool: (name, target) => {
                        wrote ||= WRITE_TOOLS.has(name)
                        this.follow(() => {
                            status.textContent = toolStatus(name, target)
                        })
                    },
                    error: message => this.fail(answer, message),
                },
                signal,
            )
        } catch (error) {

            if (!signal.aborted) {
                const refused = error instanceof Refused
                const text = 'The chat service did not answer'
                this.fail(answer, refused ? error.message : text)
                console.error(error)
            }
        } finally {
            cancelAnimationFrame(this.frame)
            this.frame = 0
            status.remove()
            this.show(answer, source)
            answer.classList.remove('streaming')

            if (!answer.textContent) answer.remove()

            this.busy = false
            this.send.textContent = 'Send'
        }

        if (wrote) this.options.onNotesChanged()

        if (isNew) this.options.onTitle(question)

        await this.loadConversations()
    }

    /** Redraw the answer so far; keep following it at the bottom. */
    show(answer: HTMLElement, source: string): void {

        this.follow(() => {
            answer.innerHTML = renderMarkdown(source)
        })
    }

    /** Change the page; stay at the bottom if it was following it. */
    follow(change: () => void): void {

        const box = this.messages
        const gap = box.scrollHeight - box.scrollTop - box.clientHeight
        change()

        if (gap < FOLLOW_PX) this.scrollToEnd()
    }

    /** Move the page down to the last message. */
    scrollToEnd(): void {

        this.messages.scrollTop = this.messages.scrollHeight
    }

    /** Show what went wrong under the answer. */
    fail(answer: HTMLElement, message: string): void {

        const note = element('p', 'chat-error')
        note.textContent = message
        answer.after(note)
    }

    /** Add an empty message of one side to the end of the page. */
    bubble(role: 'user' | 'assistant'): HTMLElement {

        const message = element('div', `message ${role}`)
        this.messages.append(message)

        return message
    }

    /** Hint shown while the conversation has no messages yet. */
    showEmpty(): void {

        const hint = element('p', 'chat-empty')
        hint.textContent = 'Ask a question to start a conversation.'
        this.messages.replaceChildren(hint)
    }

    /** Highlight the open conversation in the list. */
    markCurrent(): void {

        const rows = this.list.querySelectorAll<HTMLElement>('.conversation')
        rows.forEach(row => {
            const current = row.dataset.id === this.conversationId
            row.ariaCurrent = current ? 'true' : null
        })
    }
}

/** The status of a tool call, with the name of what it acts on if known. */
function toolStatus(name: string, target: string | null): string {

    const [verb, nameless] = TOOL_STATUS[name] ?? ['Using', 'a tool']

    return `${verb} ${target ? `"${target}"` : nameless}`
}

/** Create an element of a tag with a class. */
function element<K extends keyof HTMLElementTagNameMap>(
    tag: K,
    className: string,
): HTMLElementTagNameMap[K] {

    const el = document.createElement(tag)
    el.className = className

    return el
}

/** The text of a message: its text blocks, one after the other. */
function text(content: Block[]): string {

    return content.map(block => block.text ?? '').join('')
}
