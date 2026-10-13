# Protocolo da etapa 1 — Brainstorm do fluxo

## 1. Abertura

Comece pelas duas linhas da regra [E1] da SKILL.md. Em seguida, uma frase sobre o que acontece nesta etapa:
"Vamos transformar a rotina num documento de ideia e conferir na sua conta do Make o que já existe para ela. Nada é
criado na conta nesta etapa."

## 2. Conta

1. `environment_get`: zona, organização, equipe. Mais de uma? Pergunte qual usar.
2. `organizations_list`: nome do plano (`serviceName`), operações por mês (`license.operations`), intervalo mínimo de
   agendamento em minutos (`license.interval`), se o plano permite pedido de credencial (`license.credentialRequests`),
   execução sob demanda (`license.onDemandScheduling`) e apps premium (`license.premiumApps`).
3. Diga em uma frase o que o plano permite. Exemplo: "Seu plano é o Core: 10.000 operações por mês, agendamento a cada
   1 minuto no mínimo."

## 3. Rotina — perguntas, uma por mensagem

Escolha só as que ainda não foram respondidas:

- O que faz a rotina começar? (chega um e-mail, todo dia 5, uma linha nova numa planilha, você pede)
- O que entra? (um anexo, um número, uma planilha)
- O que sai, e onde fica? (linha numa planilha, e-mail ao cliente, lançamento no ERP)
- Com que frequência e em que volume? (por dia ou por mês)
- Quem confere o resultado hoje?
- O que acontece hoje quando dá errado?
- Quanto tempo leva hoje, por mês? (opcional)

Se a pessoa não souber por onde começar, ofereça estes exemplos, uma linha cada:

1. "Todo dia 5, me avise das contas a pagar que vencem na semana."
2. "Quando chegar e-mail com nota fiscal, guarde o número, o valor e o emitente numa planilha."
3. "Quando eu informar o CNPJ de um cliente novo, busque os dados cadastrais e guarde numa tabela."
4. "Toda sexta, mande aos clientes a lista de documentos que ainda faltam."
5. "Quando um cliente responder o formulário, crie a pasta dele no Drive."
6. "Todo mês, junte os extratos recebidos numa planilha só."

## 4. Viabilidade na conta

Para cada passo do fluxo:

1. `apps_recommend` com a intenção em uma frase ("buscar dados de empresa pelo CNPJ").
2. Considere apenas resultados claramente ligados ao passo; mostre no máximo 3, pelo rótulo do módulo.
3. Prefira app nativo. Use HTTP genérico só quando não houver nativo, e diga isso.
3a. Guardar dado no próprio Make, chamar uma API sem app, dividir o fluxo em caminhos ou repetir para cada item da
    lista: são apps embutidos que a recomendação não mostra — consulte direto `app-modules_list` com `datastore`,
    `http` ou `builtin` (ver MCP_MAKE.md, fato 8).
4. App premium num plano que não permite: avise e ofereça alternativa.

Depois, `connections_list` na equipe. Monte a tabela: passo · app escolhido · já conectado? · o que falta autorizar.
Conexões faltantes serão pedidas no build por link (`credential-requests_create`); nunca peça senha ou chave aqui.

## 5. Amostra

Peça uma amostra que represente um caso real, **sem dado pessoal real** (ver COPY.md). Anote: a amostra, o
resultado esperado com ela e de onde veio (pública ou inventada).

## 6. Abordagens

2 ou 3 jeitos, por exemplo: gatilho por e-mail × planilha que dispara × sob demanda. Para cada um: como funciona,
prós, contras e operações por mês (operações por execução × execuções por mês) contra o limite do plano. Recomende
um, com o motivo.

## 7. Corte

Para cada parte proposta, pergunte se é necessária agora. Registre na tabela de cortes o que saiu e se pode voltar.

## 8. Validação

Dois blocos curtos, cada um seguido de "Confere?":

1. O que o fluxo faz, com quais apps, em que ordem.
2. O que acontece quando algo falha e quem fica sabendo.

## 9. Documento e fecho

Preencha `assets/BRAINSTORM_TEMPLATE.md`. Itens não confirmados ficam como "a confirmar". Entregue como arquivo
`BRAINSTORM_<FLUXO>.md` (nome curto em maiúsculas, sem acento: `BRAINSTORM_CADASTRO_CNPJ.md`). Feche com [E1].
