// Imports
import { deleteNote, listTree } from '../notes/api.ts'
import {
    addSkill,
    listPublished,
    listWorkspaceSkills,
    publishSkill,
} from './api.ts'

import type { NotePath } from '../notes/api.ts'
import type { PublishedSkill, SkillSource, WorkspaceSkill } from './api.ts'


// Global variables
const WORKSPACE = '.workspace'

type Options = {
    // Where the panel goes: the work area, next to the note panel
    parent: HTMLElement
    openNote: (id: string) => Promise<boolean>
    // Called after a note is created or deleted here
    onNotesChanged: () => void
}

type Workspace = {
    id: string
    path: string
}


// Code
/** A new element with a class and, when given, its text. */
function element<K extends keyof HTMLElementTagNameMap>(
    tag: K,
    className: string,
    text = '',
): HTMLElementTagNameMap[K] {

    const el = document.createElement(tag)
    el.className = className
    el.textContent = text

    return el
}

/** The folders that hold a .workspace, by their path. */
function workspacesOf(entries: NotePath[]): Workspace[] {

    const suffix = `/${WORKSPACE}`
    const folders = new Map(entries.map(entry => [entry.path, entry.id]))
    const paths = entries
        .filter(entry => entry.is_folder && entry.path.endsWith(suffix))
        .map(entry => entry.path.slice(0, -suffix.length))

    return paths.flatMap(path => {
        const id = folders.get(path)

        return id ? [{ id, path }] : []
    })
}

/** Tab with the skills of each workspace and the published ones. */
export class SkillsTab {
    panel: HTMLElement
    options: Options
    workspaces: Workspace[] = []
    selected: Workspace | null = null
    installed: WorkspaceSkill[] = []
    side = element('nav', 'skills-side')
    list = element('ul', 'skills-list')
    published = element('ul', 'skills-list')
    status = element('p', 'skills-status')
    filter = element('select', 'skills-filter')
    heading = element('h2', 'skills-heading', 'Skills')

    /** Build the panel; the data comes each time the tab shows. */
    constructor(options: Options) {

        this.options = options
        this.panel = element('section', 'skills-panel')
        this.panel.hidden = true
        this.filter.append(
            new Option('Everyone', 'everyone'),
            new Option('Mine', 'me'),
        )
        this.filter.setAttribute('aria-label', 'Published by')
        this.filter.addEventListener('change', () => void this.showPublished())
        const main = element('div', 'skills-main')
        const addHead = element('div', 'skills-add-head')
        addHead.append(element('h2', 'skills-heading', 'Add'), this.filter)
        main.append(this.heading, this.list, addHead, this.status)
        main.append(this.published)
        this.panel.append(this.side, main)
        options.parent.append(this.panel)
    }

    /** Read the workspaces again, keeping the one selected. */
    async load(): Promise<void> {

        try {
            this.workspaces = workspacesOf(await listTree())
            const known = this.workspaces.find(
                workspace => workspace.id === this.selected?.id,
            )
            this.selected = known ?? this.workspaces[0] ?? null
            await this.refresh()
        } catch (error) {
            this.status.textContent = 'Server unreachable, try again'
            console.error(error)
        }
    }

    /** Draw everything from the selected workspace. */
    async refresh(): Promise<void> {

        this.drawSide()
        const selected = this.selected
        this.installed = selected
            ? await listWorkspaceSkills(selected.id)
            : []
        this.heading.textContent = selected
            ? `Skills of ${selected.path}`
            : 'Skills'
        this.drawInstalled()
        await this.showPublished()
    }

    /** The list of workspaces on the left. */
    drawSide(): void {

        const items = this.workspaces.map(workspace => {
            const button = element('button', 'skills-workspace', workspace.path)
            button.type = 'button'
            button.classList.toggle(
                'active',
                workspace.id === this.selected?.id,
            )
            button.addEventListener('click', () => {
                this.selected = workspace
                void this.run(() => this.refresh())
            })

            return button
        })
        this.side.replaceChildren(...items)

        if (items.length === 0) {
            this.side.textContent = 'Create a workspace first.'
        }
    }

