---
tags: [noteproject, conceito, auth]
---
# Hash de senha

Quem invade um banco lê tudo o que está nele, e por isso a senha não pode ficar guardada como foi digitada. Um hash é uma conta de mão única: da senha sai um texto embaralhado, e desse texto não dá para voltar à senha.

- **Conferir**: o servidor aplica a mesma conta à senha digitada e compara com o que guardou. Em nenhum momento precisa da senha original.
- **Salt**: um valor aleatório, diferente por usuário, entra na conta. Duas pessoas com a mesma senha ficam com hashes diferentes, e uma tabela pronta de hashes comuns não serve. O salt fica guardado junto do hash e não é segredo: seu papel é obrigar o atacante a refazer as contas para cada usuário.
- **Lento de propósito**: senha humana é curta e previsível, então o atacante tenta milhões de palpites. Algoritmos como bcrypt, scrypt e Argon2 gastam tempo em cada conta, e isso encarece cada palpite. SHA-256 é rápido demais para senha.

```sql
-- pgcrypto: gen_salt('bf') sorteia o salt do bcrypt
INSERT INTO users (email, password_hash)
VALUES ('a@example.com', crypt('senha', gen_salt('bf')));

-- crypt lê o salt de dentro do hash guardado e refaz a conta
SELECT id FROM users
WHERE email = 'a@example.com'
  AND password_hash = crypt('senha', password_hash);
```

## O que um vazamento revela

Quem copia o banco lê o hash inteiro, e nele estão o algoritmo, o custo e o salt:

```
$2a$06$ Ka2wEoe0DJnD.q5rjkQuBu GHSuG53jQMRh29QRuApUdP8VJxvTp6C
bcrypt, custo 6   salt (22 caracteres)   resultado da conta
```

O algoritmo é público, e a segurança não depende de escondê-lo. O que falta ao atacante é a senha: ele testa uma lista de senhas comuns, faz a conta para cada uma e compara com o hash.

Exemplo: 1 milhão de usuários vazados e uma lista de 10 milhões de senhas, com velocidades medidas em um núcleo de CPU (2026-11-04). O tempo é o pior caso de percorrer a lista.

| Como o banco guarda | Contas por segundo | Quebrar 1 usuário | Testar todos |
|---|---|---|---|
| Senha pura | nenhuma conta | 0 | 0 |
| SHA-256 sem salt | 1,5 milhão | 6,5 s | 6,5 s |
| SHA-256 com salt | 1,5 milhão | 6,5 s | ~75 dias |
| bcrypt custo 6 com salt | ~280 | ~10 h | ~1.100 anos |
| bcrypt custo 12 com salt | ~6 | ~20 dias | ~54 mil anos |

- Sem salt, a lista é calculada uma vez e serve para todos os usuários. O salt não encarece a quebra de um usuário só; ele impede o reaproveitamento das contas.
- A lentidão encarece cada palpite, e o custo do bcrypt regula o quanto: cada ponto a mais dobra o tempo.
- GPU faz essas contas muito mais rápido, sobretudo SHA-256 *(geral)*, então vale a proporção entre as linhas, e os tempos absolutos são um teto.
- Senha fora da lista não cai por esse caminho, qualquer que seja a linha da tabela.

> [!warning] A senha ainda viaja
> O hash protege o que fica guardado. No caminho até o servidor quem protege a senha é o [[TLS]].

> [!example] Um uso
> O `nujabes` confere a senha assim no [[Login no navegador]].
