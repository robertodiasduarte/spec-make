# MCP do Make — o que esta skill usa e o que já foi medido

Este arquivo é igual em todas as skills do spec-make. Os nomes das ferramentas são os do
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
| Design | `apps_recommend` · `app-modules_list` · `app-module_get` · `connections_list` · `validate_module_configuration` · `validate_blueprint_schema` · `validate_scenario_interface` | Só módulos que existem; parâmetros conferidos; blueprint validado. A documentação pública do app (`https://apps.make.com/<app>`) é lida na web, uma vez por app ([W1]) |
| Handoff | `environment_get` · `scenarios_get` · `hooks_list` · `data-stores_list` · `connections_list` | Ficha do fluxo para continuar depois: só leitura, 0 operações; nunca lê registros de data store |
| Build | `credential-requests_create` · `validate_*` · `scenarios_create` · `scenarios_set-interface` · `scenarios_activate` · `scenarios_run` · `executions_get` · `executions_get-detail` · `scenarios_interface` · `scenarios_update` · `data-stores_create` · `data-store-records_list` · `scenarios_deactivate` | Criar, testar, ler a execução, ligar o gatilho com OK |

Ler a conta não gasta operação. Executar um fluxo gasta.

## Fatos medidos (teste real de 13/10/2026, plano Core)

1. **Os dois validadores não bastam.** `validate_blueprint_schema` e
   `validate_module_configuration` aprovaram um blueprint que falhou na primeira execução
   (`BundleValidationError: Validation failed for 1 parameter(s)`). O que fecha o teste é a
   execução, nunca a validação.
2. **Interface gravada à parte.** Um fluxo sob demanda que recebe dados (módulo
   `scenario-service:StartSubscenario`) precisa da interface do cenário gravada com
   `scenarios_set-interface` depois de criar. Declarar a entrada só dentro do módulo 1 não basta
   (o teste falha com "Validation failed for 1 parameter(s)"), e os validadores não avisam.
   Não ponha a chave `interface` no blueprint: `validate_blueprint_schema` a recusa ("must NOT
   have additional properties"), embora `scenarios_get` a devolva dentro do blueprint de um
   cenário existente — copiar um cenário existente leva a esse erro.
3. **Só roda se estiver ativo.** `scenarios_run` recusa fluxo inativo. Criar com agendamento
   `on-demand` e ativar é inofensivo: o fluxo só roda quando alguém pede. O que precisa do OK do
   pessoa é trocar o agendamento ou ligar o gatilho real.
4. **O detalhe da falha pode vir vazio.** `executions_get-detail` de uma falha de validação
   trouxe só a mensagem genérica, sem dizer o módulo nem o parâmetro. Por isso a skill de build
   tem um roteiro de diagnóstico próprio.
5. **Fluxo confidencial não guarda o passo a passo.** Com `confidential: true`, o detalhe da
   execução traz só o resultado final. O spec-make liga essa opção sempre, porque o escritório
   trata dado de cliente; o diagnóstico não depende do passo a passo.
6. **App nativo primeiro.** `apps_recommend` costuma achar um app nativo onde a primeira ideia
   seria uma chamada HTTP genérica. Prefira o nativo e diga à pessoa qual escolheu.
7. **App não instalado.** `scenarios_create` pode pedir confirmação quando o fluxo usa um app
   ainda não instalado na conta. Diga à pessoa o que vai ser instalado antes de confirmar.
8. **Apps embutidos não aparecem na recomendação.** `apps_recommend` lista apps de terceiros e
   deixa de fora os embutidos do Make — data store (`datastore`), HTTP (`http`), roteador e
   iterador (`builtin`). Para guardar dado dentro do Make, por exemplo, ela sugeriu CRMs; o
   certo era `app-modules_list(appName: "datastore", appVersion: 1)`. Para guardar linhas numa tabela de um projeto
   Supabase, ela acha o app nativo `supabase` (medido em 15/10/2026).
9. **Módulo que depende de outro recurso.** O `datastore:AddRecord` só mostra os campos depois
   que o data store existe (o esquema vem da estrutura dele). Valide esse módulo na etapa 4,
   depois de criar o data store.
10. **Custo do teste.** No teste medido, cada execução gastou 1 operação (só o módulo do app
   conta; entrada e saída do fluxo sob demanda não contam). Informe sempre o custo antes de rodar.

11. **App Supabase (16/10/2026).** O app `supabase` versão 1 tem 12 módulos (não existe versão 2). Os de dados são
   `searchRows`, `createARow`, `upsertARecord`, `getRowsCount` e `deleteRows`; os demais (aviso de mudança de tabela,
   chamada de API e armazenamento de arquivos) ficam fora do kit. Não existem `searchRecords`, `createARecord` nem
   `updateARecord`.
12. **Filtro do `searchRows`.** Operadores por tipo: texto (igual, diferente, contém), número, data e verdadeiro/falso
   (igual, diferente). Não há "é vazio": o pendente é uma coluna verdadeiro/falso. O módulo devolve várias linhas, uma por
   passagem pelos módulos seguintes, e o limite padrão é 10.
13. **Conexão do app Supabase.** Pede o **Project ID** e a **API Key** (a documentação do app aponta Project Settings →
   API Keys → Secret keys), sem outros campos.
14. **Atualizar uma linha.** Não há módulo "atualizar": o `upsertARecord` decide pela chave primária da tabela. O banco
   confere as colunas obrigatórias da linha inteira, então quem marca uma linha como feita regrava a linha toda.
15. **Filtro verdadeiro/falso no blueprint (16/10/2026).** Na condição do `searchRows`, o valor vai em texto
   (`"b": "false"`). Com o booleano `false` o Make ignora a condição: a busca lê qualquer linha (medido: as 3 execuções
   leram 2 linhas e gastaram 7 operações, a fila nunca esvaziou).
16. **Busca sem resultado (16/10/2026).** O `searchRows` sem linha devolve 1 pacote vazio, não zero. O módulo seguinte
   roda com campos vazios (medido: gravação com campo obrigatório vazio falhou e a execução terminou em erro). Um filtro
   "`{{<id da busca>.id}}` existe" no 1º módulo depois da busca para o fluxo ali: a execução gasta 1 operação.

## Conexões e credenciais

Nunca peça chave, senha ou token no chat. Para uma conexão que falta, use
`credential-requests_create`: ela devolve um link em que a própria pessoa autoriza a conexão
dentro do Make. Espere a pessoa dizer que autorizou e confira com `connections_list`.

## O que não fazer com a conta da pessoa

- Não altere nem apague fluxo, data store ou conexão que esta conversa não criou.
- Não ligue agendamento nem gatilho sem o "sim" da pessoa (regra [B2] da skill de build).
- Não rode execução sem dizer antes quantas operações ela gasta.