    /** The skills of the workspace, with what can be done to each. */
    drawInstalled(): void {

        this.list.replaceChildren(
            ...this.installed.map(skill => this.installedItem(skill)),
        )

        if (this.selected && this.installed.length === 0) {
            this.list.append(
                element('li', 'skills-empty', 'No skills here yet.'),
            )
        }
    }

    /** One skill of the workspace: opens, copies, publishes, removes. */
    installedItem(skill: WorkspaceSkill): HTMLElement {

        const item = element('li', 'skill')
        const open = element('button', 'skill-title', skill.title)
        open.type = 'button'
        open.addEventListener('click', () => {
            void this.options.openNote(skill.id)
        })
        const actions = element('div', 'skill-actions')
        actions.append(
            this.copySelect(skill),
            this.button('Publish', () => this.publish(skill)),
            this.button('Remove', () => this.remove(skill)),
        )
        item.append(open, element('p', 'skill-summary', skill.summary), actions)

        return item
    }

    /** A menu with the other workspaces; picking one copies the skill. */
    copySelect(skill: WorkspaceSkill): HTMLElement {

        const select = element('select', 'skill-copy')
        select.setAttribute('aria-label', `Copy ${skill.title} to`)
        select.append(new Option('Copy to', ''))
        const others = this.workspaces.filter(
            workspace => workspace.id !== this.selected?.id,
        )
        select.append(...others.map(other => new Option(other.path, other.id)))
        select.disabled = others.length === 0
        select.addEventListener('change', () => {
            const target = select.value
            select.value = ''

            if (!target) return

            void this.run(() => this.add(target, { note_id: skill.id }))
        })

        return select
    }

    /** A small button that reports its failure on the status line. */
    button(text: string, action: () => Promise<void>): HTMLButtonElement {

        const button = element('button', 'skill-action', text)
        button.type = 'button'
        button.addEventListener('click', () => void this.run(action))

        return button
    }

    /** The published skills, by the filter of the section. */
    async showPublished(): Promise<void> {

        const published = await listPublished(this.filter.value === 'me')
        const titles = new Set(this.installed.map(skill => skill.title))
        const skills = published.filter(skill => !titles.has(skill.title))
        this.published.replaceChildren(
            ...skills.map(skill => this.publishedItem(skill)),
        )

        if (skills.length === 0) {
            this.published.append(
                element('li', 'skills-empty', 'Nothing to add here.'),
            )
        }
    }

    /** One published skill, its text readable before adding it. */
    publishedItem(skill: PublishedSkill): HTMLElement {

        const item = element('li', 'skill')
        const body = element('details', 'skill-body')
        body.append(
            element('summary', '', 'Read the instructions'),
            element('pre', '', skill.body),
        )
        const actions = element('div', 'skill-actions')
        const add = this.button('Add', () => this.addToSelected(skill))
        add.disabled = !this.selected
        actions.append(add)
        item.append(
            element('span', 'skill-title', skill.title),
            element('p', 'skill-summary', skill.summary),
            body,
            actions,
        )

        return item
    }

    /** Copy a published skill to the selected workspace. */
    async addToSelected(skill: PublishedSkill): Promise<void> {

        if (!this.selected) return

        await this.add(this.selected.id, { skill_id: skill.id })
    }

    /** Copy a skill to a workspace and show it. */
    async add(folderId: string, source: SkillSource): Promise<void> {

        await addSkill(folderId, source)
        this.options.onNotesChanged()
        await this.refresh()
        this.status.textContent = 'Skill added'
    }

    /** Publish a skill, or update what it published before. */
    async publish(skill: WorkspaceSkill): Promise<void> {

        await publishSkill(skill.id)
        await this.showPublished()
        this.status.textContent = `${skill.title} published`
    }

    /** Delete the note of a skill, after asking. */
    async remove(skill: WorkspaceSkill): Promise<void> {

        if (!confirm(`Remove ${skill.title} from this workspace?`)) return

        await deleteNote(skill.id)
        this.options.onNotesChanged()
        await this.refresh()
        this.status.textContent = ''
    }

    /** Run an action, showing its failure on the status line. */
    async run(action: () => Promise<void>): Promise<void> {

        this.status.textContent = ''

        try {
            await action()
        } catch (error) {
            this.status.textContent = error instanceof Error
                ? error.message
                : 'Not saved'
            console.error(error)
        }
    }
}
