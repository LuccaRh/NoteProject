---
tags: [noteproject, conceito, infra]
---
# Container e Docker Compose

Um serviço só roda numa máquina que tenha a versão certa da linguagem, das libs e do sistema. Instalar isso à mão em cada máquina quebra fácil e não se repete igual.

- **Imagem**: pacote com o programa e tudo de que ele precisa, feito a partir de um [[Dockerfile e camadas|Dockerfile]].
- **Container**: a imagem rodando, isolada das outras e da máquina.
- **Docker Compose**: um arquivo (`docker-compose.yml`) que descreve vários containers, portas, volumes e redes; `docker compose up` sobe todos.

| No compose | Para quê |
|---|---|
| `services` | um container por serviço (api, banco como o [[Postgres e migrations\|Postgres]], [[Reverse proxy\|proxy]]) |
| `volumes` | dado que sobrevive ao container (o banco) |
| `restart: unless-stopped` | volta sozinho depois de cair ou de a máquina reiniciar |
| `healthcheck` | o compose sabe se o serviço responde ([[Observabilidade]]) |

- Em desenvolvimento, o código costuma ser montado no container para recarregar a cada mudança; em produção, a imagem já vem pronta de um registry ([[CI e CD]]).

## Onde cada coisa fica

- O Docker é um [[Daemon|daemon]] só por máquina e guarda tudo numa pasta só, `/var/lib/docker/`: imagens, containers e volumes de todos os projetos. O que está ali sobrevive ao reboot; volume só sai com `docker volume rm` ou `docker compose down -v`. *(geral)*
- O compose põe o nome do projeto (por padrão, o da pasta) na frente do que cria: o volume `db` vira `noteproject_db`, e outro projeto com um `db` ganha um volume próprio. `docker volume inspect <nome>` mostra onde ele fica no disco (`Mountpoint`). *(geral)*

![[docker-por-dentro.drawio.svg]]
*Arquivos do projeto ficam no PC; imagens, containers e volumes ficam no Docker, num lugar só por máquina.*

## Rodar um comando no container: `exec`

`docker compose exec <serviço> <programa>` roda um programa dentro de um container que já está de pé e liga o terminal a ele; o container não é recriado. *(geral)*

| Exemplo | Faz |
|---|---|
| `docker compose exec postgres bash` | abre um shell no container; `exit` volta |
| `docker compose exec postgres psql -U <usuário> -d <banco>` | abre direto o [[Postgres e migrations\|psql]] |
| `docker compose exec notes uv run alembic upgrade head` | roda as [[Migrations com Alembic\|migrations]] onde o nome do banco resolve |

- O serviço é o nome no arquivo do compose; com `-f`, o mesmo `-f` do `up`.
- Container parado: o `exec` falha. O `docker compose run <serviço> <programa>` cria um container novo só para o comando.
- O programa roda com as variáveis do container (as do `.env`) e na rede do compose, onde os outros serviços são achados pelo nome.

## Variáveis do `.env`

- `env_file: .env` num serviço: quem lê o arquivo é o `docker compose`, no host. Ao criar o container, cada linha `NOME=valor` vira uma variável de ambiente dele, o mesmo que `docker run -e NOME=valor`. O arquivo não entra no container. *(geral)*
- O mesmo `.env` em dois serviços entrega o mesmo valor aos dois: a senha que cria o usuário no [[Postgres e migrations|Postgres]] é a que a API usa para conectar.
- O container guarda os valores de quando foi criado; mudar o `.env` só vale ao recriá-lo (`up` de novo). *(geral)*
- O `.env` fica fora do git (`.gitignore`), porque tem segredo.

## Volume por cima da imagem

O sistema de arquivos do container começa como o da imagem. Um volume é uma pasta de fora da imagem, montada **num caminho que já existe**: montar = "neste caminho, mostre outra pasta". Um caminho só mostra uma coisa por vez; o que a imagem tinha ali fica escondido, não apagado, e volta se o volume sai.

Ordem: o [[Dockerfile e camadas|Dockerfile]] roda no **build** (gera a imagem); os `volumes:` são montados ao **criar o container**, por cima dela; por último roda o `CMD`.

![[volume-por-cima.drawio.svg]]
*O volume chega depois do build e cobre o `/app` da imagem; o volume anônimo devolve só a pasta das libs.*

| Em `volumes:` | Tipo | O que monta | Recebe o que a imagem tinha no caminho? |
|---|---|---|---|
| `./web:/app` (`origem:destino`) | bind mount | a pasta do host, ao vivo (nada é copiado; editar no host aparece na hora) | não |
| `/app/node_modules` (só destino) | volume anônimo | área guardada pelo Docker | sim, **só quando vazio** |
| `dados:/var/lib/postgresql` | volume nomeado | idem, com nome | idem; sobrevive a apagar o container (o banco) |

- Caminho mais fundo fica por cima: o Docker monta o pai (`/app`) antes do filho (`/app/node_modules`), seja qual for a ordem das linhas no YAML. *(geral)*
- O Docker não procura a pasta pelo nome: olha o caminho de destino na imagem.
- O programa não escolhe entre as duas versões: o Node (ou o Python) só abre o caminho e vê a folha de cima.

