---
tags: [noteproject, ia, editor]
---
# Figuras geradas

No workspace, a IA nunca desenha pixel. Ela escreve YAML para o `tools/diagrama.py` (que vira draw.io/SVG), monta o circuito no Falstad ou gera o gráfico com MATLAB/Python. A figura vai embutida na página (regra de 2026-10-13).

No app seria o mesmo caminho: a IA escreve a **receita** e o [[O daemon notesd|daemon]] gera a **imagem**.

## Tipos

| Tipo | Receita | Quem gera | Sai |
|---|---|---|---|
| fluxo, estados | Mermaid | o próprio editor | SVG, na hora |
| diagrama de blocos | YAML do `diagrama.py` | [[O daemon notesd\|daemon]] | SVG |
| gráfico | script Python (matplotlib) | [[O daemon notesd\|daemon]], em processo isolado | PNG |
| circuito | link do Falstad | [[O daemon notesd\|daemon]] (tira o print) | PNG + link |
| imagem colada | — | você | PNG |

## Onde fica cada coisa

- Na nota fica só o [[Marcador no texto, conteúdo fora|marcador]] `![[fig-3f2a.svg]]`.
- No [[O daemon notesd|daemon]] fica a tabela `figuras`: a receita, o arquivo gerado e a nota dona.
- Clicar na figura abre a receita, para editar e gerar de novo.
- Pedir à IA "põe o eixo em dB" manda só a receita, não a imagem.

## Por que

- **Menos tokens**: a receita é um texto curto. Uma imagem feita pela IA custaria mais e não daria para editar.
- **Número conferido**: o script que desenha o gráfico é a própria conta, então o gráfico confere o número que o texto afirma.
- **Mesmos geradores do workspace**: dá para reaproveitar o `diagrama.py` em vez de reescrever.

## Cuidado

Script gerado pela IA é código rodando na sua máquina:

- rodar em processo separado, com tempo limite e sem rede (ou no [[Container e Docker Compose|container]] do `docker-compose.yml`);
- mostrar o script antes da primeira execução.
