---
tags: [noteproject, conceito]
---
# Conceitos — mapa

Os conceitos que o projeto usa, uma página cada: como funcionam, em geral. Cada seção abaixo é uma pasta de `Conceitos/`. Como o NoteProject usa cada um mora em [[00 Mapa — Estrutura do projeto|Estrutura do projeto]]; perguntas para se testar, em [[00 Mapa — Prova do projeto|Prova do projeto]].

## Sync

| Página | Ideia |
|---|---|
| [[Local-first]] | tudo acontece no dispositivo primeiro; a rede propaga depois |
| [[UI otimista]] | a tela mostra o resultado antes de o servidor confirmar |
| [[CRDT]] | edições paralelas se juntam sem conflito, em qualquer ordem |
| [[Yjs]] | a lib de CRDT em JavaScript: cada edição vira um update binário |
| [[WebSocket]] | conexão aberta: o servidor manda sem esperar pedido |
| [[Sync por versão]] | quem volta do offline pede só [[Sync por versão\|`version > N`]] |
| [[Redis pub-sub]] | instâncias de sync avisando umas às outras |

## Editor

| Página | Ideia |
|---|---|
| [[CodeMirror]] | o texto não muda; a decoração mostra outra coisa no lugar |
| [[Markdown]] | formatação escrita com caracteres comuns; `.md` é só texto |
| [[WebAssembly]] | programa em C/Rust rodando dentro da página |

## Banco de dados

| Página | Ideia |
|---|---|
| [[SQLite]] | banco SQL inteiro num arquivo, sem servidor |
| [[FTS5]] | índice invertido do SQLite: palavra → linhas onde ela aparece |
| [[Postgres]] | banco que roda como serviço; muitos clientes escrevem ao mesmo tempo |
| [[Migration]] | cada mudança do schema é um arquivo versionado: `upgrade` aplica, `downgrade` reverte |
| [[SQLAlchemy]] | a API guarda conexões abertas e empresta uma por pedido |
| [[Transação]] | vários comandos num bloco de tudo ou nada: `COMMIT` ou `ROLLBACK` |
| [[Árvore no banco]] | cada linha aponta para o pai; a pasta é um item da mesma tabela |

## Python

| Página | Ideia |
|---|---|
| [[Módulo Python]] | um arquivo `.py`; o primeiro `import` roda o arquivo inteiro |
| [[Package Python]] | pasta de módulos importada com ponto; estrutura plana × `src/` |
| [[sys.path]] | a lista de pastas onde o `import` procura, só no primeiro nível |
| [[venv]] | cada projeto com o seu Python e as suas libs |
| [[uv]] | o `pyproject.toml` é o pedido, o `.venv` o resultado; o uv deixa os dois iguais |
| [[Decorator]] | o `@` passa a função a outra logo depois do `def`, uma vez, ao importar |
| [[Context manager]] | o `with` garante a saída; o `yield` divide entrada e saída; o `async with` espera ao abrir e fechar |
| [[Gerador]] | o `yield` entrega um item por vez e pausa; o `async for` espera cada item sem travar os outros |
| [[FastAPI]] | a função tipada vira rota validada e documentada |

## Rede

| Página | Ideia |
|---|---|
| [[Endereço IP]] | o endereço da máquina numa rede; público ou privado, por DHCP ou fixo |
| [[Porta]] | o número que acha o programa dentro da máquina |
| [[Rede]] | máquinas que se alcançam direto; uma máquina está em várias |
| [[Roteamento]] | cada roteador decide só o próximo pulo, pela tabela de rotas |
| [[NAT]] | a casa inteira sai por um IP público; a porta diz de quem é a volta |
| [[TCP]] | dados viajam em pacotes; o TCP numera e confirma, e vira uma linha de bytes confiável |
| [[DNS]] | traduz o nome no IP |
| [[Domínio]] | nome fixo, alugado, que segue valendo quando a máquina muda |
| [[TLS]] | conexão cifrada e servidor comprovado; HTTPS é HTTP por dentro dele |
| [[Reverse proxy]] | uma porta na frente de todos os serviços |
| [[CORS]] | o navegador só deixa a página ler respostas da mesma origem, salvo se o servidor liberar |
| [[URL relativa]] | o código escreve só o caminho; o navegador completa com a origem da página |
| [[Proxy de desenvolvimento]] | o servidor do front repassa `/api` à api, e tudo fica na mesma origem |
| [[Servidor de desenvolvimento]] | quem responde `/` com o `index.html` e converte o `.ts` na hora; o `Content-Type` diz o que o navegador faz |
| [[Arquivo estático]] | resposta lida do disco como está, um pedido por arquivo; a dinâmica sai de código |
| [[Server-sent events]] | uma resposta HTTP que fica aberta e manda eventos nomeados aos pedaços |

