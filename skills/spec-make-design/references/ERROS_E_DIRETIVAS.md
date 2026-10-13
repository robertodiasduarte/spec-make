# Erros e diretivas — a skill escolhe, a pessoa decide o negócio

Sem tratamento de erro, um item com problema para o fluxo inteiro e os seguintes não rodam. O Make tem 5 diretivas
para o que fazer quando um módulo falha:

| Diretiva | O que faz | Quando a skill escolhe |
|---|---|---|
| Break | Pausa e tenta de novo depois (intervalo e número de tentativas) | App externo com falha passageira: fora do ar, limite de uso, tempo esgotado |
| Rollback | Marca a execução como falha e segue para o próximo item | Item com problema que não se resolve tentando de novo (dado inválido) |
| Resume | Substitui o resultado por um valor padrão e segue | Existe um valor aceitável ("não encontrado") |
| Ignore | Descarta em silêncio e segue | Quase nunca: esconde erro |
| Commit | Força a execução como sucesso | Quase nunca |

## Como decidir

1. O erro é passageiro? → Break, com 3 tentativas e intervalo de 15 minutos.
2. O erro é do item? → Rollback, e o item vai para uma lista de pendências (planilha ou data store) para alguém ver.
3. Existe valor padrão aceitável para o escritório? → Resume.
4. Ignore e Commit só com motivo escrito no DESIGN.

Atenção: Rollback não desfaz o que já foi gravado em outro sistema. Se o passo anterior gravou, combine com a chave
natural ([G3]) para que tentar de novo não duplique.

## A pergunta à pessoa

Faça só a pergunta de negócio, uma por mensagem, com a recomendação primeiro:

- "Se a Receita não responder: tento de novo em 15 minutos, até 3 vezes, e depois te aviso por e-mail?"
- "Se o CNPJ não existir: gravo como 'não encontrado' e sigo, ou paro e te aviso?"

Registre a resposta e a diretiva no DESIGN.
