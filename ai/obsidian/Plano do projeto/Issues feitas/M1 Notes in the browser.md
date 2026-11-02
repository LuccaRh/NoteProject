---
tags: [noteproject, plano, servidor, dados]
---
# M1 Notes in the browser

Etapa do [[Roadmap]] que leva as notas do [[Postgres]] ao navegador: rotas `/notes` na [[API de notas]], o [[Navegador|front]] lendo e editando por elas, e depois pastas, campos e views. Cada issue tem uma página com o que entregou, separado por tópico.

| Issue | Título | Estado | Tópicos |
|---|---|---|---|
| [[Issue 57 — Apply the import and typing rules to the old notes files\|#57]] | Apply the import and typing rules to the old notes files | ✅ PR #58 mergeado | Python, regras de forma |
| [[Issue 46 — Expose the notes API on the server\|#46]] | Expose the notes API on the server | ✅ PR #59 mergeado | [[FastAPI]], Postgres, testes |
| #62 | List, create and edit notes in the editor through the API | ✅ mergeado | front, [[API de notas]] |
| #64 | Proxy API requests from the Vite dev server to the notes service | ✅ fechada | [[Proxy de desenvolvimento]] |
| #65 · #69 | Indent the web code and the dev compose file with 4 spaces | ✅ fechadas | regras de forma |
| #16 | Put Caddy with local TLS in front of the server | ✅ fechada | [[Reverse proxy]], [[TLS]] |
| #56 | Search notes with Postgres full-text search | ⏳ aberta | Postgres |
