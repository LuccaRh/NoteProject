---
name: destrinchar
description: Acha a raiz de uma confusão do Lucca sobre um conceito do projeto (sync, CRDT, auth, proxy, deploy...) com perguntas curtas, um elo do raciocínio por vez, e grava a lógica no Obsidian no fim. Use quando ele disser "/destrinchar", "não entendo como isso se conecta", "ainda está confuso", "me pergunta até achar onde eu me perco".
argument-hint: "<conceito ou trecho>"
---
# /destrinchar <conceito>

Diagnóstico socrático: descubra **qual elo** falta, não despeje a explicação.

1. Leia a nota do conceito (`ai/obsidian/`, `Programing/` do vault) e o código onde ele aparece
   (`ai/np contexto <área>`). Base da explicação; nada de cabeça.
2. Monte a **corrente de elos** do conceito até o uso no projeto. Exemplos:
   - HTTP não tem memória ⇒ toda requisição precisa de prova ⇒ token ⇒ onde guardar ⇒ revogar
     ⇒ por que um token por dispositivo.
   - dois dispositivos editam ⇒ ordem das edições diverge ⇒ CRDT comuta ⇒ update idempotente ⇒
     reconectar é seguro ⇒ `version > N` só traz o delta.
   Mostre a corrente numerada e pergunte quais ele já domina.
3. **Um elo por vez**: pergunta concreta e pequena, respondível em uma linha (dois dispositivos,
   três letras; um `curl`; um container). "Não sei" e chute valem.
4. Resposta dele: certa → confirme em uma linha e siga; errada → mostre **onde** escorregou, com
   exemplo pequeno; "não sei" → explique só esse elo e refaça a pergunta.
5. Toda explicação termina com **uma** pergunta de checagem.
6. Fechou um elo que a nota não explicava → grave na página onde o conceito mora, `ai/np obsidian`,
   diga em uma linha onde ficou.
7. Fim da corrente → ofereça o exercício no projeto (`/aprender`, passo 5).

≤ ~6 linhas por mensagem além do bloco de código.
