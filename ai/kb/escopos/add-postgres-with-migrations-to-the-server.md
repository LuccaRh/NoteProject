---
id: add-postgres-with-migrations-to-the-server
nome: Postgres com migrations e segredos no .env (issues #12 e #13)
areas: [dados, infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Serviço Postgres no `docker-compose-dev.yml`, com volume nomeado: os dados sobrevivem ao `docker compose down`.
2. `.env` fora do git (`git check-ignore -v .env` acha a regra) e `.env.example` com cada variável comentada; o compose lê o `.env` por `env_file` (#13).
3. Ferramenta de migration: Alembic + SQLAlchemy (ok do usuário em 2026-10-22).
4. Migration cria `notes` (`parent_id`, `is_folder`) (Entrega de 2026-10-29). `pedidos` vai para a #31, numa migration própria (2026-10-23). Sem `users` (2026-10-23): entra com o login (M2), numa migration nova com `owner_id`; `fields` e `version` nas issues deles.
5. A API conecta no banco com as variáveis do ambiente; `make check` passa.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- README (como criar o `.env` e subir o banco); `apps/notes/pyproject.toml` (driver e lib de migration).
- Notas `Conceitos/Postgres e migrations`, `Conceitos/Container e Docker Compose`, `Estrutura do projeto/API de notas`.
- Mudanças de md já trazidas para a branch (Features, IP e rede, Entrega de 2026-10-29, Roadmap).

## Fora (vira outra branch)
- Rotas `/notes` e `/search` (#46); sidebar e cliente da API (M1).
- Chave da API do modelo no `.env` (#35, junto do worker).
- Compose de produção, backup do banco (M3); login e tabela de sessões (M2).
