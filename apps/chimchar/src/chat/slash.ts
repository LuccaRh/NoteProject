// Imports
import { getNote } from '../notes/api.ts'
import { listWorkspaceSkills } from '../skills/api.ts'

import type { WorkspaceSkill } from '../skills/api.ts'


// Global variables
// Between what the person wrote and the text of the skill in a message
const SKILL_START = '\n\n<skill>\n'
const SKILL_END = '\n</skill>'


// Code
/** What the person wrote in a message, without the text of its skill. */
export function written(message: string): string {

    return message.split(SKILL_START, 1)[0] ?? ''
}

/** Whether a question calls a skill: /title, then nothing or a space. */
function calls(question: string, skill: WorkspaceSkill): boolean {

    const name = `/${skill.title}`

    if (!question.startsWith(name)) return false

    return /^(\s|$)/.test(question.slice(name.length))
}

/** List of the workspace's skills, opened by a / in the question. */
export class SkillMenu {
    input: HTMLTextAreaElement
    folderId: () => string | null
    list: HTMLUListElement
    // Asked once per /, so a skill added meanwhile shows up the next time
    skills: Promise<WorkspaceSkill[]> | null = null
    shown: WorkspaceSkill[] = []
    active: number = 0
    // Esc closes the list until the / is gone
    closed: boolean = false

    /** Build the empty list and follow what is typed in the input. */
    constructor(input: HTMLTextAreaElement, folderId: () => string | null) {

        this.input = input
        this.folderId = folderId
        this.list = document.createElement('ul')
        this.list.className = 'skill-menu'
        this.list.hidden = true
        this.list.ariaLabel = 'Skills'
        // Keeps the focus in the question when a skill is clicked
        this.list.addEventListener('mousedown', e => e.preventDefault())
        input.addEventListener('input', () => void this.update())
    }

    /** The skills of the conversation's workspace; none if they fail. */
    load(): Promise<WorkspaceSkill[]> {

        const folderId = this.folderId()

        if (folderId === null) return Promise.resolve([])

        this.skills ??= listWorkspaceSkills(folderId).catch(() => [])

        return this.skills
    }

    /** Forget the skills and close the list: the workspace changed. */
    forget(): void {

        this.skills = null
        this.closed = false
        this.show([])
    }

    /** Filter the list by what follows the /. */
    async update(): Promise<void> {

        const typed = this.input.value

        if (!typed.startsWith('/')) {
            this.forget()

            return
        }

        const skills = await this.load()

        // More was typed while the skills were coming
        if (this.input.value !== typed) return

        const query = typed.slice(1).toLowerCase()
        const found = skills
            .filter(skill => skill.title.toLowerCase().includes(query))
        this.show(this.closed ? [] : found)
    }

    /** Show these skills with the first one marked. */
    show(skills: WorkspaceSkill[]): void {

        this.shown = skills
        this.active = 0
        this.draw()
    }

    /** Redraw the list and keep the marked skill in view. */
    draw(): void {

        const rows = this.shown.map((skill, index) => {
            return this.row(skill, index === this.active)
        })
        this.list.replaceChildren(...rows)
        this.list.hidden = rows.length === 0
        rows[this.active]?.scrollIntoView({ block: 'nearest' })
    }

    /** One skill of the list; a click picks it. */
    row(skill: WorkspaceSkill, active: boolean): HTMLLIElement {

        const title = document.createElement('span')
        title.className = 'skill-menu-title'
        title.textContent = `/${skill.title}`

        const summary = document.createElement('span')
        summary.className = 'skill-menu-summary'
        summary.textContent = skill.summary

        const row = document.createElement('li')
        row.className = 'skill-menu-row'
        row.classList.toggle('active', active)
        row.append(title, summary)
        row.addEventListener('click', () => this.pick(skill))

        return row
    }

    /** Put the name of a skill in the question, ready for the rest. */
    pick(skill: WorkspaceSkill): void {

        this.input.value = `/${skill.title} `
        this.show([])
    }

    /** Handle a key while the list is open; false if it isn't for it. */
    key(event: KeyboardEvent): boolean {

        const count = this.shown.length
        const skill = this.shown[this.active]

        if (!skill || event.isComposing) return false

        if (event.key === 'ArrowDown') this.move(1, count)
        else if (event.key === 'ArrowUp') this.move(count - 1, count)
        else if (event.key === 'Tab') this.pick(skill)
        else if (event.key === 'Enter' && !event.shiftKey) this.pick(skill)
        else if (event.key === 'Escape') this.close()
        else return false

        event.preventDefault()

        return true
    }

    /** Mark another skill, going around at the ends. */
    move(step: number, count: number): void {

        this.active = (this.active + step) % count
        this.draw()
    }

    /** Hide the list until the / is gone. */
    close(): void {

        this.closed = true
        this.show([])
    }

    /** The message to send: the question and the text of its skill. */
    async expand(question: string): Promise<string> {

        if (!question.startsWith('/')) return question

        // The longest first: /a must not win over /a b
        const skills = [...await this.load()]
            .sort((a, b) => b.title.length - a.title.length)
        const skill = skills.find(s => calls(question, s))
        this.forget()

        if (!skill) return question

        // A skill just deleted goes as plain text: the question still counts
        const note = await getNote(skill.id).catch(() => null)

        if (!note) return question

        return `${question}${SKILL_START}${note.body}${SKILL_END}`
    }
}
