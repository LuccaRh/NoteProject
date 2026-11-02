---
tags: [noteproject, plano]
---
# Issues feitas — mapa

Diário das issues do [[Tarefas no GitHub|GitHub]]: uma página por milestone do [[Roadmap]], com a tabela das issues, e uma página por issue com o que ela entregou e o que ficou aprendido. A página entra quando a primeira issue da milestone começa.

![[o-que-ja-foi-feito.drawio.svg]]
*O projeto em 2026-11-01 por rede (dev): o navegador entra só pelo Caddy em `notes.localhost`, que manda `/api/notes/*` ao `ichiro`, `/api/chat/*` ao `lonzo` (que pergunta à Anthropic) e o resto ao `chimchar`; ✅ entregue, ⏳ em andamento.*

![[caddy-em-producao.drawio.svg]]
*Plano (M3), para comparar: o mesmo caminho na AWS, com domínio real, certificado da Let's Encrypt e o `dist/` no lugar do Vite; o `lonzo` fica fora até o login.*

| Página | Ideia |
|---|---|
| [[M0 Server skeleton]] | tabela das issues da M0, com uma página por issue em `M0 Server skeleton/`: #4 workspace no git, #10 API com `/health`, #11 API no compose, #12 · #13 Postgres e `.env` |
| [[AI in the app]] | tabela das issues da etapa de IA, com uma página por issue em `AI in the app/`: #82 uv alinhado, #74 chat pelo `lonzo`, #73 workspace criado pela IA |
| [[M1 Notes in the browser]] | tabela das issues da M1, com uma página por issue em `M1 Notes in the browser/`: #57 regras de forma nos arquivos antigos, #46 rotas `/notes` |
