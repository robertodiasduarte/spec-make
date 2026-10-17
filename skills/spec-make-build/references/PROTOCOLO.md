# Protocolo da etapa 4 — Build do fluxo

## Abertura

A linha de versão e o mapa da regra [E1], e os alertas aceitos das etapas anteriores ([A2]). Depois: "Vou criar o fluxo na sua conta, testar com a sua amostra e só ligar o gatilho
se você disser sim. Antes de cada gravação eu aviso o que vai acontecer."

**[B1] Ordem das chamadas.** Siga esta ordem; pule só o que não se aplica e diga por quê:

1. `environment_get` — confirmar organização e equipe do DESIGN.
2. `connections_list` — conferir as conexões do DESIGN. Para cada uma que falta: `credential-requests_create` (app e
   módulos do DESIGN), mandar o link, esperar a pessoa autorizar e conferir de novo. Nunca peça chave no chat.
   2b. Fluxo que toca Supabase: confirme com a pessoa que o SQL do `Prepare o banco` rodou sem erro no SQL Editor; o
   teste do passo 10 prova o resto.
3. `validate_module_configuration` (por módulo) e `validate_blueprint_schema` — o blueprint final, já com as conexões.
   Rode também `scripts/checar_blueprint.py`: o verificador roda em todo fluxo; o que fazer com cada saída (0, 1, 2 e 3)
   está no [B8] do SKILL.md.
4. `data-structures_create` e depois `data-stores_create` — só se o DESIGN tiver data store novo. Em seguida,
   valide o módulo que grava nele (`validate_module_configuration` com o id do data store): os campos só aparecem
   depois que ele existe (MCP_MAKE.md, fato 9).
5. `scenarios_create` — com `scheduling: { "type": "on-demand" }`, `confidential: true` e o nome do DESIGN. Se
   pedir confirmação de app não instalado, diga qual app e confirme. Anote o id.
6. `scenarios_set-interface` — se o fluxo recebe dados; confira com `scenarios_interface` que `input` não está vazio.
7. `scenarios_activate` — necessário para rodar; sob demanda, ele só roda quando alguém pede.
8. `scenarios_run` — com os dados da amostra do DEFINE e `responsive: true`. Anote o id da execução.
9. `executions_get-detail` e `executions_get` — resultado e operações gastas.
10. Fluxo que grava: conferir o destino (`data-store-records_list` ou o app) e repetir os passos 8–9 com a mesma
    amostra (gatilho real: tabela abaixo); a contagem não pode mudar e a 2ª execução tem de ter processado o item
    (operações maiores que zero; ela pode gastar menos que a 1ª). Execução que não processou nada também gasta 1
    operação: com fila, confira que a linha nova voltou como `processado = true`. Com fila, rode também uma 3ª execução
    com a fila vazia: ela termina em sucesso e gasta exatamente 1 operação.
11. Recibo, pergunta [B2] e, só com "Ligar agora" ou "sim", `scenarios_update` com o agendamento do DESIGN (ou ligar o
    gatilho real). Fila do Supabase: no mesmo `scenarios_update` tire a condição `TESTE-1` do `searchRows`, rode
    `validate_module_configuration` no módulo editado e confira com `scenarios_get` que o filtro ficou só com
    `processado` igual a `false` — sem isso o fluxo ligado lê só a chave de teste e os pendentes reais ficam parados.

## Teste de aceite: dois modos

| Modo do DEFINE | Como rodar |
|---|---|
| Sob demanda com a amostra | `scenarios_run` com `data` = campos da amostra |
| Gatilho real (e-mail, planilha, pasta) | Teste numa **origem de teste**, nunca na caixa, planilha ou pasta real do escritório: um rótulo, aba ou pasta só para o teste, com limite de 1 item por execução no módulo de gatilho. Peça à pessoa para colocar a amostra lá, rode uma vez com `scenarios_run` sem `data`. Fluxo que grava: a 2ª passada tem de levar ao fluxo um item com a **mesma chave natural** do DESIGN. Chave de conteúdo (chave de acesso da nota, CNPJ, número do documento): ponha na origem de teste um item novo com o mesmo conteúdo (reenvie o e-mail de teste, copie a linha ou o arquivo) — a contagem no destino não pode mudar. Chave que é o id do item na origem (id do e-mail, do arquivo, número da linha): um item novo é outro registro, e um 2º registro aí é o certo; marque o mesmo e-mail de novo como não lido e rode; se o gatilho não o pegar de novo: alerta [A1] — a chave pelo id do item não prova a 2ª passada; recomende trocar, na etapa 3, por uma chave de conteúdo. Em qualquer caso, confira em `executions_get` que a 2ª execução processou o item (operações maiores que zero; ela pode gastar menos que a 1ª): execução que não processou nada não testa nada. (passo 10) A origem real só entra depois do teste aprovado **e** da resposta "Ligar agora" na pergunta [B2], com o ponto de partida "a partir de agora" (nunca "todos": isso reprocessaria o histórico); qualquer outra resposta mantém o gatilho na origem de teste |
| Fila do Supabase (agenda do Make) | **Isole o teste:** use a chave natural `TESTE-1` e acrescente ao filtro do `searchRows` a condição `chave_natural` igual a `TESTE-1` (as duas condições juntas), para o teste nunca ler nem marcar um pendente real; tire essa condição, com `scenarios_update`, junto com a troca do agendamento no "Ligar agora" (passo 11: valide o módulo editado e confira o filtro). A chave do aceite (`chave_do_aceite`) também começa com `TESTE-`: o aceite de teste fica na auditoria (ela não se apaga), mas a view da taxa de correção o ignora; o registro de teste do destino a pessoa apaga com um `delete`. Peça à pessoa 2 INSERTs na fila com a **mesma chave natural de teste** (1 colagem de SQL), rode `scenarios_run` sem `data` e confira que as linhas voltaram como `processado = true` e que o destino tem 1 linha com essa chave. Para a 2ª passagem, 1 INSERT novo com a mesma chave: o destino segue com 1 linha com essa chave, as operações são maiores que zero **e** a linha nova voltou como `processado = true` (um `searchRows` com `processado` igual a `false` e a condição `TESTE-1` volta vazio). Faça ainda a **3ª execução com a fila vazia**: ela termina em sucesso e gasta exatamente 1 operação — prova de que o filtro de pendente vale (com o filtro ignorado a 2ª e a 3ª leem as mesmas linhas e gastam o mesmo que a 1ª) e de que nada roda depois de uma busca vazia. Só com "Ligar agora" na pergunta [B2] você troca o agendamento do DESIGN |

## Depois do teste

- Aprovado: recibo ([assets/RECIBO_TEMPLATE.md](../assets/RECIBO_TEMPLATE.md)) e [B2].
- Reprovado: [B3] (DIAGNOSTICO.md).
- A pessoa pediu para remover o teste: apague só o que esta conversa criou ([B4]), na ordem desativar → apagar.
