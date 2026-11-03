---
id: chimchar/keep-host-files-out-of-the-build-context
nome: Tirar node_modules e dist do contexto do build do front (issue #51)
areas: [infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `apps/chimchar/.dockerignore` exclui `node_modules` e `dist`.
2. O contexto do build cai de ~101 MB para ~176 kB (builder legado, `Sending build context`).
3. `docker compose up --build chimchar` continua servindo o Vite (pelo Caddy,
   `https://notes.localhost/`: a 5173 não sai mais para o host); versão 0.8.0 → 0.9.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Escrita pela sessão a pedido do Lucca (label `infrastructure`).
- Com o BuildKit, o Docker já só transfere o que os `COPY` usam (54 kB no build); o ganho
  é no builder legado e a proteção para um `COPY . .` futuro.

## Fora (vira outra branch)
- Nada: o ichiro e o lonzo já têm `.dockerignore`.
