# Protocolo da etapa 4 — Build do fluxo

## Abertura

As duas linhas da regra [E1]. Depois: "Vou criar o fluxo na sua conta, testar com a sua amostra e só ligar o gatilho
se você disser sim. Antes de cada gravação eu aviso o que vai acontecer."

**[B1] Ordem das chamadas.** Siga esta ordem; pule só o que não se aplica e diga por quê:

1. `environment_get` — confirmar organização e equipe do DESIGN.
2. `connections_list` — conferir as conexões do DESIGN. Para cada uma que falta: `credential-requests_create` (app e
   módulos do DESIGN), mandar o link, esperar a pessoa autorizar e conferir de novo. Nunca peça chave no chat.
3. `validate_module_configuration` (por módulo) e `validate_blueprint_schema` — o blueprint final, já com as conexões.
   Rode também `scripts/checar_blueprint.py` se o ambiente executar código.
4. `data-stores_create` — só se o DESIGN tiver data store novo (com `data-structures_create` antes). Em seguida,
   valide o módulo que grava nele (`validate_module_configuration` com o id do data store): os campos só aparecem
   depois que ele existe (MCP_MAKE.md, fato 9).
5. `scenarios_create` — com `scheduling: { "type": "on-demand" }`, `confidential: true` e o nome do DESIGN. Se
   pedir confirmação de app não instalado, diga qual app e confirme. Anote o id.
6. `scenarios_set-interface` — se o fluxo recebe dados; confira com `scenarios_interface` que `input` não está vazio.
7. `scenarios_activate` — necessário para rodar; sob demanda, ele só roda quando alguém pede.
8. `scenarios_run` — com os dados da amostra do DEFINE e `responsive: true`. Anote o id da execução.
9. `executions_get-detail` e `executions_get` — resultado e operações gastas.
10. Fluxo que grava: conferir o destino (`data-store-records_list` ou o app) e repetir os passos 8–9 com a mesma
    amostra; a contagem não pode mudar.
11. Recibo, pergunta [B2] e, só com "Ligar agora" ou "sim", `scenarios_update` com o agendamento do DESIGN (ou ligar o
    gatilho real).

## Teste de aceite: dois modos

| Modo do DEFINE | Como rodar |
|---|---|
| Sob demanda com a amostra | `scenarios_run` com `data` = campos da amostra |
| Gatilho real (e-mail, planilha, pasta) | Teste numa **origem de teste**, nunca na caixa, planilha ou pasta real do escritório: um rótulo, aba ou pasta só para o teste, com limite de 1 item por execução no módulo de gatilho. Peça à pessoa para colocar a amostra lá, rode uma vez com `scenarios_run` sem `data`. A origem real só entra depois do teste aprovado **e** da resposta "Ligar agora" na pergunta [B2], com o ponto de partida "a partir de agora" (nunca "todos": isso reprocessaria o histórico); qualquer outra resposta mantém o gatilho na origem de teste |

## Depois do teste

- Aprovado: recibo ([assets/RECIBO_TEMPLATE.md](../assets/RECIBO_TEMPLATE.md)) e [B2].
- Reprovado: [B3] (DIAGNOSTICO.md).
- A pessoa pediu para remover o teste: apague só o que esta conversa criou ([B4]), na ordem desativar → apagar.
