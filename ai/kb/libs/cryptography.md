---
pacote: cryptography
versao: 50.0.2
fonte: apps/lonzo/.venv/lib/python3.14/site-packages/cryptography/fernet.py
areas: [ia]
---
# cryptography — cifra da chave da Anthropic (lonzo)

- `Fernet(key)` (33): `key` em base64 de 32 bytes; vem de `Fernet.generate_key()` (54). Valor
  inválido falha no construtor, ou seja, no import de `lonzo/core/cipher.py`.
- `encrypt(data: bytes) -> bytes` (57). `decrypt(token, ttl=None) -> bytes` (86).
- Segredo errado ou token mexido: `InvalidToken` (21).
- `MultiFernet` (173) decifra com várias chaves; serve para trocar o segredo sem perder as salvas.