```
/app               ← bind mount: pasta do host, ao vivo
/app/node_modules  ← volume anônimo: libs instaladas no build (o "buraco" no bind mount)
```

- O bind mount cobre tudo o que a imagem pôs em `/app`, inclusive a pasta das libs. Sem o buraco, o container veria o `node_modules`/`.venv` do host (ou nada, se o host não instalou), feito para o sistema do host ([[Dockerfile e camadas#A lista de libs e a pasta das libs|lista × pasta das libs]]). Para Python, a mesma linha com `/app/.venv`.
- O compose **reaproveita** o volume anônimo ao recriar o container. Lib nova + `--build`: a imagem nova tem a lib, mas o volume antigo, já cheio, não recebe a cópia e cobre a imagem. Saída: `docker compose up --build -V` (`--renew-anon-volumes`) ([compose up](https://docs.docker.com/reference/cli/docker/compose/up/), [volumes](https://docs.docker.com/engine/storage/volumes/)).

> [!warning] Erros comuns
> - Achar que o volume é uma cópia: é a pasta do host vista de dentro.
> - Achar que o volume basta para lib nova: ele leva a lista, quem instala é o build.
> - Bind mount do projeto sem o buraco da pasta das libs: o container usa as do host.

## Recriar o container

Com imagem nova (`--build`), o compose **para e apaga** o container antigo e cria outro, com o mesmo nome, a partir dela.

- O que o container escreveu dentro de si some junto; só fica o que estava em volume.
- A imagem antiga fica no disco sem nome (`<none>` em `docker images`) até `docker image prune`. *(geral)*

Para parar, o Docker manda um **sinal** ao processo: um aviso do Linux, que o processo pode tratar ou não ([`man 7 signal`](https://man7.org/linux/man-pages/man7/signal.7.html)).

| Sinal | Quem manda | O processo pode tratar? |
|---|---|---|
| `SIGINT` | Ctrl+C | sim |
| `SIGTERM` | `kill <pid>`, `docker stop` | sim: fecha com calma |
| `SIGKILL` | `kill -9`, o Docker depois do prazo (10 s por padrão) | não: morre na hora |

- Servidor HTTP que trata o `SIGTERM` (o uvicorn do [[FastAPI]]) para de aceitar requests novas e espera as em andamento terminarem.
- Entre o container velho cair e o novo subir, request nova recebe "connection refused": alguns segundos fora do ar. Evitar isso pede deploy sem downtime (dois containers e troca no [[Reverse proxy|proxy]]). *(geral)*

## Recarga dentro do container

- Quem recarrega ao salvar é um vigia de arquivos: o chokidar no Vite, o watchfiles no `fastapi dev`. Ele espera o sistema avisar que o arquivo mudou.
- Quando o aviso não atravessa para o container (comum no Docker Desktop do Mac e do Windows), o vigia passa a reler os arquivos de tempos em tempos (polling), ligado por variável em `environment:`: `CHOKIDAR_USEPOLLING=true` (Vite), `WATCHFILES_FORCE_POLLING=true` (watchfiles). Cada variável só vale para a sua lib. *(geral)*

## Desenvolvimento e produção

- A mesma imagem (o mesmo [[Dockerfile e camadas|Dockerfile]]) serve aos dois; muda o compose.
- Desenvolvimento: monta o código por bind mount e troca o comando por um que recarrega. Produção: arquivo à parte (`docker-compose.prod.yml`), sem código montado, com a imagem vinda do registry e `restart`.
- O código entra pelos dois caminhos: `COPY . .` na imagem e bind mount no dev. No dev, o volume cobre a cópia, que fica redundante ali; a cópia é o que faz a imagem rodar **sozinha** (CI, outra máquina, produção) e o que o instalador precisa para instalar o próprio projeto no build.

| | Dev | Produção |
|---|---|---|
| Imagem | `build:` | `image:` pronta, do registry |
| Comando | um que recarrega (`fastapi dev`) | sem recarga (`fastapi run`) |
| Volume do código | bind mount + buraco da pasta das libs | nenhum: vale o código do `COPY` |
| Volume de dados | — | volume nomeado do banco |
| `ports:` da API | `127.0.0.1:8000:8000`, para testar do host | nenhum: só o [[Reverse proxy\|proxy]] publica (443, e 80 para redirecionar) e chama `api:8000` pela rede do compose |
| `restart:` | — | `unless-stopped` |

- Sem `ports:` na API, o único caminho de fora até ela passa pelo proxy, onde fica o [[TLS e HTTPS|TLS]] ([[IP, porta e rede de containers]]).
- O Compose também junta arquivos: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up` aplica o segundo por cima do primeiro ([Merge Compose files](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/)).

> [!example] No NoteProject
> Hoje o compose sobe o Vite; o servidor e o [[Postgres e migrations|Postgres]] entram em M0, e em produção, o mesmo jeito numa [[EC2]] ([[Infra — deploy e operação]]).

Doc: [Docker Compose](https://docs.docker.com/compose/).
