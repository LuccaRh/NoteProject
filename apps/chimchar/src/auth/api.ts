// Global variables
// Same origin: Caddy forwards /api/auth to nujabes; the session cookie
// is httpOnly, so this code never sees it, the browser sends it alone
const BASE = '/api/auth'


// Code
/** Whether the browser has an open session (its cookie is valid). */
export async function isLoggedIn(): Promise<boolean> {

    const res = await fetch(BASE + '/session')

    return res.ok
}

/** Log in; false when the email or the password is wrong. */
export async function logIn(email: string, password: string): Promise<boolean> {

    const res = await fetch(BASE + '/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    })

    if (res.status === 401) return false

    if (!res.ok) throw new Error(`POST /login: ${res.status}`)

    return true
}

/** End the session; the server also tells the browser to drop it. */
export async function logOut(): Promise<void> {

    const res = await fetch(BASE + '/logout', { method: 'POST' })

    if (!res.ok) throw new Error(`POST /logout: ${res.status}`)
}
