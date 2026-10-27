---
tags: [noteproject, conceito, servidor]
---
# venv

Um `site-packages` (a pasta onde ficam as libs instaladas) comporta um só `fastapi/`: instalar a versão 0.100 apaga a 0.120, e um dos projetos da máquina que dependem dela quebra. O venv dá a cada projeto as suas libs, sem brigar com os outros.

- **venv**: pasta com um `python` e um `site-packages` só daquele projeto.

```
projeto/.venv/
├── bin/python                      ← o Python deste projeto
└── lib/python3.x/site-packages/    ← os instalados só deste projeto
```

## Qual Python roda

O `import` não muda com o venv; muda **qual Python** roda, e cada Python traz o seu [[sys.path]]:

```
python3 main.py             ← Python do sistema: site-packages do sistema
.venv/bin/python main.py    ← Python do venv: site-packages do venv
uv run python main.py       ← igual ao de cima; o uv escolhe o Python do .venv
```

## Gerado, fora do git

O `.venv` é gerado: fica fora do git e não se edita à mão. O [[uv]] o preenche a partir do `pyproject.toml` e do `uv.lock`; com o `.venv` apagado, o `uv sync` reinstala tudo igual. É o mesmo papel do `node_modules/` com `package.json` e `package-lock.json`.

- A pasta foi feita para o sistema da máquina: uma [[Dockerfile#A lista de libs e a pasta das libs|imagem Docker]] recebe a lista e cria o seu `.venv`, sem copiar o do host.

Doc: [venv](https://docs.python.org/3/library/venv.html).
