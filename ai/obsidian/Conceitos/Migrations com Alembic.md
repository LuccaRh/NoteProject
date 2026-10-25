---
tags: [noteproject, conceito, dados]
---
# Migrations com Alembic

Um banco com dados não pode ser apagado e recriado a cada mudança de tabela. A mudança precisa ser escrita uma vez e aplicada igual em todo banco: o do notebook, o de outra máquina, o do servidor. Isso é a migration ([[Postgres e migrations]]); o Alembic é a ferramenta de migrations do Python, feita sobre o [[SQLAlchemy — engine e conexão|SQLAlchemy]].

- **Migration**: uma alteração do schema, versionada. Cada arquivo é uma mudança (cria tabela, adiciona coluna) e aponta para a anterior; juntos, formam o histórico do schema, como commits.
- **`upgrade()`**: aplica a mudança do arquivo.
- **`downgrade()`**: reverte exatamente essa mudança.

```
versions/
  a1_create_users_and_notes.py   upgrade: cria as tabelas  | downgrade: apaga
  b2_add_deleted_at.py           upgrade: add coluna       | downgrade: drop coluna
```

## Do arquivo ao banco

| Passo | Comando | Toca no banco? |
|---|---|---|
| criar o arquivo | `alembic revision -m "<mensagem>"` | não: gera o arquivo com `upgrade()` e `downgrade()` vazios |
| escrever a mudança | `op.create_table(...)` no `upgrade()`, `op.drop_table(...)` no `downgrade()` | não |
| aplicar | `alembic upgrade head` | sim: roda o `upgrade()` dos arquivos que faltam |
| reverter a última | `alembic downgrade -1` | sim: roda o `downgrade()` dela |

- O `-m` é só um rótulo: vira o nome do arquivo, como a mensagem de um commit. O que cria a tabela é o código dentro do `upgrade()`.
- O banco guarda numa tabela `alembic_version` o último arquivo aplicado. O `upgrade head` roda só os que faltam depois dele; sem nada faltando, não faz nada.
- Banco vazio (volume apagado, máquina nova): o mesmo `upgrade head` roda todos, do primeiro ao último, e chega ao schema atual.
- `upgrade <id>` e `downgrade <id>` param num arquivo escolhido; o normal é `head`, o último.
- O `downgrade()` só roda quando pedido. Serve para voltar atrás de uma migration errada: reverte, corrige, aplica de novo.

## Mudar o schema depois

- Arquivo já aplicado em outro banco ou já no git não se edita: o banco que já o rodou nunca veria a mudança. A mudança nova é **um arquivo novo** (`op.add_column` / `op.drop_column`).
- Arquivo só no banco local, sem commit: `downgrade -1`, editar, `upgrade head`.
- Coluna nova numa tabela com linhas precisa aceitar vazio (`nullable=True`) ou ter um valor padrão (`server_default`); senão o Postgres não tem o que pôr nas linhas antigas.

## A conexão

O Alembic é um cliente do [[Postgres e migrations|Postgres]] como outro qualquer: conecta por uma URL (`postgresql+psycopg://usuário:senha@host:5432/banco`), em que o host é o nome do serviço, achado pelo DNS da [[IP, porta e rede de containers|rede do compose]], e a URL vem do [[Container e Docker Compose|`.env`]]. Quem monta a conexão é o `env.py`, gerado pelo `alembic init` e editado à mão; o `alembic.ini` diz onde ficam as migrations.

> [!warning] Erros comuns
> - Achar que o `alembic revision` criou a tabela: ele só cria o arquivo.
> - Editar uma migration já aplicada em outro banco em vez de criar uma nova.
> - Rodar o Alembic fora da rede do compose: o nome do serviço não resolve ali.

> [!example] No NoteProject
> A migration cria `users` e `notes` no servidor ([[API de notas]]).

Doc: [Alembic — tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html).
