---
tags: [noteproject, workspace]
---
# Propostas recusadas

Várias propostas de desenho da sessão foram recusadas na conversa, e o projeto seguiu por outro caminho. Juntas, elas mostram em que tipo de proposta a sessão costuma errar. A lista ajuda a conferir uma proposta nova antes de levá-la à conversa.

## Lista (2026-10-20 a 2026-11-09)

Tirada dos históricos de sessão (`~/.claude/projects/-home-lucca-Documents-NoteProject/*.jsonl`), nos trechos em que a sessão mudou de recomendação depois de uma objeção. Ficam de fora os fatos errados corrigidos depois (o `.env` inteiro no ichiro, a constraint de título repetido, o `GRANT` nas migrations).

| Data | Proposta da sessão | Objeção | Caminho escolhido |
|---|---|---|---|
| 2026-10-20 | Atribuir a escolha da estrutura plana ao usuário e sugerir [[Package Python\|package]] | A estrutura plana não tinha sido escolhida | A sessão tirou a conclusão do lugar do `main.py`; package não era necessário |
| 2026-10-21 | Desenho de redes com uma rede dentro da outra | Redes não se aninham | Uma caixa por rede (operadora, wi-fi, loopback, Docker) |
| 2026-10-26 | `check_parent` também conferia se o `note_id` era `None` | A checagem do id não tem a ver com `check_parent` | Duas funções; o `PATCH` confere o próprio id |
| 2026-11-01 | Um workspace fixo por pessoa | Workspace tem de ser modular, um por assunto | Workspace = pasta com `.workspace/`, vários por pessoa ([[Workspace no app]]) |
| 2026-11-02 | `write_workspace` recebia as pastas como parâmetro | Parâmetro sem uso; a ferramenta busca a pasta | Parâmetro removido; o prompt só diz que as pastas existem |
| 2026-11-02 | Loop de ferramentas do lonzo escrito à mão | O vault já previa o `tool_runner` | `tool_runner` da `anthropic` ([[Harness do lonzo]]) |
| 2026-11-02 | Rota `/by-path` | Não segue o padrão REST | A URL nomeia o recurso; o jeito de achar vai na query string |
| 2026-11-03 | A IA só criaria notas dentro do workspace | Essa trava já tinha sido recusada antes | Sem trava de pasta: a IA cria onde quiser |
| 2026-11-05 | Ferramentas devolvendo só o uuid, sem o dicionário de títulos | A IA só sabe o uuid depois de uma busca, e a busca já traz o título | Dicionário de títulos no status das ferramentas (#129) |
| 2026-11-05 | Mais regras no prompt para corrigir o comportamento do modelo | Era tapar buraco de novo | As três branches voltaram ao remoto; a análise partiu do problema e de como o Claude Code o resolve |
| 2026-11-06 | Skills como `.md` no código, num catálogo | Basta uma tabela com pública/privada e dono, e usar copia | Tabela `skills` no lonzo; adicionar sempre copia (#161) |
| 2026-11-06 | Comando `/` mandando um `skill_id` ao backend | O front já tem o texto da skill | Só no front, num bloco `<skill>` (#162) |
| 2026-11-06 | Deixar o `[docs]` ir direto para a `master` | Quase tudo já passa por PR | Ruleset `Master Rules`: a `master` só recebe PR ([[Regras de git]]) |
| 2026-11-08 | Mudança "na última branch" posta na branch local mais nova | A última branch é a ponta dos PRs abertos | Ponta da pilha de PRs |
| 2026-11-09 | Arquivos de contexto no ichiro (tabela `files`, rotas em `/notes/files`) | O ichiro cuida só de notas | Serviço novo **bbmetal** (abaixo) |

## O caso do bbmetal

Os arquivos de contexto de um workspace (PDF, imagem), como nos Projects do claude.ai, precisavam de um lugar para morar.

| | No ichiro (proposta) | Serviço próprio (escolha) |
|---|---|---|
| Metadados | tabela `files` no banco `ichiro`, policy de dono das notas | tabela `files` no banco do bbmetal, com RLS por `owner` |
| Ligação com a pasta | FK e `ON DELETE CASCADE` | coluna `folder_id` sem FK, como o `note_id` da tabela `skills` |
| Onde aparece | na árvore, ao lado das notas | aba Sources, como a aba Skills |
| Custo | ichiro mistura notas e arquivos | mais um container, banco e rota no Caddy (`/api/files/*`); arquivos órfãos quando a pasta some |

- **Argumento da proposta:** separar dividiria a regra de dono entre dois bancos.
- **Por que caiu:** todo serviço já recebe o `X-User-Id` do Caddy e tem banco com RLS. O cascade apagaria só a linha, e os bytes ficariam no S3 nos dois casos.
- **Objeção que sobrou:** separar os arquivos por workspace. Uma coluna `folder_id` resolve: "fontes deste workspace" vira `WHERE folder_id = X`.
- **Como ficou:** SeaweedFS como S3 local, limite de 100 MB por arquivo, bytes do navegador direto para o storage por URL assinada. O lonzo gera um card em `.workspace/kb/` e lê o original quando o card não basta.
- **Revisar se:** a limpeza dos órfãos ficar cara, ou se o arquivo precisar abrir na árvore como uma nota.

Mais sobre bancos separados: [[Bancos dos serviços]].

## O que se repete

- **Desenho maior que o pedido**: parâmetro sem uso, catálogo, `skill_id`, regras no prompt.
- **Contra o que já estava decidido** no vault ou na conversa: `tool_runner`, trava de pasta, estrutura plana.
- **Assunto no serviço errado**: arquivos no ichiro.
- **Conclusão sem conferir**: estrutura plana deduzida do lugar do `main.py`, "última branch" sem olhar os PRs.

Só a trava de pasta e a última branch viraram memória da sessão; o resto ainda não virou regra em [[Regras de resposta]].
