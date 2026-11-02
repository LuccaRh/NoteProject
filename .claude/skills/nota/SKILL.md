---
name: nota
description: Escreve ou atualiza páginas do NoteProject no Obsidian (vault Note Project/, cópia ai/obsidian/) — arquitetura, front/back/infra, decisões e trade-offs — seguindo as regras de página, com desenhos draw.io embutidos. Use quando o usuário disser "/nota", "documenta X no obsidian", "faz uma pasta explicando X", "escreve a decisão de X".
argument-hint: "<tema ou pasta>"
---
# /nota <tema>

1. **Leia antes**: `regras.md` (nesta pasta = `Workspace de IA/Regras de página`), `ls -R ai/obsidian/`
   (não repetir página), a página vizinha mais parecida (copiar o estilo) e, para cada área
   envolvida, `ai/np contexto <área>`. Conceitos que o texto cita: `grep -rl` nos títulos de
   `ai/obsidian/` para linkar o que já existe; nada de linkar página de fora do projeto.
2. **Fonte**: estado atual sai do código; plano e porquê, das notas do vault (única fonte
   do projeto). Fato externo que muda decisão (preço, licença, lib descontinuada) → conferir na web
   e citar com data. Sem fonte → *(geral)* no trecho.
3. **Uma pergunta** se o pedido deixa aberto o recorte (pasta inteira ou uma página; para quem).
   Pedido claro → siga.
4. **Escreva** em `ai/obsidian/<Pasta>/`: `00 Mapa — <pasta>.md` com a tabela Página | Ideia, e uma
   ideia por página. Fluxo, camadas, sequência → **desenho**: `/diagrama` com `destino:` na pasta
   `Figuras/` dela e `![[nome.drawio.svg]]` na página, com legenda de uma linha. Mermaid só para
   o que é pequeno demais para valer um desenho.
5. Página nova entra no mapa da pasta e é citada por pelo menos uma outra. `ai/np obsidian`.
6. No chat: lista das páginas e por onde começar. Não cole o conteúdo.
