---
tags: [noteproject, prova]
---
# Perguntas de entrevista

Perguntas prováveis sobre como o NoteProject foi feito, do geral ao detalhe. Tentar responder em voz alta antes de abrir a resposta; o link leva à página do resumo com o detalhe.

## Visão geral

### 1. Explique o projeto em 30 segundos.

> [!note]- Resposta
> App de notas em Markdown com um chat de IA que busca, lê e edita as notas. Quatro serviços em containers: front (Vite + CodeMirror), notas (`ichiro`), IA (`lonzo`) e login (`nujabes`), todos FastAPI com Postgres, atrás de um Caddy que faz HTTPS e confere a sessão. Feito para uso próprio e para aprender servidor, banco, auth e infra ([[Visão geral do NoteProject]]).

### 2. Qual foi a parte mais difícil?

> [!note]- Resposta
> Três boas candidatas: (a) o isolamento por usuário com RLS funcionando com pool de conexões e com a IA passando pela API; (b) o stream do chat, com várias chamadas ao modelo e ferramentas no meio, sem perder o histórico; (c) montar o contexto da IA para o cache de prompt acertar ([[Isolamento por usuário]], [[Chat com IA]], [[Ferramentas e contexto da IA]]).

## Banco

### 3. Como cada usuário só vê as próprias notas?

> [!note]- Resposta
> Row-Level Security no Postgres. A policy compara `owner_id` com `current_setting('app.user_id')`; toda transação começa com `set_config('app.user_id', <id>, true)`. O app conecta com um usuário sem `BYPASSRLS` e a tabela tem `FORCE ROW LEVEL SECURITY` ([[Isolamento por usuário]]).

### 4. O `set_config` não vaza entre pedidos com pool de conexões?

> [!note]- Resposta
> Não: o terceiro argumento `true` faz o valor valer só até o fim da transação. Cada pedido abre a própria transação; quando a conexão volta ao pool, o valor já sumiu ([[Isolamento por usuário]]).

### 5. Como guarda uma árvore de pastas no banco?

> [!note]- Resposta
> Lista de adjacência: cada linha tem `parent_id`. Leituras da árvore (subárvore, caminho, ancestrais) são CTEs `WITH RECURSIVE`, uma ida ao banco. Apagar pasta usa `ON DELETE CASCADE`; mover é mudar uma linha ([[Serviço de notas]]).

### 6. Como funciona a busca?

> [!note]- Resposta
> Full-text do Postgres: `to_tsvector('simple', title || ' ' || body)` com índice GIN na mesma expressão e `websearch_to_tsquery`. Dicionário `simple` porque as notas misturam línguas. Busca por título com `ILIKE` e curingas escapados ([[Serviço de notas]]).

### 7. Por que dois usuários de banco por serviço?

> [!note]- Resposta
> O migrator é dono das tabelas e roda o Alembic; o usuário do app só lê e escreve linhas, sob RLS. Um bug ou injeção no app não consegue mudar esquema nem desligar a policy ([[Isolamento por usuário]]).

### 8. Como os testes usam o banco?

> [!note]- Resposta
> Postgres real. No `ichiro`, cada teste abre uma conexão e cada transação do service vira um savepoint; no fim, rollback. Testam RLS de verdade, conectando como o usuário do app ([[Testes, CI e qualidade]]).

## Auth

### 9. Como funciona o login?

> [!note]- Resposta
> `POST /auth/login` confere a senha (bcrypt via `pgcrypto`), gera token aleatório de 256 bits, guarda o SHA-256 dele numa tabela de sessões e devolve o token em cookie `HttpOnly`, `Secure`, `SameSite=Lax`. Em cada pedido, o Caddy faz `forward_auth` no `nujabes`, que devolve o `X-User-Id` ([[Login e gateway]]).

### 10. Por que guardar o hash do token e não o token?

> [!note]- Resposta
> Se a tabela vazar, ninguém usa os hashes para logar. SHA-256 basta (não precisa bcrypt) porque o token já é aleatório e longo, impossível de adivinhar por força bruta ([[Login e gateway]]).

### 11. Um cliente não pode mandar `X-User-Id` falso?

> [!note]- Resposta
> Do navegador, não: o `copy_headers` do Caddy sobrescreve o cabeçalho com o que veio do `nujabes`. Dentro da rede do compose, sim: os serviços confiam no cabeçalho. Só o Caddy tem porta exposta; a melhoria seria um token assinado pelo gateway ([[Login e gateway]]).

### 12. Sessão no banco ou JWT?

> [!note]- Resposta
> Sessão no banco: logout e revogação imediatos, sem lista negra. Custa uma consulta por pedido, irrelevante aqui. JWT compensaria com muitos serviços validando sem um ponto central ([[Login e gateway]]).

## IA

### 13. Como o chat funciona por dentro?

