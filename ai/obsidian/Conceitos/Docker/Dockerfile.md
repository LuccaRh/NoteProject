---
tags: [noteproject, conceito, infra]
---
# Dockerfile

Uma [[Container|imagem]] precisa de uma receita repetível: qual sistema, qual linguagem, quais libs, qual código e qual comando sobe o programa. O `Dockerfile` é essa receita, lida de cima para baixo por `docker build` (ou pelo `build:` do compose).

- Comentário: linha que **começa** com `#`. Um `#` depois da instrução não é comentário: vira argumento dela (`COPY a ./  # x` tenta copiar um arquivo chamado `#`) ([Dockerfile reference — format](https://docs.docker.com/reference/dockerfile/#format)).
- O formato é próprio, sem `if` nem laço: cada linha é `INSTRUÇÃO argumentos`, de uma lista fixa. O que vem depois do `RUN` é comando de terminal comum, rodado pelo shell (`/bin/sh -c`) dentro da imagem ([Dockerfile reference](https://docs.docker.com/reference/dockerfile/)).

## As instruções

| Instrução                 | Quando roda       | O que faz                                                                    |
| ------------------------- | ----------------- | ---------------------------------------------------------------------------- |
| `FROM python:3.14-slim`   | build             | imagem de partida (sistema + linguagem); tudo o que vem depois fica por cima |
| `WORKDIR /app`            | build             | pasta onde os próximos comandos rodam e os arquivos caem                     |
| `COPY origem destino`     | build             | copia arquivos da máquina (o *contexto* do build) para dentro da imagem      |
| `RUN comando`             | build             | roda o comando agora (instalar libs) e guarda o resultado na imagem          |
| `ENV NOME=valor`          | build e container | variável de ambiente que fica valendo nos containers                         |
| `EXPOSE 8000`             | —                 | só documenta a porta; **não publica** (quem publica é o `ports:` do compose) |
| `CMD ["programa", "arg"]` | container         | comando que roda quando o container sobe; nada roda no build                 |

- **Como ler o `COPY`**: `COPY <origem…> <destino>`. O último argumento é o destino; os outros são origens, relativas ao contexto do build. Destino relativo (`./`) parte do `WORKDIR`: depois de `WORKDIR /app`, `COPY pyproject.toml uv.lock ./` põe os dois arquivos em `/app`.
- **`COPY --from=<imagem>`** copia de **outra imagem**, não do host. `COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /uvx /bin/` pega os executáveis da imagem oficial do uv e os põe em `/bin/`, uma das pastas do `PATH` (a lista de pastas onde o shell procura comandos); por isso os `RUN` seguintes acham o `uv` ([uv — Docker](https://docs.astral.sh/uv/guides/integration/docker/)).

## Build e container

- **Build** = montar a imagem: o Docker lê o Dockerfile, roda cada linha e guarda o resultado. A imagem fica pronta no disco, haja container ou não.
- **Container** = um processo que sobe a partir da imagem; só o `CMD` roda nessa hora.

| Ação | `RUN` (ex.: instalar libs) | `CMD` |
|---|---|---|
| build | roda 1 vez | não roda |
| subir 3 containers da mesma imagem | não roda | roda 3 vezes |

- O código copiado por `COPY` fica congelado na imagem. Editar o arquivo no host não muda o container que está rodando, nem um container novo da **mesma** imagem: só uma imagem nova (novo build) leva a mudança.
- O `docker compose up` só faz o build se a imagem ainda não existe. Mudou o Dockerfile, o código copiado ou as libs → `docker compose up --build`. Código que entra por volume não precisa de build ([[Volume do Docker|volume]]; [compose up](https://docs.docker.com/reference/cli/docker/compose/up/)).

## Camadas e cache

- Cada instrução vira uma **camada**: um "diff" sobre a anterior. A imagem é a pilha de camadas.
- No build seguinte, o Docker reaproveita (cache) toda camada cuja instrução e arquivos não mudaram.
- Mudou uma camada → ela **e todas as de baixo** são refeitas, mesmo que nada nelas mude.

Por isso a ordem importa: o que muda pouco vai em cima, o que muda sempre vai embaixo.

```dockerfile
FROM node:22-alpine
WORKDIR /app
# só a lista de libs: muda pouco
COPY package.json package-lock.json ./
# lento; fica no cache enquanto a lista não mudar
RUN npm install
# o código: muda sempre
COPY . .
CMD ["npm", "start"]
```

- Editar um arquivo do código só refaz o `COPY` do código: o `npm install` vem do cache.
- Copiar o código inteiro **antes** do `npm install` faria qualquer edição reinstalar todas as libs.
- Em Python com uv, o mesmo padrão: primeiro `pyproject.toml` e `uv.lock`, depois `uv sync --locked --no-install-project` (instala só as libs), depois o código e um `uv sync --locked` final ([uv — Docker](https://docs.astral.sh/uv/guides/integration/docker/)).
- O uv entra na imagem copiado da imagem oficial dele, com a versão fixa: `COPY --from=ghcr.io/astral-sh/uv:<versão> /uv /uvx /bin/` (mesmo guia).

## A lista de libs e a pasta das libs

A imagem não recebe as libs do host: recebe a **lista** e instala as suas.

```
host                        imagem (build)
pyproject.toml  ──COPY──▶   pyproject.toml ─┐
uv.lock         ──COPY──▶   uv.lock        ─┴─ RUN uv sync ─▶ /app/.venv (nova)
.venv  (fica no host)
```

| Ecossistema | Lista (vai no `COPY`) | Instala com | Pasta das libs (criada pelo instalador, na pasta onde roda) |
|---|---|---|---|
| Python ([[venv]]) | `pyproject.toml` + `uv.lock` | `uv sync` | `./.venv` |
| Node | `package.json` + `package-lock.json` | `npm install` | `./node_modules` |

- O Dockerfile não diz onde as libs caem: é convenção do instalador, que usa a pasta de trabalho (`WORKDIR`).
- O lockfile fixa a versão exata de cada lib, e a pasta da imagem sai igual à do host sem ser copiada.
- Mudou a lista → só o build instala (o `RUN` não roda ao subir o container). O [[Volume do Docker|volume]] leva a lista nova, mas ninguém roda o instalador.
- A pasta do host (`.venv`, `node_modules`) fica fora do git e foi feita para o sistema do host. Lib com binário compilado só roda no sistema para o qual foi feita: um `…-linux-x64-gnu` (glibc, Arch e Debian) não roda numa imagem alpine (musl).

## Contexto do build e `.dockerignore`

- O contexto é a pasta mandada ao Docker no build (`context:` do compose); `COPY` só enxerga o que está nela.
- `.dockerignore` tira coisas do contexto. A `.venv` e o `node_modules` locais ficam de fora: foram feitos para a máquina do host, e a imagem cria os seus.
- Sem o `.dockerignore`, o `COPY . .` (que vem **depois** do `RUN` que instala as libs) misturaria a pasta de libs do host por cima da criada na imagem: arquivo de mesmo nome é sobrescrito. Com ele, a do host nem chega ao Docker e a da imagem fica intacta.

```
contexto (pasta do serviço) ─ .dockerignore tira .venv, caches ─▶ COPY . . ─▶ /app (a .venv do RUN continua)
```

| Momento | O que pode cobrir a pasta de libs da imagem | Proteção |
|---|---|---|
| build | o `COPY . .` trazendo a do host | `.dockerignore` |
| container de dev | o bind mount do código | volume anônimo (o [[Volume do Docker\|buraco]]) |
| container de produção | nada (sem bind mount) | nenhuma |

> [!warning] Erros comuns
> - `COPY . .` antes de instalar as libs: o cache das libs se perde a cada edição.
> - Duas instruções na mesma linha (`COPY a RUN b`): o `COPY` lê `RUN` e `b` como arquivos a copiar. Uma instrução por linha, e o `COPY` sempre com destino.
> - `CMD` de outro ecossistema (`pip run dev` copiado de `npm run dev`): o pip não tem `run`; o comando é o do servidor da linguagem.
> - Esperar que `EXPOSE` abra a porta: só o `ports:` (ou `-p`) publica.
> - `CMD` com o programa escutando em `127.0.0.1`: de fora do container ninguém alcança ([[Porta#Endereço de escuta|endereço de escuta]]).
> - Copiar a `.venv` do host para a imagem: libs compiladas para outra máquina.

> [!example] No NoteProject
> A imagem da [[API de notas]] segue esse padrão com uv e sobe com `fastapi run`.

Docs: [Dockerfile reference](https://docs.docker.com/reference/dockerfile/), [Build cache](https://docs.docker.com/build/cache/), [uv — Docker](https://docs.astral.sh/uv/guides/integration/docker/).
