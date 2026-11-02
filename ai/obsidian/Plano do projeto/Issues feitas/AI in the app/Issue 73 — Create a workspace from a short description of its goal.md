---
tags: [noteproject, plano, ia, servidor]
---
# #73 Create a workspace from a short description of its goal

Issue do [[AI in the app]]: qualquer pasta vira workspace. `POST /api/chat/workspaces {folder_id, description}` faz o `lonzo` pedir ao Haiku 5.5, numa chamada só, o workspace inteiro a partir de um texto da pessoa (o `CLAUDE.md` preenchido e, se o texto pedir, skills, scripts e hooks), e gravar em `.workspace/` dentro da pasta, pela [[API de notas]] do `ichiro`. O `POST /api/chat` ganhou `folder_id` e passa a mandar as regras do workspace no `system`. Versão do `lonzo`: `0.2.0`. Passou por [[Saída estruturada|saída estruturada]], chamada entre serviços na [[Rede de containers|rede do compose]], Python e testes.

## Saída estruturada

- `client.messages.parse(..., output_format=Workspace)` (`anthropic/resources/messages/messages.py:2785`, lib 2.3.0): a classe Pydantic `Workspace` vira JSON Schema, e a volta já vem validada em `message.parsed_output` ([[Saída estruturada]]).
- Uma [[Chamada a um modelo|chamada]], sem [[Laço de ferramentas|laço]]: o modelo não pede nada, só devolve `rules` (o `CLAUDE.md` base preenchido, com os mesmos headings) e as listas `skills`, `scripts` e `hooks` de `Piece {title, body}`, quase sempre vazias.
- (2026-11-02) No começo eram 5 notas, uma por seção (`Skeleton`). Virou uma nota só: a pessoa manda um texto, e as 5 perguntas de ajuda ficam no front.
- O `system` é o prompt (`create_workspace.md`) + o `CLAUDE.md` base (`base_rules.md`), os dois fixos; a data de hoje vai na mensagem, para o `system` não mudar a cada dia ([[Cache de prompt]]).
- `max_tokens` 4096 (regras e skills juntas) e `thinking` desligado, como no chat.

## Chamada entre serviços

- O `lonzo` fala com o `ichiro` direto: `http://ichiro:8000/notes`, pelo nome do serviço na [[Rede de containers|rede do compose]], sem passar pelo [[Reverse proxy|Caddy]] nem pelo `/api`.
- O endereço vem de `ICHIRO_URL` no [[Docker Compose|compose]], com `depends_on: ichiro`.
- Cliente HTTP: `httpx2` 2.16.0, a lib que a `anthropic` já usa (`anthropic/_base_client.py:40`). A `httpx` 0.28.1 também está no venv, só pelo `fastapi-cli`; misturar as duas quebrou o mypy (`Response` de uma não é a da outra).
- `ichiro` fora do ar ou com erro inesperado → `httpx2.HTTPError` → 502 `notes service unavailable` (exception handler no `main.py`).

## Regras no chat

- `system` = notas do `.workspace` da raiz, depois as do `.workspace` da pasta, cada uma com `# <título>`; sem nenhuma, vai sem `system` (`omit`, `anthropic/__init__.py:14`). O `rules.md` da #74 saiu (2026-11-02): ou valem as regras do workspace, ou nenhuma.
- As regras são lidas **antes** do `StreamingResponse`: um erro do `ichiro` ainda sai como status HTTP, não como evento `error` ([[Server-sent events]]).
- Sem uma frase de abertura, o Haiku respondia em inglês a "respostas em português" quando a pergunta vinha em inglês. Com `These notes are the person's workspace... they win over your own defaults`, respondeu em português (conferido em 2026-11-02).

## Organização do código

- Cada API de fora tem um módulo em `lonzo/clients/`: `anthropic.py` (`get_client`, `stream_answer`, `write_workspace`, com o `MODEL` e os `max_tokens`) e `ichiro.py` (`get_ichiro`, `children`, `find_workspace`, `workspace_rules`, `get_note`, `create_note`, `create_workspace_folder`, `create_rules_note`, com o `WORKSPACE` e o `RULES`).
- Os modelos Pydantic ficam em `lonzo/schemas/` (`Note`, `WorkspaceRequest`, `Piece`, `Workspace`), como no `ichiro`; as rotas em `routers/` só usam clientes e schemas.
- Constante não sai do módulo dela: a rota chama `create_workspace_folder(ichiro=..., parent_id=...)`, e é o cliente que usa o `WORKSPACE`. Por isso o `message_start` do chat perdeu o `model`, que foi para o `message_end` (`final.model`).
- Toda chamada a função do serviço passa os argumentos com o nome do parâmetro (`create_note(ichiro=ichiro, title=title, ...)`).
- (2026-11-02) Toda função e classe explica o que faz numa docstring dentro dela, grudada na assinatura e com uma linha em branco antes do código (lint W21 e W14); parâmetros que não cabem numa linha vão um por linha (W20); teste novo em commit próprio.
- Commits pequenos: 13 no app (dependência, cliente da Anthropic, compose, cliente do `ichiro`, chat, 502, testes do 502, testes das regras, schema, `write_workspace`, criar notas, rota, testes, versão).

## API

- `folder_id` obrigatório: workspace na raiz não faz sentido (o `.workspace` da raiz é o que vale para todos).
- Pasta inexistente → 404; nota que não é pasta → 422; pasta que já tem `.workspace` → 409.
- Devolve 201 com tudo o que criou, na ordem: `.workspace`, `CLAUDE.md` e, para cada tipo que veio com algo, a subpasta (`skills`, `scripts`, `hooks`) seguida das notas dela.

## Testes

- `tests/fakes.py`: `FakeIchiro` faz o papel do `ichiro` com um `dict` e um `httpx2.MockTransport`; nenhum teste abre conexão.
- O cliente da Anthropic falso guarda os parâmetros da última chamada, para conferir o `system` e o `output_format`.
- Ponta a ponta com o compose: duas pastas de teste (`Baseball (test 73)`, `Calculus (test 73)`), cada uma com o próprio workspace, e o chat de cada uma seguindo as próprias regras. Depois da troca para uma nota só, `Guitar (test 73)`: "toda semana mando a gravação para revisar" virou a skill `revisar-gravacao` (201 em 5 s). As pastas de teste foram apagadas.

## Notas do vault

- Nova: [[Saída estruturada]].
- [[Workspace no app#Como nasce]]: os passos 2 e 3 com a rota, os nomes das notas e o que já existe.
- Workspace: card `httpx2` e saída estruturada no card `anthropic`; o lint W05 lê o lockfile do serviço do card; regras novas com lint (W18 constante importada, W19 argumento sem nome) e a de `clients/`.
- [[Regras de git]]: commit pequeno, com a #74 de exemplo, e teste em commit próprio.
- [[Workspace no app#Como nasce]]: o `CLAUDE.md` base no lugar das 5 notas e a tabela de como o PC extrai PDF e vídeo para a KB.
