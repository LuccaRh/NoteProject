---
tags: [noteproject, conceito, infra]
---
# Volume do Docker

O que um [[Container|container]] escreve dentro de si some quando ele é recriado, e o código copiado na imagem fica congelado nela. O volume resolve os dois: dado que sobrevive ao container (o banco) e código do host visto ao vivo dentro dele (desenvolvimento).

O sistema de arquivos do container começa como o da imagem. Um volume é uma pasta de fora da imagem, montada **num caminho que já existe**: montar = "neste caminho, mostre outra pasta". Um caminho só mostra uma coisa por vez; o que a imagem tinha ali fica escondido, não apagado, e volta se o volume sai.

## Volume por cima da imagem

Ordem: o [[Dockerfile]] roda no **build** (gera a imagem); os `volumes:` do [[Docker Compose|compose]] são montados ao **criar o container**, por cima dela; por último roda o `CMD`.

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
- Volumes ficam em `/var/lib/docker/`, junto com imagens e containers ([[Container#Onde cada coisa fica|onde cada coisa fica]]).

## O buraco da pasta das libs

```
/app               ← bind mount: pasta do host, ao vivo
/app/node_modules  ← volume anônimo: libs instaladas no build (o "buraco" no bind mount)
```

- O bind mount cobre tudo o que a imagem pôs em `/app`, inclusive a pasta das libs. Sem o buraco, o container veria o `node_modules`/`.venv` do host (ou nada, se o host não instalou), feito para o sistema do host ([[Dockerfile#A lista de libs e a pasta das libs|lista × pasta das libs]]). Para Python, a mesma linha com `/app/.venv`.
- O compose **reaproveita** o volume anônimo ao recriar o container. Lib nova + `--build`: a imagem nova tem a lib, mas o volume antigo, já cheio, não recebe a cópia e cobre a imagem. Saída: `docker compose up --build -V` (`--renew-anon-volumes`) ([compose up](https://docs.docker.com/reference/cli/docker/compose/up/), [volumes](https://docs.docker.com/engine/storage/volumes/)).

> [!warning] Erros comuns
> - Achar que o volume é uma cópia: é a pasta do host vista de dentro.
> - Achar que o volume basta para lib nova: ele leva a lista, quem instala é o build.
> - Bind mount do projeto sem o buraco da pasta das libs: o container usa as do host.

Doc: [Docker — volumes](https://docs.docker.com/engine/storage/volumes/).
