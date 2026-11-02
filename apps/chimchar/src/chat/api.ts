// Imports
import type { Note } from '../notes/api.ts'


// Global variables
// Same origin: Caddy forwards /api/chat to the chat service
const BASE = '/api/chat'

export type Conversation = {
    id: string
    folder_id: string | null
    title: string
    created_at: string
    updated_at: string
}

export type Block = {
    type: string
    text?: string
}

export type Message = {
    id: string
    role: 'user' | 'assistant'
    content: Block[]
    created_at: string
}

export type ConversationWithMessages = Conversation & {
    messages: Message[]
}

export type Question = {
    question: string
    folder_id: string | null
    conversation_id: string | null
}

// What the page does with each server-sent event of an answer
export type AnswerHandlers = {
    start: (conversationId: string) => void
    text: (text: string) => void
    error: (message: string) => void
}


// Code
/** Call the chat API through the /api proxy; throw on error. */
async function request<T>(path: string, init?: RequestInit): Promise<T> {

    const res = await fetch(BASE + path, {
        ...init,
        headers: { 'Content-Type': 'application/json' },
    })

    if (!res.ok) {
        throw new Error(`${init?.method ?? 'GET'} ${path}: ${res.status}`)
    }

    return await res.json() as T
}

/** Conversations of a workspace folder (null = root), newest first. */
export function listConversations(
    folderId: string | null,
): Promise<Conversation[]> {

    return request(`/conversations${folderId ? `?folder_id=${folderId}` : ''}`)
}

/** One conversation with all its messages, in order. */
export function getConversation(
    id: string,
): Promise<ConversationWithMessages> {

    return request(`/conversations/${id}`)
}

/** Turn a folder into a workspace from a description; the AI writes it. */
export function createWorkspace(
    folderId: string,
    description: string,
): Promise<Note[]> {

    return request('/workspaces', {
        method: 'POST',
        body: JSON.stringify({
            folder_id: folderId,
            description,
        }),
    })
}

/**
 * Ask a question and hand each server-sent event to the handlers as it
 * arrives; resolves when the answer ends.
 */
export async function ask(
    question: Question,
    handlers: AnswerHandlers,
): Promise<void> {

    const res = await fetch(BASE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(question),
    })

    if (!res.ok || !res.body) throw new Error(`POST ${BASE}: ${res.status}`)

    const reader = res.body.pipeThrough(new TextDecoderStream()).getReader()
    let buffer = ''

    while (true) {
        const { done, value } = await reader.read()

        if (done) return

        buffer += value
        // A blank line ends an event; the last piece may still be coming
        const events = buffer.split('\n\n')
        buffer = events.pop() ?? ''
        events.forEach(event => dispatch(event, handlers))
    }
}

/** Read one "event: name / data: json" block and call its handler. */
function dispatch(event: string, handlers: AnswerHandlers): void {

    let name = ''
    let data = ''

    for (const line of event.split('\n')) {

        if (line.startsWith('event: ')) name = line.slice(7)

        if (line.startsWith('data: ')) data += line.slice(6)
    }

    const payload = JSON.parse(data || '{}') as Record<string, string>

    if (name === 'message_start') handlers.start(payload.conversation_id)

    if (name === 'text_delta') handlers.text(payload.text)

    if (name === 'error') handlers.error(payload.message)
}
