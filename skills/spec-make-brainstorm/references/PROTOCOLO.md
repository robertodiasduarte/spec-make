# Protocolo da etapa 1 — Brainstorm do fluxo

## 1. Abertura e pré-requisitos — regra [E2]

Comece pela linha de versão e pelo mapa da regra [E1]. Depois, em 4 a 6 linhas: "O spec-make leva uma rotina do
escritório até um fluxo funcionando no Make, em 4 etapas — Brainstorm, Define, Design e Build — e uma ficha para
continuar depois (Handoff). No fim, você tem o fluxo testado na sua conta, o recibo do teste e as fichas. Para isso,
precisamos de 3 coisas: sua conta no Make, o conector do Make ligado aqui com as ferramentas que gravam e uma amostra da
rotina sem dado pessoal real. Nesta etapa nada é criado na conta."

Confira pelo MCP o que dá e mostre 1 linha por pré-requisito, com o ícone e o estado em palavras (✅ ok · ⚠️ falta · a
confirmar). Faltando algum, mostre o como resolver abaixo e siga a conversa. A resposta termina com uma pergunta só:
qual rotina a pessoa quer automatizar.

### Conector ausente

1. No seu assistente, abra as configurações e procure Conectores (no Claude) ou Aplicativos e conectores (no ChatGPT);
   o nome do menu muda com a versão do app.
2. Escolha o Make, entre com a sua conta do Make e permita as ferramentas que criam, ativam e rodam cenários.
3. Abra uma conversa nova e pergunte: "Liste as ferramentas do Make que você tem e diga se consegue criar, ativar e
   rodar um cenário." Deu certo quando aparecem criar, ativar e rodar.

A conversa segue no papel enquanto isso ([M1]): o que depende da conta fica "a confirmar na conta".

### Conector só de leitura

1. Nas configurações do conector do Make, ligue as ferramentas que gravam (criar, ativar e rodar cenários); em alguns
   apps é preciso desconectar e conectar de novo para elas aparecerem.
2. Confira com a mesma pergunta do caso acima.

A conversa segue: as etapas 1 a 3 só leem a conta; só a etapa 4 precisa gravar.

### Conexão faltando

1. Agora, nada: a etapa 4 manda um link de autorização do próprio Make para cada app que falta.
2. Quando o link chegar, abra, entre com a conta do app e autorize. Nunca cole senha ou chave no chat.

A conversa segue; a tabela de viabilidade marca o que falta autorizar.

### Sem amostra

1. Escolha um caso real da rotina e troque tudo que é pessoal por dado inventado, ou use dado público (o CNPJ de uma
   companhia aberta, por exemplo).
2. Anote o resultado que você espera com essa amostra: os valores que devem aparecer e onde.

A conversa segue; a amostra pode chegar até o passo 4 do mapa.

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
3. Módulo oficial primeiro ([N1]): HTTP genérico só quando o app não tiver módulo para a operação, com o motivo
   escrito ("o app <X> não tem módulo para <operação> — conferido em `app-modules_list` em <data>").
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
