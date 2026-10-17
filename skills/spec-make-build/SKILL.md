---
name: spec-make-build
license: MIT
description: "Conduz a etapa 4 de 4 do spec-make: cria na conta do Make, pelo MCP do Make, o fluxo desenhado no DESIGN — pede as conexões por link de autorização, cria o fluxo sob demanda e confidencial, roda o teste de aceite do DEFINE com a amostra, lê o resultado, diz o custo em operações e só liga o gatilho com o 'sim' da pessoa; entrega o recibo e a ficha do fluxo. Use quando a pessoa anexar BRAINSTORM, DEFINE e DESIGN de um fluxo do Make e pedir para criá-lo. Não redesenha o fluxo (spec-make-design), não altera nem apaga fluxo que não criou e não escreve prompt de IA sem o contrato do DESIGN (prompt-builder-by-rdd). Período de consulta e de cálculo: não se aplicam."
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: "1.4.0"
  updated: "2026-10"
---

# spec-make — Etapa 4: Build do fluxo

Na primeira resposta desta skill, comece com a linha de versão, uma vez só:
`spec-make-build v1.4.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/spec-make/releases/latest`
Em seguida, e em toda resposta, o mapa de posição ([E1]). A conversa segue
[references/CONDUCAO.md](references/CONDUCAO.md): mapa, glossário, pergunta de decisão, alerta e bloqueios.

## Quick start

1. Receba BRAINSTORM, DEFINE e DESIGN. Sem o DESIGN: [A3] de references/CONDUCAO.md. Liste no começo os alertas aceitos
   das etapas anteriores ([A2]).
2. Confira se a conversa tem o MCP do Make com ferramentas de gravação ([references/MCP_MAKE.md](references/MCP_MAKE.md)). Sem elas, siga **[M1]**.
3. Confira **[P1]** e **[N1]**; com Supabase, **[B7]** ([references/SUPABASE.md](references/SUPABASE.md)). O que para o
   build está em **[B8]**; o resto vira alerta.
4. Siga a ordem **[B1]** ([references/PROTOCOLO.md](references/PROTOCOLO.md)), avisando antes de gravar ou rodar **[B5]**.
5. Rode o teste de aceite do DEFINE e compare com o resultado esperado.
6. Se falhar, siga **[B3]** ([references/DIAGNOSTICO.md](references/DIAGNOSTICO.md)).
7. Passou: entregue o recibo ([assets/RECIBO_TEMPLATE.md](assets/RECIBO_TEMPLATE.md)) e faça a pergunta **[B2]**.
8. Entregue `FICHA_DO_FLUXO_<FLUXO>.md` ([assets/FICHA_DO_FLUXO_TEMPLATE.md](assets/FICHA_DO_FLUXO_TEMPLATE.md)) e `HANDOFF_<FLUXO>.md` (skill `spec-make-handoff`) e feche com **[E1]**.

## Quando usar / Quando não usar

Usar quando o fluxo já tem BRAINSTORM, DEFINE e DESIGN e a pessoa quer vê-lo funcionando na conta dela. Usar também
para implementar algo novo num fluxo que já está na conta, com o `HANDOFF_<FLUXO>.md` anexado (**[B6]**).

Sem algum dos três documentos, siga o [A3]. Não usar para mudar o desenho: se o teste mostrar que o desenho está errado
além do que o [B3] corrige: alerta [A1] — corrigir aqui deixa o DESIGN desatualizado; recomende a etapa 3, com o comando
pronto. Não mexe em fluxo, data store ou conexão que esta conversa não criou.

## Dados necessários

- `BRAINSTORM_<FLUXO>.md`, `DEFINE_<FLUXO>.md`, `DESIGN_<FLUXO>.md` e o blueprint.
- O teste de aceite do DEFINE (amostra sem dado pessoal real, resultado esperado, segunda execução se grava).
- `organizationId` e `teamId`.
- O "sim" da pessoa para cada gravação na conta e para ligar o gatilho.
- `HANDOFF_<FLUXO>.md`, quando a conversa retoma um fluxo que já existe na conta ([B6]).

## Procedimento passo a passo

1. **Conferência de entrada.** Três documentos presentes ([A3]); liste no começo os alertas aceitos das etapas
   anteriores ([A2]); blueprint com [C1]; [P1], [N1] e [B8] conferidos.
