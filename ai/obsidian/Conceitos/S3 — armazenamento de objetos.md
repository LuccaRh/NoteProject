---
tags: [noteproject, conceito, infra]
---
# S3 — armazenamento de objetos

Imagens, snapshots e [[Backup e restore|backups]] são arquivos grandes que não mudam por dentro: são gravados e lidos inteiros. No banco, pesam; no disco da máquina, somem com ela.

- **Armazenamento de objetos**: guarda arquivos (objetos) por uma chave (`snapshots/nota-1.bin`), acessados por API HTTP. Sem pastas de verdade nem edição parcial.
- **S3**: o da AWS. Paga por GB guardado; *bucket* vazio não custa nada.

- Padrão comum: o banco guarda só a chave do objeto; o conteúdo fica no bucket.
- Uma máquina grava no bucket com a role dela no [[IAM]], sem chave guardada.

> [!example] No NoteProject
> Snapshots do [[CRDT e Yjs|Yjs]], imagens e backups no S3; no Postgres, só a chave ([[Back — daemon e servidor]]).

Doc: [Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html).
