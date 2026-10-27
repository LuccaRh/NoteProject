---
tags: [noteproject, conceito, infra]
---
# Container

Um serviço só roda numa máquina que tenha a versão certa da linguagem, das libs e do sistema. Instalar isso à mão em cada máquina quebra fácil e não se repete igual.

- **Imagem**: pacote com o programa e tudo de que ele precisa, feito a partir de um [[Dockerfile]].
- **Container**: a imagem rodando, isolada das outras e da máquina. Tem IP próprio e suas portas ([[Rede de containers]]).
- Vários containers descritos num arquivo e subidos juntos: [[Docker Compose]]. Dado que sobrevive ao container: [[Volume do Docker|volume]].

## Onde cada coisa fica

- O Docker é um [[Daemon|daemon]] só por máquina e guarda tudo numa pasta só, `/var/lib/docker/`: imagens, containers e volumes de todos os projetos. O que está ali sobrevive ao reboot; volume só sai com `docker volume rm` ou `docker compose down -v`. *(geral)*

![[docker-por-dentro.drawio.svg]]
*Arquivos do projeto ficam no PC; imagens, containers e volumes ficam no Docker, num lugar só por máquina.*

## Recriar o container

Com imagem nova (`--build`), o compose **para e apaga** o container antigo e cria outro, com o mesmo nome, a partir dela.

- O que o container escreveu dentro de si some junto; só fica o que estava em [[Volume do Docker|volume]].
- A imagem antiga fica no disco sem nome (`<none>` em `docker images`) até `docker image prune`. *(geral)*
- Para parar, o Docker manda um [[Sinal do Linux|sinal]] ao processo: primeiro o `SIGTERM`, e o `SIGKILL` depois do prazo (10 s por padrão).
- Servidor HTTP que trata o `SIGTERM` (o uvicorn do [[FastAPI]]) para de aceitar requests novas e espera as em andamento terminarem.
- Entre o container velho cair e o novo subir, request nova recebe "connection refused": alguns segundos fora do ar. Evitar isso pede deploy sem downtime (dois containers e troca no [[Reverse proxy|proxy]]). *(geral)*

## Recarga dentro do container

- Quem recarrega ao salvar é um vigia de arquivos: o chokidar no Vite, o watchfiles no `fastapi dev`. Ele espera o sistema avisar que o arquivo mudou.
- Quando o aviso não atravessa para o container (comum no Docker Desktop do Mac e do Windows), o vigia passa a reler os arquivos de tempos em tempos (polling), ligado por variável em `environment:`: `CHOKIDAR_USEPOLLING=true` (Vite), `WATCHFILES_FORCE_POLLING=true` (watchfiles). Cada variável só vale para a sua lib. *(geral)*

Doc: [Docker — what is a container](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/).
