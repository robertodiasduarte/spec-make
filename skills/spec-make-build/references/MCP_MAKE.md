# MCP do Make — o que esta skill usa e o que já foi medido

Este arquivo é igual nas quatro skills do spec-make. Os nomes das ferramentas são os do
servidor MCP oficial do Make e valem em qualquer agente que o tenha conectado.

## Como saber se a conversa tem o MCP do Make

Peça a lista de ferramentas disponíveis. A conversa tem o MCP do Make quando aparecem
ferramentas com nomes como `environment_get`, `scenarios_list` e `apps_recommend`. Ela pode
**gravar** quando aparecem também `scenarios_create`, `scenarios_activate` e `scenarios_run`.

Sem nenhuma delas, siga a regra **[M1]** da skill (trabalho no papel).

## Primeira chamada de qualquer etapa

`environment_get` devolve a zona, a organização e a equipe. Quase toda outra ferramenta exige o
`organizationId` e o `teamId` que vêm daqui. Anote os dois no documento da etapa.

Se houver mais de uma organização ou equipe, pergunte uma vez qual usar e anote.

## Ferramentas por etapa

| Etapa | Ferramentas | Para quê |
|---|---|---|
| Brainstorm | `environment_get` · `organizations_list` · `connections_list` · `apps_recommend` | Plano e limites da conta; o que já está conectado; se existe app nativo para cada passo |
| Define | `environment_get` · `organizations_list` | Orçamento de operações por mês contra o plano |
| Design | `apps_recommend` · `app-modules_list` · `app-module_get` · `connections_list` · `validate_module_configuration` · `validate_blueprint_schema` · `validate_scenario_interface` | Só módulos que existem; parâmetros conferidos; blueprint validado |
| Build | `credential-requests_create` · `validate_*` · `scenarios_create` · `scenarios_set-interface` · `scenarios_activate` · `scenarios_run` · `executions_get` · `executions_get-detail` · `scenarios_interface` · `scenarios_update` · `data-stores_create` · `data-store-records_list` · `scenarios_deactivate` | Criar, testar, ler a execução, ligar o gatilho com OK |

Ler a conta não gasta operação. Executar um fluxo gasta.

## Fatos medidos (teste real de 13/10/2026, plano Core)

1. **Os dois validadores não bastam.** `validate_blueprint_schema` e
   `validate_module_configuration` aprovaram um blueprint que falhou na primeira execução
   (`BundleValidationError: Validation failed for 1 parameter(s)`). O que fecha o teste é a
   execução, nunca a validação.
2. **Interface no topo.** Um fluxo sob demanda que recebe dados (módulo
   `scenario-service:StartSubscenario`) precisa da interface de entrada em
   `blueprint.interface.input`, ou gravada depois com `scenarios_set-interface`. Declarar a
   entrada só dentro do módulo 1 não basta, e os validadores não avisam.
3. **Só roda se estiver ativo.** `scenarios_run` recusa fluxo inativo. Criar com agendamento
   `on-demand` e ativar é inofensivo: o fluxo só roda quando alguém pede. O que precisa do OK do
   aluno é trocar o agendamento ou ligar o gatilho real.
4. **O detalhe da falha pode vir vazio.** `executions_get-detail` de uma falha de validação
   trouxe só a mensagem genérica, sem dizer o módulo nem o parâmetro. Por isso a skill de build
   tem um roteiro de diagnóstico próprio.
5. **Fluxo confidencial não guarda o passo a passo.** Com `confidential: true`, o detalhe da
   execução traz só o resultado final. O spec-make liga essa opção sempre, porque o escritório
   trata dado de cliente; o diagnóstico não depende do passo a passo.
6. **App nativo primeiro.** `apps_recommend` costuma achar um app nativo onde a primeira ideia
   seria uma chamada HTTP genérica. Prefira o nativo e diga ao aluno qual escolheu.
7. **App não instalado.** `scenarios_create` pode pedir confirmação quando o fluxo usa um app
   ainda não instalado na conta. Diga ao aluno o que vai ser instalado antes de confirmar.
8. **Custo do teste.** No teste medido, cada execução gastou 1 operação (só o módulo do app
   conta; entrada e saída do fluxo sob demanda não contam). Informe sempre o custo antes de rodar.

## Conexões e credenciais

Nunca peça chave, senha ou token no chat. Para uma conexão que falta, use
`credential-requests_create`: ela devolve um link em que o próprio aluno autoriza a conexão
dentro do Make. Espere o aluno dizer que autorizou e confira com `connections_list`.

## O que não fazer com a conta do aluno

- Não altere nem apague fluxo, data store ou conexão que esta conversa não criou.
- Não ligue agendamento nem gatilho sem o "sim" do aluno (regra [B2] da skill de build).
- Não rode execução sem dizer antes quantas operações ela gasta.