2. **Ordem [B1].** Siga PROTOCOLO.md: conta → conexões → validação → criar → interface → ativar → rodar → ler.
3. **Aviso [B5]** antes de criar e antes de cada execução.
4. **Prompts.** [P1]: gere os prompts do inventário e coloque o texto no módulo de IA antes de criar o fluxo.
5. **Teste de aceite.** Rode como o DEFINE manda. Fluxo que grava: rode a mesma amostra uma segunda vez e confira
   que a contagem de registros não mudou.
6. **Resultado.** Compare valor a valor com o esperado e mostre em linguagem de escritório ("a razão social apareceu
   na tabela de clientes: …").
7. **Falha.** [B3].
8. **Recibo e gatilho.** Recibo com operações gastas e os alertas aceitos que ficaram pendentes ([A2]); depois, a
   pergunta [B2].
9. **Fichas.** Preencha a ficha do fluxo e o handoff — `HANDOFF_<FLUXO>.md` pela skill `spec-make-handoff`, com os ids
   lidos agora e esta sessão no histórico — e feche com [E1]. Sem a skill de handoff instalada, diga isso em uma frase e
   indique o download; a ficha do fluxo sai do mesmo jeito. Antes das fichas, gere as skills do inventário ([P1]); a
   ficha os repete na seção `Alertas aceitos` ([A2]).

**[B2] Pergunta do gatilho.** Depois do teste aprovado, faça uma única pergunta dizendo o estado de agora e o que
muda: "Hoje o fluxo só roda quando você pede. Ligo para {o gatilho do DESIGN: rodar todo dia às 8h / quando chegar
e-mail}?" com duas opções: "Ligar agora" e "Deixar só sob demanda". Só troque o agendamento (`scenarios_update` com
`scheduling` diferente de `on-demand`) ou ligue o gatilho real depois de a pessoa responder "Ligar agora" ou "sim".
Qualquer outra resposta, ou nenhuma, mantém o fluxo sob demanda, sem agenda nem webhook ligados, e a ficha registra
"aguardando OK para ligar o gatilho".

**[B4] Só o que você criou.** Nunca chame `scenarios_update`, `scenarios_delete`, `scenarios_deactivate`,
`data-stores_delete` ou qualquer alteração em fluxo, data store ou conexão que esta conversa não criou. Para mudar um
fluxo antigo da pessoa, crie um novo com outro nome e diga isso a ela.

**[B5] Antes de gravar.** Antes de criar qualquer coisa na conta e antes de cada execução, diga em uma frase o que
vai acontecer e o custo: "Vou criar o fluxo na sua conta, sob demanda e sem ligar o gatilho." · "Vou rodar o teste com
a sua amostra: gasta cerca de {n} operações das {limite} do seu plano no mês."

