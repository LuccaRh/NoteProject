---
pacote: dompurify
versao: 3.4.17
fonte: apps/chimchar/node_modules/dompurify/dist/purify.cjs.d.ts
areas: [ui]
---
# dompurify — limpa o HTML das respostas do chat

Card destilado do código instalado (fonte acima). Uso em `apps/chimchar/src/chat/markdown.ts`.

- Esquema de URL fora da lista (`IS_ALLOWED_URI`, `dist/purify.es.mjs:955`) perde o `href`; `note:` é um deles.
- `addHook('uponSanitizeAttribute', (node, event) => ...)` (linha 333 do d.ts): com `event.forceKeepAttr = true` (linha 432) o atributo fica sem passar por essa lista.
- O hook vale para todo `sanitize`, por isso entra uma vez só, no import.
