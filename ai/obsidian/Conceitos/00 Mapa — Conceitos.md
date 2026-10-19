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
| [[WebAssembly]] | programa em C/Rust rodando dentro da página |

## Dados e sync

| Página | Ideia |
|---|---|
| [[SQLite e FTS5]] | banco num arquivo + busca por palavra |
| [[Postgres e migrations]] | banco do servidor e mudanças de schema em ordem |
| [[CRDT e Yjs]] | edições paralelas se juntam sem conflito |
| [[WebSocket]] | conexão aberta: o servidor manda sem esperar pedido |
| [[Sync por versão]] | quem volta do offline pede só [[Sync por versão\|`version > N`]] |
| [[Redis pub-sub]] | instâncias de sync avisando umas às outras |

## Servidor e acesso

| Página | Ideia |
|---|---|
| [[Token por dispositivo]] | um [[Token por dispositivo\|token por dispositivo]], mandado em todo pedido |
| [[IP, porta e rede de containers]] | IP acha a máquina, porta acha o programa; containers se acham pelo nome |
| [[Reverse proxy]] | uma porta na frente de todos os serviços |
| [[TLS e HTTPS]] | conexão cifrada e servidor comprovado |
| [[DNS e domínio]] | nome fixo que aponta para o IP |

## Infra

| Página | Ideia |
|---|---|
| [[Container e Docker Compose]] | serviço empacotado; vários descritos num arquivo |
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