**[B6] Custódia pela ficha.** Com `HANDOFF_<FLUXO>.md` anexo, os recursos listados como `desta família` contam como
criados por esta conversa para [B4] — e só eles, e só depois de conferir a conta. Primeiro leia `scenarios_get` de cada
parte e compare o `lastEdit` com o da ficha: se for diferente, diga em 1 frase os dois horários ("editado no Make depois
da ficha") e faça o alerta [A1]: a mudança pode apagar o que alguém fez no Make depois da ficha; siga só depois de a
pessoa escolher "Seguir assim e registrar o alerta". Depois releia `data-stores_list` e `hooks_list` e recalcule a custódia
pelos `scenarioUsages` e `scenarioId` de agora: recurso que ganhou uso fora da família passa a `compartilhado com N
cenários`, e você diz isso à pessoa. Só então chame `scenarios_update`, `scenarios_set-interface`, `data-stores_update`
ou `hooks_update`, com o aviso [B5]. Recurso `compartilhado com N cenários`: só ler e acrescentar registro — nunca
chame `data-stores_delete`, `data-stores_update` de estrutura nem `hooks_delete` sobre ele; ofereça criar um data store
novo só para este fluxo. Recurso ausente da ficha ou `fora do spec-make`: [B4] como sempre.

**[B7] Fluxo com Supabase.** Se o DESIGN toca Supabase (app `supabase`, `supabase-management`, `postgres` ou HTTP para
o endereço de um projeto Supabase, em qualquer caminho), confira antes de gravar: coluna `alcance` preenchida com o
motivo, as tabelas e as operações; seção `Prepare o banco` com o SQL quando o fluxo grava no banco; bloco `Relógio` com
o gatilho e, quando é agenda, o intervalo e a linha de operações paradas na seção `Custo`. Faltando algum: alerta [A1]
antes de qualquer `scenarios_create` — sem eles, ninguém sabe o que a chave alcança, o banco pode não ter as travas e o
custo parado não foi somado.

**[B8] O que para o build.** Pare antes de qualquer `scenarios_create`, sem alerta nem pergunta, em dois casos. (1) Fluxo
com Supabase que usa do app `supabase` algo além de `searchRows`, `createARow`, `upsertARecord`, `getRowsCount` e
`deleteRows`, ou módulo `postgres` ou `supabase-management`, ou HTTP para o projeto, ou gatilho que não seja a agenda do
Make nem sob demanda: fica fora do alcance do kit ([X2]); diga o que falta e indique "Use a skill spec-make-design.".
(2) `scripts/checar_blueprint.py` sai 1 (ERRO) ou 2 (não leu o arquivo: nada foi conferido): não crie o fluxo; diga o
problema e indique a mesma skill. Saída 3 (AVISO): cada aviso vira alerta [A1], menos o aviso de HTTP ([N1]) de módulo
que tem no DESIGN a linha de motivo do [N1] — o design já decidiu. Rode o verificador em todo fluxo; se o ambiente não
executa código, faça a mesma conferência lendo.

**[C1] Confidencial.** O fluxo é criado com `metadata.scenario.confidential: true`. Se o blueprint do DESIGN não
tiver, corrija antes de criar e diga isso.

**[P1] Prompts e skills do fluxo.** Com inventário no DESIGN, gere cada linha `tipo: prompt` com a skill
`prompt-builder-by-rdd`, passando o contrato do DESIGN, e ponha o prompt no módulo de IA antes de criar o fluxo; gere
cada linha `tipo: skill` com a skill `skill-builder-by-rdd` só depois do teste aprovado, quando o cenário já existe com a
interface gravada e a ferramenta MCP dele tem nome; registre na ficha do fluxo, em `Prompts e skills gerados`, o nome, o
tipo e o builder usado. Builder não instalado: mostre o link de instalação
(`https://github.com/robertodiasduarte/skills-by-rdd/releases/latest/download/<builder>.zip`) e siga — para prompt,
escreva um prompt provisório pelo contrato, com alerta [A1] (ficou sem a conferência do builder); para skill, siga sem
ela, com alerta [A1]. Fluxo com módulo de IA e sem inventário de prompts e skills no DESIGN, ou IA que grava sem o aceite
humano [G1] ou sem o registro do aceite [G2]: alerta [A1] antes do `scenarios_create` — sem o contrato o prompt sai sem
conferência, e sem o aceite a IA grava sozinha.

**[N1] Módulo oficial primeiro.** Para cada passo do fluxo, procure primeiro o módulo do próprio app no Make
(`apps_recommend`, depois `app-modules_list` e `app-module_get`) e só depois considere o módulo HTTP genérico
(`http:*`). HTTP só entra com o motivo escrito no documento: "o app <X> não tem módulo para <operação> — conferido em
`app-modules_list` em <data>". HTTP sem esse motivo, ou com módulo oficial disponível: alerta [A1] — a chamada HTTP pede
endereço, cabeçalho e autenticação montados à mão, e o módulo oficial já traz a conexão e os campos. Os apps embutidos do
Make (data store, roteador, entrada sob demanda) não contam como HTTP. Com o Supabase, HTTP fica fora do alcance ([X2]).

**[M1] Sem o conector do Make.** Se a conversa não tiver o MCP do Make com as ferramentas de gravação, avise em uma
frase, entregue o blueprint como arquivo `.json` e os passos para importar no Make (Cenários → Criar → menu "…" →
Importar blueprint), o roteiro do teste de aceite para a pessoa rodar, e marque como "a confirmar na conta" as
conexões a autorizar, o plano e as operações. Não afirme que criou, rodou ou ligou nada.

**[E1] Etapa 4 de 4.** Toda resposta abre com o mapa de posição ([K1] de references/CONDUCAO.md), que começa por
"Etapa 4 de 4 · Build"; a primeira resposta traz antes a linha de versão. O fecho segue [K5] e entrega o recibo
e dois arquivos, `FICHA_DO_FLUXO_<FLUXO>.md` e `HANDOFF_<FLUXO>.md`, pede para salvar os dois e diz: "Pronto: o fluxo
está na sua conta. A ficha diz o que fazer quando ele falhar; o handoff, como continuar depois." Sem a skill de handoff
instalada, entregue só a ficha do fluxo, diga em uma frase que falta a skill `spec-make-handoff` e feche com "Pronto: o
fluxo está na sua conta. A ficha diz o que fazer quando ele falhar."

## Validações e checklist de qualidade

- [ ] Toda resposta com o mapa de posição; alertas aceitos das etapas anteriores listados no começo ([A2])
- [ ] Três documentos ([A3]), [P1], [N1], [B8] e, com Supabase, [B7] conferidos antes de gravar
- [ ] Ordem [B1] seguida; nenhum nome de módulo inventado
- [ ] [B5] antes de criar e antes de cada execução
- [ ] Fluxo criado sob demanda e com `confidential: true`
- [ ] Teste de aceite rodado; resultado comparado valor a valor
- [ ] Fluxo que grava: segunda execução sem registro novo
- [ ] Operações gastas informadas
- [ ] Gatilho ligado só depois de "Ligar agora" ou "sim" ([B2])
- [ ] Nada alterado fora do que esta conversa criou ([B4])
- [ ] Com `HANDOFF` anexo: `lastEdit` e usos conferidos antes de gravar ([B6])
- [ ] Recibo, ficha do fluxo e handoff entregues (sem a skill de handoff: o aviso no lugar do handoff), com os alertas
  aceitos pendentes no recibo e na seção `Alertas aceitos` da ficha

## Tratamento de exceções

- **Teste falhou:** [B3]: até 3 correções sem perguntar; depois, o alerta do [B3].
- **Conexão faltando:** `credential-requests_create` com o app e os módulos do DESIGN; mande o link; espere a pessoa
  dizer que autorizou; confira com `connections_list`.
- **"Scenario is already being executed":** espere a execução em andamento terminar; não rode de novo por cima.
- **O plano não tem operações suficientes no mês:** diga quantas restam (se a conta informar); alerta [A1] — o Make
  interrompe a execução quando a cota acaba.
- **A pessoa pede para apagar o fluxo de teste:** apague só o que esta conversa criou ([B4]).
- **O resultado diverge do esperado, mas o fluxo não deu erro:** trate como falha do teste ([B3]); não declare
  aprovado.

## Examples

**Caso positivo (sintético).** DESIGN do cadastro por CNPJ. A skill avisa ([B5]), cria o data store e o fluxo sob
demanda e confidencial, grava a interface, ativa, roda com o CNPJ da amostra (1 registro, 2 operações), roda de novo
(continua 1 registro), mostra o recibo e pergunta [B2]; a pessoa responde "Deixar só sob demanda"; a ficha registra
"aguardando OK para ligar o gatilho".

**Contraexemplo.** "Use meu fluxo 'Cobrança antiga' e troque a planilha dele." A skill não altera ([B4]): oferece
criar um fluxo novo a partir do DESIGN.

## Inventário do bundle

- `SKILL.md`
- `references/PROTOCOLO.md` — a ordem [B1], chamada a chamada
- `references/DIAGNOSTICO.md` — o roteiro [B3]
- `references/CONDUCAO.md` — mapa de posição, glossário, pergunta de decisão, alerta, alertas aceitos e bloqueios
- `references/MCP_MAKE.md` · `references/COPY.md` · `references/RUNTIME_COMPATIBILITY.md` · `references/SUPABASE.md`
- `assets/RECIBO_TEMPLATE.md` · `assets/FICHA_DO_FLUXO_TEMPLATE.md`
- `scripts/checar_blueprint.py` — confere confidencial, interface, credencial escrita, o Supabase só como banco e o HTTP genérico [N1]; sai 1 com ERRO, 3 só com AVISO (Python 3.9+, sem dependências)
- `manifest.json` · `evals/cases.json`

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
