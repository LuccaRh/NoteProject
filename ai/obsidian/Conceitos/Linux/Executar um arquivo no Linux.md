---
tags: [noteproject, conceito, infra]
---
# Executar um arquivo no Linux

Um programa fica no disco como qualquer outro arquivo: uma sequência de bytes. Para rodar um arquivo, o Linux não olha o nome; ele confere duas coisas: se o arquivo tem licença para ser executado (a permissão `x`) e se o conteúdo está num formato que ele sabe executar.

## Permissão `x`

- Cada arquivo guarda, fora do conteúdo, três permissões: `r` (ler), `w` (escrever) e `x` (executar).
- `ls -l` mostra as três para três públicos: o dono, o grupo do arquivo e os outros usuários.
- `chmod` (*change mode*) muda as permissões: `chmod +x arq` liga a de executar, `chmod -x arq` tira.
- Sem `x`, o Linux recusa com `Permission denied`, seja qual for o conteúdo.

```
$ ls -l /usr/bin/ls
-rwxr-xr-x ...
 └┬┘└┬┘└┬┘
 dono grupo outros
```

## Formato que o Linux sabe executar

Com o `x` ligado, o Linux lê o começo do arquivo para decidir como rodá-lo:

| Começo do arquivo | O que é | Quem executa |
|---|---|---|
| `.ELF` (bytes `7f 45 4c 46`) | programa compilado: cabeçalho + instruções de máquina | a CPU, direto |
| `#!/usr/bin/python3` (*shebang*) | script | o programa escrito depois do `#!`, que recebe o arquivo |
| outra coisa (texto puro) | nada que ele reconheça | ninguém: `Exec format error` |

- **ELF** (*Executable and Linkable Format*): o formato dos programas no Linux. O cabeçalho diz também para qual CPU o programa foi compilado (`x86-64`, ARM).
- O Windows usa outro formato, o PE (o dos `.exe`). Por isso um programa compilado para um sistema não roda no outro.
- A [[Markdown|extensão]] não entra na conta: um `teste.txt` que começa com `#!/usr/bin/python3` roda como Python.

## O plano B do terminal

Quando o Linux recusa com `Exec format error`, o bash tenta de novo: lê o arquivo como uma lista de comandos de shell. Teste com dois arquivos de texto, os dois com `chmod +x`:

```
oi.txt  = "oi mundo"
  pedido direto ao Linux (execv)  →  Exec format error
  ./oi.txt no bash                →  oi: command not found

oi2.txt = echo "rodei!"
  ./oi2.txt no bash               →  rodei!
```

- Um script sem `#!` costuma rodar no terminal e falhar quando outro programa o chama direto, porque esse outro programa não tem o plano B.

Doc: `man 2 execve`, `man 1 chmod`.
