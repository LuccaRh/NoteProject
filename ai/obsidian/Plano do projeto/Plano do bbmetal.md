---
tags: [noteproject, plano, arquivos]
---
# Plano do bbmetal

Fontes (PDF, imagem, texto) que a pessoa sobe para um workspace precisam de um lugar para os bytes e de uma tabela que diga de quem é cada arquivo. O plano é um serviço novo, o `bbmetal`, com a tabela `files` no [[Postgres]] e os bytes num storage S3 (SeaweedFS no dev, S3 na AWS na M3). O navegador sobe direto para o storage por URL assinada, sem passar os bytes pelo servidor. Issues: #206, #207, #208 (feitas uma vez e desfeitas em 2026-11-19, para refazer com calma e à mão), depois #209, #210 e #44.

> [!info] Primeira tentativa guardada
> As 6 branches da primeira tentativa (30 commits, 2026-11-09) estão no bundle `ai/build/bbmetal-stack.bundle`, fora do git. Para ver uma: `git fetch ai/build/bbmetal-stack.bundle bbmetal/add-the-bbmetal-file-service:old/bbmetal`.

## Pilha de branches

Uma branch por serviço, cada uma em cima da anterior (⏳ todas).

| # | Branch | Issue | Entrega |
|---|---|---|---|
| 1 | `seaweedfs/add-an-s3-storage-container` | #206 | serviço `seaweedfs` no compose (versão fixa, S3 na porta 8333, volume nomeado, sem porta no host); credenciais no `.env`; CORS para `https://notes.localhost` pela flag `-s3.allowedOrigins`; `PUT` sem assinatura → 403 |
| 2 | `caddy/add-an-s3-storage-container` | #206 | `https://files.localhost` → `seaweedfs:8333` com o `Host` intacto (a assinatura cobre ele); corpo acima de 100 MB → 413 |
| 3 | `postgres/add-the-bbmetal-file-service` | #207 | `postgres/init/create-bbmetal-database.sh` cria `bbmetal_migrator`, `bbmetal` e o banco `bbmetal` ([[Usuários do banco]]); `BBMETAL_*` no `.env.example`. Volume já existente: rodar o script à mão |
| 4 | `bbmetal/add-the-bbmetal-file-service` | #207 | `apps/bbmetal` (FastAPI em camadas, Alembic, `make check` e CI); tabela `files`; rotas abaixo; bucket `bbmetal` criado quando o serviço sobe; bbmetal 0.1.0 |
| 5 | `caddy/add-the-bbmetal-file-service` | #207 | `/api/files` e `/api/files/*` → `bbmetal:8000` sem o `/api`, só com sessão (401 sem) |
| 6 | `chimchar/add-the-sources-tab` | #208 | botão Sources (grupo da IA) abre uma aba com os workspaces à esquerda; arrastar sobe (`POST /api/files`, depois `PUT` na URL assinada; falhou o `PUT`, a linha some); lista com nome, tamanho e estado do card; Delete apaga linha e bytes |

## O serviço bbmetal

- **Tabela `files`**: `owner` por [[Row-Level Security|RLS]], `folder_id` sem FK (a pasta mora no banco do `ichiro`), `name`, `mime`, `size`, `card_status`, `created_at`.
- **Rotas**: `POST /files` devolve a URL de `PUT` assinada com tipo e tamanho (413 acima de 100 MB); `GET /files?folder_id=`; `GET /files/{id}` devolve a URL de `GET`; `DELETE /files/{id}` apaga linha e bytes.
- **Usuário do pedido**: lido do header `X-User-Id`, e a transação abre como esse usuário (a [[Row-Level Security|policy]] do banco filtra).
- **Ordem dos commits** da primeira tentativa: serviço com rota de saúde → teste → `make check` e CI → compose → tabela com policy → usuário do pedido → transação como o usuário → boto3 → client S3 → bucket no startup → repository → service com o limite → erros com status → rotas → testes.

## O que a primeira tentativa ensinou

- **URL assinada não faz rede**: `generate_presigned_url` só calcula a assinatura com a chave (boto3 1.43.126, `botocore/signers.py:325`). Por isso dois clientes: `public` (`https://files.localhost`) só para assinar e `inner` (`http://seaweedfs:8333`) para falar com o storage.
- **O `host` entra sempre na assinatura** (`botocore/auth.py:256`): URL assinada para um host não vale em outro.
- **Tipo e tamanho travados**: `Params={"ContentType": ..., "ContentLength": ...}` entra em `X-Amz-SignedHeaders`; `PUT` com outro tamanho ou tipo leva 403 (conferido contra o SeaweedFS 4.51).
- **Config**: `Config(signature_version="s3v4", s3={"addressing_style": "path"})`, URL `host/bucket/chave`, sem subdomínio por bucket.
- **Lint W13**: o prefixo `seaweedfs/` só passa se o W13 aceitar qualquer serviço do compose como prefixo de branch (mudança em `ai/tools/np.py`, `_branch_servico`).
- **Área nova** `arquivos` no `ai/kb/areas.yaml` (código em `apps/bbmetal/`, `caddy/Caddyfile`, compose; lib `boto3`; nota [[CORS]]).

## Fora da pilha

- ⏳ #209: ferramentas `list_sources`/`read_source` no `lonzo`. O `lonzo` não alcança `files.localhost` de dentro do compose; precisa de URL assinada para o host interno.
- ⏳ #210: card da fonte em `.workspace/kb/` (muda o `card_status`; botão de tentar de novo).
- ⏳ #44: imagens no editor.
- ⏳ CORS por bucket (`PutBucketCors`), como vai ser no S3: na M3, pelo Terraform.