> [!note]- Resposta
> `POST /api/chat` abre o laço de ferramentas do SDK (`tool_runner(stream=True)`): o modelo pede ferramentas (buscar, ler, editar nota), o `lonzo` chama o `ichiro` por HTTP, devolve o resultado e o modelo continua. Cada evento vira SSE (`text_delta`, `tool_use`, `message_end`). No fim, a conversa com os blocos de ferramenta é salva em JSONB ([[Chat com IA]]).

### 14. Por que SSE e não WebSocket?

> [!note]- Resposta
> Fluxo de mão única por pedido; SSE é HTTP comum, passa pelo proxy sem config e cancelar é fechar a conexão. Como o pedido é `POST`, o front lê com `fetch` + `ReadableStream` em vez de `EventSource` ([[Chat com IA]]).

### 15. O que acontece se a API da Anthropic falhar no meio da resposta?

> [!note]- Resposta
> O 200 já saiu, então o erro vira um evento `error`, e pergunta e turnos não são salvos (numa conversa nova, fica só a conversa vazia). Erros que dá para prever (sem chave, conversa inexistente) são conferidos antes do primeiro evento e viram status HTTP ([[Chat com IA]]).

### 16. Como a IA edita uma nota sem reescrever tudo?

> [!note]- Resposta
> `edit_note(note_id, old_text, new_text)`: o trecho tem de aparecer uma vez só no corpo; ausente ou repetido volta como erro para o modelo mandar mais contexto. Menos tokens e menos risco de estragar o resto ([[Ferramentas e contexto da IA]]).

### 17. Como reduziu custo de tokens?

> [!note]- Resposta
> System fixo e igual para todos, com `cache_control`; o que muda por pergunta (data, pasta, regras) vai num bloco `<context>` na primeira mensagem, para não invalidar o cache. Skills entram como lista e só carregam o corpo por `load_skill`. Limite de turnos e `max_tokens` por usuário ([[Ferramentas e contexto da IA]]).

### 18. A IA consegue ler notas de outro usuário?

> [!note]- Resposta
> Não: as ferramentas chamam o `ichiro` com o `X-User-Id` de quem perguntou (hook do cliente HTTP lendo a `ContextVar`), e o RLS do `ichiro` filtra ([[Isolamento por usuário]]).

### 19. Como guarda a chave da API de cada usuário?

> [!note]- Resposta
> Cifrada com Fernet (AES + HMAC), com a chave de cifra em variável de ambiente fora do banco. Cifra reversível porque o serviço precisa da chave original para chamar a API ([[Chave da API por usuário]]).

### 20. Prompt injection?

> [!note]- Resposta
> Não há defesa completa: texto de uma nota lida entra no contexto. O estrago é limitado ao que as ferramentas permitem: só notas do próprio usuário, sem rede nem execução de código. Desfazer e revisão de edição estão no plano ([[Ferramentas e contexto da IA]]).

## Infra

### 21. Como roda hoje e como vai para produção?

> [!note]- Resposta
> Hoje: Docker Compose no notebook, Caddy com certificado da CA local. Plano: o mesmo compose numa EC2 `t4g.small`, imagens do GHCR publicadas pela CI, Let's Encrypt, Terraform, SSM no lugar de SSH, `pg_dump` para S3 com restore testado ([[Infra hoje e o plano na AWS]]).

### 22. Por que não Kubernetes / ECS?

> [!note]- Resposta
> Uma máquina e cinco containers fixos; orquestrador seria custo e complexidade sem ganho, e esconderia o que se quer aprender. Escalar começaria por Postgres gerenciado e réplicas dos serviços sem estado ([[Infra hoje e o plano na AWS]]).

### 23. Como está o CI?

> [!note]- Resposta
> GitHub Actions, um job por serviço; os jobs Python sobem `postgres:18` como service, rodam o mesmo script de criação do banco do compose e o `make check` (ruff, mypy strict, pytest). A `master` só recebe PR ([[Testes, CI e qualidade]]).

### 24. Como usou IA para desenvolver?

> [!note]- Resposta
> Claude Code com um workspace no repo: regras de arquitetura e estilo viraram lint, hooks de git e do Claude Code, um escopo por branch, commits pequenos e PRs empilhados. Partes de aprendizado (auth, infra) escritas à mão ([[Desenvolvimento com Claude Code]]).

## Trade-offs para citar sem ser perguntado

- RLS em vez de `WHERE` em cada consulta: segurança por padrão, regra menos visível no código.
- IA chamando a API de notas por HTTP: mais latência, mas uma regra de acesso só e a IA vira cliente substituível.
- Sessão no banco em vez de JWT: revogação imediata, uma consulta por pedido.
- Dicionário `simple` na busca: funciona em qualquer língua, sem stemming.
- Limitações conhecidas: sem rate limit no login, sem cadastro, sem desfazer edição da IA, serviços confiam no cabeçalho dentro da rede, ainda não está na AWS.
