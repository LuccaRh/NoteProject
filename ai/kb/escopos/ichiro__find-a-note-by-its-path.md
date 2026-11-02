---
id: ichiro/find-a-note-by-its-path
nome: Nota pelo caminho de títulos (issue #91)
areas: [dados, servidor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `GET /notes/by-path?path=a/b/c&parent_id=X` devolve a nota (ou pasta) no fim do caminho,
   a partir de `X` (a raiz sem `parent_id`), numa consulta só (`WITH RECURSIVE` que desce um
   nome por nível); nome que falta no caminho → 404; caminho sem nomes (`//`) → 422.
2. Testes (caminho de uma pasta, da raiz com barras sobrando, que acaba numa pasta, que falta,
   vazio); versão do ichiro 0.9.0 → 0.10.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- (2026-11-02, pedido do Lucca, escrito pela sessão) Empilhada na #90: com título único por
  pasta, um caminho aponta para uma nota só. Vem do lonzo: o `folder()` das ferramentas desce
  pasta por pasta, uma chamada HTTP por nível.
- Endpoint, não coluna `path`: a coluna teria de ser reescrita em todos os descendentes a cada
  renomear ou mover; a consulta recursiva calcula na hora.
- A rota fica antes de `/{note_id}`, senão o FastAPI tentaria ler `by-path` como UUID.
- No Postgres, índice de array sobre um `CAST` precisa de parênteses:
  `(CAST(:names AS text[]))[1]` (sem eles, `syntax error at or near "["`, conferido).

## Fora (vira outra branch)
- Título com `/`: hoje é aceito e não dá para achar pelo caminho; barrar ou escapar fica para
  depois.
- Criar as pastas que faltam pelo caminho (`mkdir -p`): fica no lonzo.
