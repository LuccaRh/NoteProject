---
tags: [noteproject, conceito]
---
# Conceitos — mapa

Os conceitos que o projeto usa, uma página cada: como funcionam, em geral. Como o NoteProject usa cada um mora em [[00 Mapa — Estrutura do projeto|Estrutura do projeto]].

## O app

| Página | Ideia |
|---|---|
| [[Local-first]] | tudo acontece no dispositivo primeiro; a rede propaga depois |
| [[UI otimista]] | a tela mostra o resultado antes de o servidor confirmar |
| [[Daemon]] | programa em segundo plano, dono único de um recurso |
| [[CodeMirror e decorações]] | o texto não muda; a tela mostra outra coisa no lugar |
| [[Markdown]] | formatação escrita com caracteres comuns; `.md` é só texto |
| [[WebAssembly]] | programa em C/Rust rodando dentro da página |

## Dados e sync

| Página | Ideia |
|---|---|
| [[SQLite e FTS5]] | banco num arquivo + busca por palavra |
| [[Árvore no banco]] | cada linha aponta para o pai; a pasta é um item da mesma tabela |
| [[Postgres e migrations]] | banco do servidor e mudanças de schema em ordem |
| [[Migrations com Alembic]] | cada mudança do schema é um arquivo versionado: `upgrade` aplica, `downgrade` reverte |
| [[SQLAlchemy — engine e conexão]] | a API guarda conexões abertas e empresta uma por pedido |
| [[CRDT e Yjs]] | edições paralelas se juntam sem conflito |
| [[WebSocket]] | conexão aberta: o servidor manda sem esperar pedido |
| [[Sync por versão]] | quem volta do offline pede só [[Sync por versão\|`version > N`]] |
| [[Redis pub-sub]] | instâncias de sync avisando umas às outras |

## Servidor e acesso

| Página | Ideia |
|---|---|
| [[Python — módulo, package e venv]] | o `import` procura numa lista de pastas; cada projeto tem as suas libs |
| [[FastAPI]] | a função tipada vira rota validada e documentada |
| [[Token por dispositivo]] | um [[Token por dispositivo\|token por dispositivo]], mandado em todo pedido |
| [[IP, porta e rede de containers]] | IP acha a máquina, porta acha o programa; containers se acham pelo nome |
| [[TCP e pacotes]] | dados viajam em pacotes; o TCP numera e confirma, e vira uma linha de bytes confiável |
| [[Reverse proxy]] | uma porta na frente de todos os serviços |
| [[TLS e HTTPS]] | conexão cifrada e servidor comprovado |
| [[DNS e domínio]] | nome fixo que aponta para o IP |

## Infra

| Página | Ideia |
|---|---|
| [[Container e Docker Compose]] | serviço empacotado; vários descritos num arquivo; volume montado por cima da imagem |
| [[Executar um arquivo no Linux]] | o Linux roda um arquivo pela permissão `x` e pelo formato (ELF ou `#!`), nunca pelo nome |
| [[Dockerfile e camadas]] | receita da imagem; build × container; a ordem das instruções decide o que o cache reaproveita |
| [[EC2]] | a máquina alugada |
| [[S3 — armazenamento de objetos]] | arquivos grandes por chave, fora da máquina |
| [[IAM]] | quem pode fazer o quê na AWS, sem chave fixa |
| [[Security Group e SSM]] | só a 443 entra; shell sem porta 22 |
| [[Terraform — infra como código]] | a infra em arquivos, recriada com um comando |
| [[CI e CD]] | testes a cada push, deploy a cada merge |
| [[OIDC]] | o GitHub entra na AWS sem chave guardada |
| [[Backup e restore]] | cópia fora da máquina, restaurada uma vez para provar |
| [[Observabilidade]] | o servidor avisa que caiu |

## IA

| Página | Ideia |
|---|---|
| [[MCP]] | padrão para a IA chamar funções de fora |
| [[Cache de prompt]] | começo igual da chamada sai mais barato |
