---
tags: [noteproject, conceito, infra]
---
# Sandbox

Um servidor que roda código escrito por outra pessoa (ou por uma IA) arrisca tudo o que está nele: banco, chaves de API, arquivos de outros usuários. Um script com erro apaga dados; um malicioso os lê e manda para fora.

- **Sandbox**: ambiente fechado onde o código roda sem alcançar o resto da máquina.
- O código só vê o que recebe como entrada e só devolve texto como saída.
- Limites típicos: sem rede, sem disco de fora, memória e tempo máximos.

## Como se faz

| Jeito | Isolamento | Custo |
|---|---|---|
| [[Container]] descartável | o processo vê só a imagem; divide o kernel com a máquina | baixo; o mais comum |
| gVisor | um kernel de mentira entre o container e o real | médio |
| Firecracker (micro-VM) | máquina virtual pequena, kernel próprio | maior; usado para código de estranhos |
| Web Worker | JavaScript isolado dentro do navegador | roda no aparelho, não no servidor |

Um container descartável, por exemplo:

```bash
docker run --rm --network none --memory 256m --cpus 0.5 \
    -i python:3.14-slim timeout 10 python - < script.py
```

- `--rm`: o container é apagado ao terminar; nada sobra para a próxima execução.
- `--network none`: o código não chama a rede.
- `python -` lê o código pelo stdin: o script não precisa existir como arquivo no servidor.
- Container não é isolamento perfeito: uma falha no kernel vale para todos os containers. Contra código de qualquer pessoa da internet, gVisor ou micro-VM. *(geral)*

> [!example] No NoteProject
> Scripts do `.workspace/`, escritos pela pessoa ou pela IA, rodariam assim ([[Workspace no app#Scripts]]).