## TypeScript

| Página | Ideia |
|---|---|
| [[DOM]] | o HTML vira uma árvore de objetos; o JS mexe nela e a tela acompanha |
| [[Arrow function]] | `x => ...` é o `lambda` do JS, e usa o `this` de fora |
| [[Spread]] | `...lista` desmonta a lista em argumentos (`*lista`); no parâmetro, junta (rest) |
| [[Nullish coalescing]] | `a ?? b`: `b` só quando `a` é `null` ou `undefined`, diferente do `\|\|` |
| [[Promise]] | o valor que chega depois; `await` espera, `void` ignora de propósito |
| [[Callback]] | a peça recebe uma função e a chama no acontecimento; quem cria decide o que fazer |
| [[Build do front]] | o `dist/`: TS convertido e juntado uma vez; o navegador baixa e roda |

## Docker

| Página | Ideia |
|---|---|
| [[Container]] | o programa empacotado com o que precisa, rodando isolado |
| [[Dockerfile]] | receita da imagem; build × container; a ordem das instruções decide o que o cache reaproveita |
| [[Build multi-stage]] | um estágio gera os arquivos, a imagem final leva só o resultado |
| [[Docker Compose]] | vários containers descritos num arquivo e subidos juntos |
| [[Volume do Docker]] | pasta de fora montada por cima da imagem; o dado sobrevive ao container |
| [[Rede de containers]] | containers se acham pelo nome; só a porta publicada chega de fora |
| [[Sandbox]] | código de terceiros rodando fechado: sem rede, banco nem chave |

## Linux

| Página | Ideia |
|---|---|
| [[Daemon]] | programa em segundo plano, dono único de um recurso |
| [[Executar um arquivo no Linux]] | o Linux roda um arquivo pela permissão `x` e pelo formato (ELF ou `#!`), nunca pelo nome |
| [[Sinal do Linux]] | o aviso de "pare" ao processo: `SIGTERM` dá para tratar, `SIGKILL` não |

## Auth

| Página | Ideia |
|---|---|
| [[Token por dispositivo]] | um [[Token por dispositivo\|token por dispositivo]], mandado em todo pedido |
| [[OIDC]] | o GitHub entra na AWS sem chave guardada |

## AWS

| Página | Ideia |
|---|---|
| [[EC2]] | a máquina alugada |
| [[S3]] | arquivos grandes por chave, fora da máquina |
| [[IAM]] | quem pode fazer o quê na AWS, sem chave fixa |
| [[Security Group]] | o firewall da máquina: só a 443 entra |
| [[SSM Session Manager]] | shell na máquina sem porta 22 |

## Deploy

| Página | Ideia |
|---|---|
| [[Terraform]] | a infra em arquivos, recriada com um comando |
| [[CI]] | testes a cada push |
| [[CD]] | deploy a cada merge |
| [[Backup]] | cópia fora da máquina, restaurada uma vez para provar |
| [[Observabilidade]] | o servidor avisa que caiu |

## IA

| Página | Ideia |
|---|---|
| [[MCP]] | padrão para a IA chamar funções de fora |
| [[Chamada a um modelo]] | request HTTP comum; o modelo não lembra nada e só sabe o que vem no pacote (`system`, `tools`, `messages`) |
| [[Laço de ferramentas]] | o modelo pede ferramenta, o programa executa e chama de novo; o harness em volta |
| [[Cache de prompt]] | começo igual da chamada sai mais barato |
