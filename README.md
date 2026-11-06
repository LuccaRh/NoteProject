# NoteProject

A self-hosted notes app with an AI chat that reads and writes your notes. You write Markdown in the browser, keep it in folders on your own server, and ask the chat to find, summarize or create notes for you.

It is a personal project, built to be used every day and to learn systems engineering: servers, authentication, infrastructure and, later, live sync.

**Status:** it runs on one machine with Docker Compose. Deploying to AWS, live edits, a desktop app and a mobile app are planned ([milestones](https://github.com/LuccaRh/NoteProject/milestones)).

## The app

The screenshots use sample notes.

The editor renders Markdown as you type and shows the raw marks only on the line with the cursor.

![The note editor with a table and a code block](docs/images/editor.png)

The chat answers next to your notes. Here it created a note, which appeared in the tree when the answer ended.

![The chat after creating a note](docs/images/chat.png)

The Skills tab lists the skills of each workspace and the ones other people published.

![The Skills tab](docs/images/skills.png)

These screenshots use Minimal dark, the default theme. The settings have seven others, and the browser remembers the choice.

<details>
<summary>Minimal</summary>

![A note in the Minimal theme](docs/images/themes/minimal-note.png)

![The chat in the Minimal theme](docs/images/themes/minimal-chat.png)

![The Skills tab in the Minimal theme](docs/images/themes/minimal-skills.png)

</details>

<details>
<summary>Glass</summary>

![A note in the Glass theme](docs/images/themes/glass-note.png)

![The chat in the Glass theme](docs/images/themes/glass-chat.png)

![The Skills tab in the Glass theme](docs/images/themes/glass-skills.png)

</details>

<details>
<summary>Grid 3D</summary>

![A note in the Grid 3D theme](docs/images/themes/grid-note.png)

![The chat in the Grid 3D theme](docs/images/themes/grid-chat.png)

![The Skills tab in the Grid 3D theme](docs/images/themes/grid-skills.png)

</details>

<details>
<summary>Liquid</summary>

![A note in the Liquid theme](docs/images/themes/liquid-note.png)

![The chat in the Liquid theme](docs/images/themes/liquid-chat.png)

![The Skills tab in the Liquid theme](docs/images/themes/liquid-skills.png)

</details>

<details>
<summary>Nvim</summary>

![A note in the Nvim theme](docs/images/themes/nvim-note.png)

![The chat in the Nvim theme](docs/images/themes/nvim-chat.png)

![The Skills tab in the Nvim theme](docs/images/themes/nvim-skills.png)

</details>

<details>
<summary>Light panels</summary>

![A note in the Light panels theme](docs/images/themes/panels-note.png)

![The chat in the Light panels theme](docs/images/themes/panels-chat.png)

![The Skills tab in the Light panels theme](docs/images/themes/panels-skills.png)

</details>

<details>
<summary>Retrofuturism</summary>

![A note in the Retrofuturism theme](docs/images/themes/retro-note.png)

![The chat in the Retrofuturism theme](docs/images/themes/retro-chat.png)

![The Skills tab in the Retrofuturism theme](docs/images/themes/retro-skills.png)

</details>

## Infrastructure

The drawing shows what is built today. Each service runs in its own container, and the only way in is Caddy.

![Caddy in front of the services, which use Postgres and the Anthropic API](docs/images/infrastructure.png)

| Service | Stack | What it does |
|---|---|---|
| `caddy` | Caddy | Serves HTTPS and sends each path to its service. Before notes and chat, it asks `nujabes` who owns the session cookie. |
| `chimchar` | Vite, TypeScript, CodeMirror 6 | The web app: tree, editor, tabs, chat, skills and settings. |
| `nujabes` | FastAPI | Login, logout and sessions. |
| `ichiro` | FastAPI | Notes and folders, full-text search and title search. |
| `lonzo` | FastAPI, Anthropic SDK | The chat: it talks to the model, runs its note tools through `ichiro`, and keeps conversations, skills and settings. |
| `postgres` | Postgres 18 | One container with one database per service. |

GitHub Actions runs the checks of each service on every pull request and on pushes to `master`.

## Databases

Each service owns its database, so a reference from one to another is only an id, with no foreign key. Row-level security in Postgres keeps each person to their own rows, using the user id that Caddy passes on from `nujabes`.

![The tables of the three databases](docs/images/databases.png)

| Database | Table | What it keeps |
|---|---|---|
| `ichiro` | `notes` | Notes and folders in one tree, with a search index on title and body. |
| `lonzo` | `conversations` | One row per chat, tied to a folder. |
| `lonzo` | `messages` | What the person and the model said, in order, including tool calls. |
| `lonzo` | `skills` | Published skills: a copy of the note taken when publishing. |
| `lonzo` | `settings` | One row per person: Anthropic key (encrypted), model and limits. |
| `nujabes` | `users` | Email and password hash. |
| `nujabes` | `sessions` | Open logins; only the hash of the token is stored. |

Each database also has Alembic's `alembic_version` table, which records the last migration applied.

## Features

**Notes**

- Folders, tabs and autosave.
- Live Markdown preview: headings, tables and code blocks with colors.
- Search by words or title with `Ctrl+O`.
- Links between notes: type `[[` and pick a note.

**Chat**

- Answers arrive as they are written, with Markdown and LaTeX, and a button to cancel.
- A status line shows what the AI is doing.
- Conversations stay on the server, listed by folder.
- Each person brings their own Anthropic key and chooses the model and limits in the settings.

**Workspaces**

A workspace is a folder that has a `.workspace/` folder inside, which is hidden from the tree by default. It gives the AI the context of one subject across conversations. You create one by describing what you want, and the AI writes it:

- `.workspace/CLAUDE.md`: the goal and how to answer, sent with every question asked in that folder.
- `.workspace/kb/`: background notes the AI reads when it needs them.
- `.workspace/skills/`: skills.

**Skills**

A skill is a note with instructions for one task, kept in `.workspace/skills/`. The list of skills goes with each question, and the AI reads a skill when the question fits it. You can also call one by typing `/` and its name in the chat.

In the Skills tab you can copy a skill to another workspace, publish it, or add a skill someone else published. Publishing and adding both make copies, so later edits to one copy do not reach the others.

## How they work together

The chat works on your notes through tools, so it can change them as well as talk about them:

| Tool | What it does |
|---|---|
| `search_notes`, `search_titles` | Find notes by words or by title. |
| `list_folder`, `read_note` | Browse folders and read a note. |
| `create_note`, `create_folder` | Write new notes and folders at a path. |
| `edit_note`, `delete_note` | Change or remove a note. |

The tools reach any of your folders, not only the current one. When the AI writes, the tree and the open note reload at the end of the answer.

For example, with a `Research` folder:

1. You create a workspace from `Research`, describing the subject and how you want answers.
2. You ask the chat in that folder to summarize your notes. The workspace rules go with the question.
3. The AI searches, reads the notes, and creates a summary note, with a link you can click to open it.
4. A task you repeat becomes a skill. You run it with `/summarize-paper`, or publish it for other people.

## The harness

A harness is the program around a model: it builds the request, runs the tools the model asks for, and repeats until the model answers. `lonzo` is a small harness of its own, inspired by Claude Code. The drawing compares the two; the Claude Code side is a general view, not taken from its code.

![lonzo and Claude Code, each with a loop around the Anthropic API](docs/images/harness.png)

Both run the same loop against the Anthropic API: the model returns text or a `tool_use`, the harness runs the tool, and sends back a `tool_result`. The differences are around that loop:

| Part | `lonzo` | Claude Code |
|---|---|---|
| Runs | on the server | on the person's computer |
| Request | `base_rules.md`, date, current folder, `.workspace` notes, list of skills | its system prompt, folder, `CLAUDE.md`, memory, skills |
| Loop | `tool_runner` of the Anthropic SDK, up to `tools_max_turns` | its own |
| Tools | 8 note tools | general tools: files, shell, MCP |
| Checks before a tool runs | none | permissions and hooks can block the call |
| History | in the `lonzo` database, never summarized | in a session file, summarized when it fills up |
| Subagents | none | yes, each with its own loop and context |

`lonzo` can skip permissions because its tools only reach the person's notes. Claude Code reaches the disk and the shell, so each call may need a check first.
