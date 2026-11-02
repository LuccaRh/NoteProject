---
id: add-note-service-to-docker-compose
nome: API de notas rodando no Docker Compose (issue #11)
areas: [infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Pergunta `fastapi dev` × `fastapi run` (`Estrutura do projeto/API de notas`) respondida antes do Dockerfile.
2. `apps/notes/Dockerfile`: imagem com Python 3.14 + uv, dependências do `uv.lock`, app em `src/`.
3. Serviço `notes` no `docker-compose-dev.yml` (build desse Dockerfile, porta `127.0.0.1:8000`).
4. `docker compose -f docker-compose-dev.yml up --build notes` sobe o servidor e `curl -i localhost:8000/health` devolve 200 `{"status":"ok"}`.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `.dockerignore` em `apps/notes` (`.venv`, caches); README (como subir pelo compose).
- Renomear `docker-compose.yml` → `docker-compose-dev.yml` (produção terá arquivo próprio; pedido do usuário, 2026-10-21).
- Notas `Conceitos/Container e Docker Compose` e `Estrutura do projeto/API de notas`.
- Desenho das redes (loopback, wi-fi, Docker, operadora até o YouTube) na página de rede, como base geral (pedido do usuário, 2026-10-20).

## Fora (vira outra branch)
- Postgres, volume do banco e migrations (#12); `.env` (#13).
- Reverse proxy/TLS (M2); compose de produção na EC2, registry e deploy por merge (M3).
- Mudar o serviço `web` ou o `Dockerfile.dev` dele.
