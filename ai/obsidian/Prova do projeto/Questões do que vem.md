---
tags: [noteproject, prova, sync, auth, infra]
---
# Questões do que vem

Conceitos das próximas etapas (M2 login, M3 AWS, M4 edição ao vivo, app desktop), ainda sem código ([[Roadmap]]). Servem para conferir se o porquê de cada peça ficou claro antes de implementar.

## Sync

### 1. Dois dispositivos editam a mesma nota offline. Sem [[CRDT]], o que acontece ao sincronizar? E com?

> [!note]- Resposta
> Sem: quem salva por último ganha, e o outro perde o que digitou. Com: cada caractere tem um id único, e juntar os updates dá o mesmo resultado em qualquer ordem; as duas edições ficam ([[CRDT]]).

### 2. Por que HTTP não basta para a edição ao vivo da M4?

> [!note]- Resposta
> No HTTP só o cliente começa a mensagem. O servidor precisa mandar a mudança assim que outro edita; o [[WebSocket]] deixa uma conexão aberta nos dois sentidos.

### 3. O que o [[Reverse proxy|Caddy]] precisa fazer para um [[WebSocket]] passar por ele?

> [!note]- Resposta
> Repassar o `Upgrade: websocket` e não cortar a conexão parada ([[WebSocket]], #30).

### 4. Um dispositivo ficou offline e perdeu as mensagens do [[WebSocket]]. Como ele se atualiza sem baixar tudo?

> [!note]- Resposta
> Guarda `N`, a última `version` que viu, e pede `version > N`. Com um contador por usuário, uma consulta só acha tudo o que mudou ([[Sync por versão]]).

### 5. Quando o [[Redis pub-sub]] passa a ser necessário?

> [!note]- Resposta
> Com duas ou mais instâncias do sync: cada uma só conhece as próprias conexões e precisa avisar as outras. Com uma só, a memória do processo basta ([[Redis pub-sub]]).

## Auth e AWS

### 6. O deploy por merge precisa entrar na AWS. Por que [[OIDC]] e não uma chave guardada nos segredos do GitHub?

> [!note]- Resposta
> A chave não expira, e quem a vazar entra. Com OIDC, o GitHub emite a cada execução um token assinado ("workflow X do repo Y, branch Z"), que a AWS troca por credenciais temporárias de uma role do [[IAM]] ([[OIDC]]).

### 7. Como se abre um shell na [[EC2]] com a porta 22 fechada?

> [!note]- Resposta
> Pelo [[SSM Session Manager]]: shell pelo console ou CLI da AWS, com acesso pelo [[IAM]] e registrado ([[SSM Session Manager]]).

### 8. Verdadeiro ou falso: um `pg_dump` diário no [[S3]] já garante o [[Backup|backup]].

> [!note]- Resposta
> Falso. Backup nunca restaurado não está provado; o fim da M3 pede um restore num banco vazio ([[Backup]], [[Roadmap]]).

### 9. Por que a infra vai em [[Terraform]] e não em cliques no console?

> [!note]- Resposta
> A infra fica em arquivos versionados e é recriada com um comando ([[Terraform]], [[AWS ou infra própria]]).

### 10. Na M3, o Caddy passa a servir o `dist/` do front. Como o `dist/` entra na imagem dele sem levar o Node?

> [!note]- Resposta
> [[Build multi-stage]]: um estágio com Node gera o `dist/` e é descartado; a imagem final do Caddy copia só a pasta ([[Navegador]], #47).
