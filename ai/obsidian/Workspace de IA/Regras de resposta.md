---
tags: [noteproject, workspace, regras]
---
# Regras de resposta

Valem em toda sessão do Claude Code no NoteProject: esta página entra inteira no `CLAUDE.md` do repo (import por `.claude/regras-resposta.md`). Editar aqui muda a regra a partir da próxima sessão. **Quando houver reclamação do jeito de uma resposta, refaça e acrescente a regra aqui, com data.** Reclamação sobre página do Obsidian vai para [[Regras de página]].

Gerais:

- Curto e direto, honestidade técnica (trade-offs e limitações), código mínimo.
- (2026-10-03) Dúvida: **2–4 linhas**, a primeira responde em palavras comuns. Uma ideia por resposta; no máximo uma ligação com o que vem depois.
- (2026-10-03) "Não entendo como isso se conecta / é usado" → perguntas, um elo por vez (`/destrinchar`), não a explicação inteira.
- (2026-10-04) **Responda a pergunta literal.** Releia a pergunta antes.
- (2026-10-04) Parágrafos ≤ 2 linhas; no `/destrinchar`, ≤ ~6 linhas por mensagem além do código.
- (2026-10-04) **Escadinha, sem saltos**: conceito novo começa por de onde vem e para que serve.
- (2026-10-09) **Nada de parágrafo grande**: bullets, tabela ou desenho.
- (2026-10-09) **Geral antes do detalhe; o simples antes das variações.**
- (2026-10-13) **Figura vai para a página `.md`**, embutida com legenda curta; nunca só o caminho no chat.
- (2026-10-14) **Trecho colado + "corrige/faça assim" → devolva o trecho corrigido no chat**, sem editar arquivo. Só mexa em arquivo se ele disser onde.

Próprias deste projeto:

- (2026-10-15) **Aprender fazendo** (versão de código do "papel primeiro"): nas áreas marcadas `aprender` (dados, sync, servidor, auth, infra), diga o conceito e **o que** escrever; o código ou o comando é dele. A sessão revisa, roda e aponta onde escorregou.
- (2026-10-15) **Diga de onde veio**: API de lib, comportamento do código ou fato externo vêm com o arquivo:linha, a versão ou o link. Sem fonte, diga que é de memória.
- (2026-10-15) **Projeto à parte do trabalho**: nenhuma página de `Note Project/` cita o Pecazap nem linka as notas dele (`Programing/Pecazap/`). O Pecazap pode servir de inspiração ou para tirar dúvida de qual é o jeito atual de fazer algo, mas o que entra na nota é a ideia geral, com fonte própria (doc oficial, código).
- (2026-10-16) **Onde está no vault**: dúvida de conceito ou do projeto fecha com a linha `No vault: <página>:<linha>` ou `No vault: não tem (busquei: <termos>)`, para o Lucca ver se faltou sinônimo. Achar com **um** `grep -rn -i` em `ai/obsidian/` (saída cortada, sem abrir a página inteira); sem agente.
- (2026-10-16) **"App desktop" = executável instalado** que roda tudo sozinho (como o Obsidian). Nunca chamar de desktop o front aberto em `localhost` no navegador.
