---
tags: [noteproject, ia, arquitetura]
---
# Sem Claude Code — provedores

O [[MCP — a IA como cliente do daemon|MCP]] supõe o Claude Code instalado. O app é pensado para várias pessoas, que podem não ter o Claude Code ou não querer pagar por IA.

Por isso o app depende da IA o mínimo possível, e cada pessoa escolhe de onde a IA vem: Claude pago ou um modelo aberto grátis.

## Camadas

| Camada | Precisa de | O que funciona |
|---|---|---|
| 0. sem IA | nada | o app inteiro: notas, busca, marcar dúvida (vira anotação), moldes pelo `/`, Mermaid, receitas escritas à mão |
| 1. modelo local | Ollama na máquina | classificar o tema; respostas simples, de qualidade menor; grátis e offline |
| 2. chave de API | conta num provedor, paga por uso | fila de pedidos completa |
| 3. Claude Code | assinatura do Claude, na máquina do worker | fila por `claude -p` + sessões com [[MCP]]; só para o dono da máquina |

- Claude para qualquer pessoa vem pela camada 2, com a chave dela.
- A assinatura (Free, Pro, Max) não pode ser usada por app de terceiro: o token dela vale só no Claude Code e no Claude.ai, e app de terceiro usa chave de API (regra da Anthropic de 2026-02-19, ainda valendo em 2026-07, conferido em 2026-10-18: [WinBuzzer](https://winbuzzer.com/2026/02/19/anthropic-bans-claude-subscription-oauth-in-third-party-apps-xcxwbn/), [pedido de feature](https://claudeissues.com/issue/82266-feature-allow-claude-pro-max-subscription-auth-to-be-used-from-third-party-apps)). `claude -p` no próprio PC, para uso pessoal, continua permitido.
- O servidor [[MCP]] serve a qualquer cliente [[MCP]], não só ao Claude Code.

## No código

- Uma interface só, por exemplo `responder(pacote) -> operacoes`, com uma implementação por provedor: `anthropic`, `ollama`, `claude_cli`. A mesma interface roda no servidor e no [[O daemon notesd|daemon]].
- O provedor é escolhido na config do [[Workspace no app|workspace]] (`modelos.yaml`); o editor não muda. É o mesmo raciocínio de `api.ts` ser a única fronteira de rede do front.
- Sem provedor configurado, o botão `Responder` some; o chip da dúvida continua.
- Os [[Blocos padronizados|moldes]] são JSON validado. Um modelo que erra o formato tem a resposta recusada, e a nota não estraga.

## Onde o worker roda

| Cliente | Worker | Modelo grátis | Chave de API |
|---|---|---|---|
| [[Navegador]] (v1) ⏳ | no servidor, ao lado da api | Ollama não cabe na [[EC2]] pequena *(estimativa, sem medição)* | guardada no servidor, cifrada, uma por conta |
| app desktop ⏳ | no [[O daemon notesd\|daemon]] | Ollama ou llama.cpp no PC | no PC |

- No navegador as perguntas passam pelo servidor; no desktop ficam na máquina.
- A fila sincroniza: um pedido feito no navegador ou no celular pode ser respondido pelo app desktop, com o modelo grátis do PC ([[Fila de pedidos]]).

## Revisar se...

- o servidor rodar numa máquina com memória para um modelo aberto → Ollama também no navegador;
- os termos da Anthropic liberarem a assinatura em app de terceiro → camada 3 para todos.
