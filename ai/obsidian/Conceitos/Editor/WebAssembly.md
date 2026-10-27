---
tags: [noteproject, conceito, cliente-api]
---
# WebAssembly

O navegador só sabia executar JavaScript. Programas escritos em C, C++ ou Rust (um banco de dados, um decodificador de vídeo) não rodavam numa página sem ser reescritos.

WebAssembly (WASM) é um formato de código compilado que o navegador executa quase na velocidade de um programa nativo. O programa em C é compilado para `.wasm` e roda dentro da página.

## Como funciona

1. O código em C/Rust é compilado para um arquivo `.wasm`.
2. A página baixa o `.wasm`, e o JavaScript o carrega e chama as funções dele.
3. O WASM roda isolado: não abre arquivo nem rede sozinho; só faz o que o JavaScript entrega.

## Para que serve

| Uso | Exemplo |
|---|---|
| banco de dados na página | [[SQLite]] compilado, guardando dados no navegador (OPFS) |
| código pesado | edição de imagem, vídeo, modelos de IA |
| reaproveitar uma biblioteca nativa | a mesma lib em C no servidor e no navegador |

> [!example] No NoteProject
> SQLite em WASM é a alternativa à [[UI otimista]] comparada em [[Navegador]].

Doc: [MDN — WebAssembly](https://developer.mozilla.org/en-US/docs/WebAssembly).
