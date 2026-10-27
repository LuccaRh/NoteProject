---
tags: [noteproject, plano, infra]
---
# #11 Run the server in Docker Compose

Issue do [[M0 Server skeleton]]. Roda a API num container: imagem de desenvolvimento e serviço `notes` no compose, em `127.0.0.1:8000`, recarregando ao salvar. Passou por [[Container e Docker Compose|Docker]] e [[IP, porta e rede de containers|rede]].

## Docker

- Imagem é o pacote; container é a imagem rodando; o compose descreve vários containers, portas e volumes ([[Container e Docker Compose]]).
- Camadas e cache: copiar `pyproject.toml` + `uv.lock` e rodar `uv sync --no-install-project` antes do `COPY . .`, para editar o código não reinstalar as libs ([[Dockerfile e camadas]]).
- A imagem recebe a lista de libs, não a pasta: a `.venv` do host foi feita para o host (binário glibc × musl), e o `.dockerignore` a tira do contexto.
- `EXPOSE` só documenta; quem publica a porta é o `ports:`.
- Volume monta por cima do que a imagem tem no caminho: o bind mount `./apps/notes:/app` cobre o `/app`, e o volume anônimo `/app/.venv` abre o buraco que devolve as libs da imagem.
- Lib nova pede `up --build -V`: o volume anônimo antigo, já cheio, cobriria a imagem nova.
- Recriar o container apaga o que não está em volume; `docker stop` manda `SIGTERM` e, passado o prazo, `SIGKILL`.
- Desenvolvimento e produção usam o mesmo Dockerfile com compose diferente; daí o nome `docker-compose-dev.yml`.

## Rede

- Uma máquina está em várias redes ao mesmo tempo (loopback, wi-fi, Docker); `0.0.0.0` = todos os IPs dela, e dentro do container `localhost` é o próprio container ([[IP, porta e rede de containers]]).
- `127.0.0.1:8000:8000` publica a porta só no loopback do host: outra máquina do wi-fi não chega.
