---
id: ichiro/align-the-uv-version
nome: Mesmo uv na imagem do ichiro, no lonzo e no PC (issue #82)
areas: [infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `apps/ichiro/Dockerfile.dev` copia o uv 0.13.5 (era 0.13.1), a versão do PC que gerou os lockfiles.
2. A imagem do ichiro builda e o `make check-ichiro` passa.
3. Versão do ichiro 0.6.0 → 0.7.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Vem da #74: o `lonzo` nasceu com uv 0.13.5; a CI fixa a mesma versão na branch dele.

## Fora (vira outra branch)
- `version` do `setup-uv` na CI: vai com o `check-lonzo`, na branch do `lonzo`.
