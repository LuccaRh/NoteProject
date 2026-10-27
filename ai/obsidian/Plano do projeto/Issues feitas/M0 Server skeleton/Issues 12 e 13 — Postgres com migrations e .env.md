---
tags: [noteproject, plano, dados, infra]
---
# #12 Postgres com migrations · #13 `.env`

Issue do [[M0 Server skeleton]]. Põe o banco na [[API de notas]]: Postgres no compose, segredos no `.env`, migration criando a tabela `notes` e a API conectando pela `DATABASE_URL`. Passou por [[Postgres e migrations|Postgres]], Docker, rede e [[TCP e pacotes|TCP]], Linux, Python e as notas do vault.

## Postgres e banco

- O schema é o formato do banco, e a migration é um arquivo versionado que o muda: aplicadas em ordem, levam qualquer banco ao schema atual. A imagem `postgres` só cria usuário e banco com a pasta de dados vazia ([[Postgres e migrations]]).
- O Alembic encadeia as revisões como commits: `upgrade` aplica, `downgrade` reverte, e o `env.py` lê a `DATABASE_URL` ([[Migrations com Alembic]]).
- A engine do SQLAlchemy guarda um pool de conexões abertas e empresta uma por pedido; `engine.begin()` abre a transação ([[SQLAlchemy — engine e conexão]]).
- Pastas dentro de pastas numa tabela plana: cada linha aponta para o pai (`parent_id`, lista de adjacência), e a pasta é uma nota com `is_folder` ([[Árvore no banco]], [[Pastas, campos e views]]).
- Texto da nota fica numa coluna `TEXT` do banco, não num bucket: salvar é um `UPDATE` numa transação e a busca enxerga o conteúdo ([[S3 — armazenamento de objetos]]); a nota é [[Markdown]], texto puro que o editor só decora na tela ([[CodeMirror e decorações]]).

## Docker

- O Docker guarda imagens, containers e volumes numa pasta só por máquina; o volume nomeado `db` vira `noteproject_db` e sobrevive ao `down`, só sai com `down -v` ([[Container e Docker Compose]]).
- `exec` roda um programa no container que já está de pé (`psql`, `alembic upgrade head`); os comandos do dia a dia, com o alias do `-f`, ficam em [[Comandos do Docker no dev]].
- Segredo vai no `.env`, lido pelo compose com `env_file`; a API e o Alembic leem a `DATABASE_URL` dele ([[API de notas]]).

## Rede e TCP

- Dentro do compose o banco é `postgres:5432`, o nome do serviço; do host, `localhost:5432`, publicado só no loopback. O IP vem do DHCP ou é fixo, e cada caixa do desenho é uma rede ([[IP, porta e rede de containers]]).
- A rede só carrega pacotes; a tabela de rotas e o gateway levam cada um à outra rede, e o TCP numera e confirma até virar uma linha de bytes confiável ([[TCP e pacotes]]).

## Linux

- O Linux roda um arquivo pela permissão `x` e pelo formato (ELF ou `#!`), nunca pelo nome: é o que acontece com o `docker-entrypoint.sh` ([[Executar um arquivo no Linux]]).

## Python

- Estrutura `src/`: na plana, o `import` acha o código da pasta atual por acaso; o `uv_build` monta o caminho do package pelas chaves de `[tool.uv.build-backend]` ([[Python — módulo, package e venv]]).

## Notas do vault

- Plano: a [[Entrega de 2026-10-29]] pede notas no navegador e a IA no app antes do login, o que mexeu no [[Roadmap]], no [[00 Mapa — Plano do projeto|mapa do plano]] e nas ideias em [[Features]]. O login virou cookie de sessão (#48) no [[Navegador]] e em [[Back — daemon e servidor]], e o token ficou só para app ([[Token por dispositivo]]); a [[Trilha de infra]] ganhou links para os conceitos de cada etapa.
- Workspace: versão do serviço sobe na branch, num commit só dela ([[Regras de git]]); a skill `/lacunas` e o lint W12 entraram em [[Como usar]]; o [[Esqueleto de tarefas]] pesa o custo de tokens dos subagentes; [[Regras de página]] e [[Regras de resposta]] foram revistas (grafo de links, marcas `[fix]` e `[comment]`).
- Os mapas [[00 Mapa — Conceitos]] e [[00 Mapa — Estrutura do projeto]] ganharam as páginas novas.
