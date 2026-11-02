---
tags: [noteproject, plano, servidor, infra]
---
# M0 Server skeleton

Etapa do [[Roadmap]] que põe a [[API de notas]] de pé no PC: projeto Python, [[Docker Compose|compose]], [[Postgres]] e `.env`, sem custo. Cada issue tem uma página com o que entregou e o que ficou aprendido, separado por tópico.

| Issue | Título | Estado | Tópicos |
|---|---|---|---|
| [[Issue 4 — Track the development workspace in git\|#4]] | Track the development workspace in git | ✅ fechada | Git |
| [[Issue 10 — Scaffold the server with a health endpoint\|#10]] | Scaffold the server with a health endpoint | ✅ fechada (PR #50) | FastAPI, Python, testes |
| [[Issue 11 — Run the server in Docker Compose\|#11]] | Run the server in Docker Compose | ✅ fechada (PR #52) | Docker, rede |
| [[Issues 12 e 13 — Postgres com migrations e .env\|#12 · #13]] | Postgres com migrations · `.env` | ✅ fechadas (PR #54) | Postgres, Docker, rede e TCP, Linux, Python, notas do vault |
| #80 | Rename the services to chimchar and ichiro | ✅ PR #81 mergeado | Docker, CI |
| #51 | contexto do build do web | ⏳ aberta | |
