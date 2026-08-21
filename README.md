# Projeto de Notas

App de anotações local-first, seguindo o documento de arquitetura
(`projeto-de-notas-arquitetura-1.pdf`).

Estado atual: **etapa 0** — cliente local, sem rede.
Criar, editar, listar, apagar e buscar notas, com tudo persistindo em SQLite.

```
apps/
  api/    notesd — daemon local em Python. Dono do SQLite (seção 9).
  web/    editor CodeMirror 6 + sidebar. Primeiro cliente do daemon.
```

## Rodar

```bash
make install   # uv sync + npm install
make dev       # daemon em :8787 e Vite em :5173
```

Abra <http://localhost:5173>. `Ctrl+N` cria uma nota; ela salva sozinha
400ms depois da última tecla.

Ou com containers: `docker compose up --build`.

## Verificar

```bash
make check     # ruff + mypy + pytest + tsc + vite build
```

## Onde ficam as notas

Um arquivo SQLite em `~/.local/share/notesd/notes.db` (ou `$NOTESD_DB`).
Conteúdo em Markdown na coluna `content`, busca por `notes_fts` (FTS5).

## Decisões que valem lembrar

- **O id nasce no cliente** (UUIDv7, `apps/web/src/notes/id.ts`). O id local já
  é o definitivo, então a sync da seção 8 não vai precisar de tabela de-para.
- **Nada do caminho crítico espera a rede.** O CodeMirror é a verdade enquanto
  você digita; o PATCH sai com debounce, em segundo plano.
- **O título sai do texto** — primeiro heading do Markdown. Ninguém digita
  título (seção 2: zero decisão de organização na captura).
- **`api.ts` é a única fronteira de rede do front.** Trocar por comandos do
  Tauri, ou por um core em Rust, não mexe em mais nenhum arquivo.

## Próximos passos

Ainda da etapa 0: pastas na sidebar (o back já tem `parent_id` e `is_folder`),
views por parâmetro (`fields`), `Ctrl+P` fuzzy e `Ctrl+Shift+F`.
Depois: servidor (etapa 1) e sync com Yjs/y-py (etapa 2).
