---
id: lonzo/create-a-workspace-from-a-short-description-of-its-goal
nome: Workspace criado pela IA a partir de um texto breve (issue #73)
areas: [ia, servidor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `POST /api/chat/workspaces {folder_id, description}` (no lonzo, `/chat/workspaces`): uma
   chamada ao modelo, sem laço, com saída estruturada (`messages.parse` + `output_format`
   Pydantic), devolve o workspace inteiro. (2026-11-02, pedido do Lucca) Um texto só da pessoa
   + as subpastas que o `.workspace` já tem → `Workspace {rules, kb, skills, scripts, hooks}`: o
   `CLAUDE.md` e notas de kb, skills, scripts e hooks só quando o texto pede (no lugar das 5
   notas). (2026-11-02) Sem `CLAUDE.md` base: o prompt diz o que as regras cobrem.
2. O lonzo cria a pasta `.workspace` dentro de `folder_id` com as subpastas fixas (`kb/`,
   `skills/`, `scripts/`, `hooks/`) **antes** da chamada ao modelo (2026-11-02); sem rascunho
   válido, apaga o `.workspace` (cascata). Depois grava o `CLAUDE.md` e as notas pelo `POST /notes` do
   ichiro (rede do compose, `http://ichiro:8000`, `httpx2`). Decidido (2026-11-01): `folder_id`
   obrigatório, nada de workspace na raiz; `httpx2` porque é a que a `anthropic` 2.3.0 usa
   (`anthropic/_base_client.py:40`), não a `httpx`.
3. `POST /api/chat {question, folder_id?}`: o `system` passa a ser as notas do `.workspace` da
   raiz + o da pasta; sem nenhum, sem `system` (2026-11-02: saiu o `rules.md` da #74).
4. Testes com cliente da Anthropic e ichiro falsos; versão do lonzo 0.1.0 → 0.2.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `docker-compose-dev.yml`: `ICHIRO_URL` e `depends_on: ichiro` no bloco do lonzo.
- O `system` do chat abre com uma frase (`RULES_HEADER`) dizendo que as notas ganham dos
  padrões do modelo: sem ela, o Haiku respondia em inglês a uma regra "respostas em português"
  (conferido em 2026-11-02).
- Vault: `IA no projeto/Workspace no app#Como nasce`, `Caminho de uma pergunta`.
- (2026-11-02, pedido do Lucca) Chamadas a APIs em `lonzo/clients/` (`anthropic.py` com o
  `MODEL`, `ichiro.py` com o `WORKSPACE`), modelos em `lonzo/schemas/`; nenhuma constante
  importada entre módulos; argumentos sempre com nome; commits pequenos (13 no app).

- (2026-11-02) Empilhada sobre as branches do ichiro (`filter-notes-by-title` →
  `keep-note-titles-unique-inside-a-folder` → `find-a-note-by-its-path` →
  `list-the-notes-inside-a-folder-with-their-paths`): o PR dela só depois dos 4. Usa o
  `?title=` (`find_note`), o `/notes/by-path` (`find_by_path`, pasta de um caminho numa
  chamada) e o 409 do título repetido (vira `ValueError` em `create_note`). O W13 avisa até
  os PRs do ichiro entrarem na `master`.

## Fora (vira outra branch)
- Perguntas guiadas e catálogo de skills prontas (#42). As 5 perguntas de ajuda ficam no front
  (tela de criar workspace); o lonzo só recebe o texto.
- Skill de extrair PDF, imagem e vídeo para a KB: depende de arquivo que não é `.md` no app.
- Scripts e hooks gerados ainda não rodam (v3 do vault, [[Sandbox]]).
- Tela de criar workspace e do chat (#76); conversas no banco (#75).
- Esconder `.workspace` na lista de notas do front.
