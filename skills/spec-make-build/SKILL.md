---
name: spec-make-build
license: MIT
description: "Conduz a etapa 4 de 4 do spec-make: cria na conta do Make, pelo MCP do Make, o fluxo desenhado no DESIGN — pede as conexões por link de autorização, cria o fluxo sob demanda e confidencial, roda o teste de aceite do DEFINE com a amostra, lê o resultado, diz o custo em operações e só liga o gatilho com o 'sim' da pessoa; entrega o recibo e a ficha do fluxo. Use quando a pessoa anexar BRAINSTORM, DEFINE e DESIGN de um fluxo do Make e pedir para criá-lo. Não redesenha o fluxo (spec-make-design), não altera nem apaga fluxo que não criou e não escreve prompt de IA sem o contrato do DESIGN (sdd-prompt-builder). Período de consulta e de cálculo: não se aplicam."
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: "1.0.0"
  updated: "2026-10"
---

# spec-make — Etapa 4: Build do fluxo

Na primeira resposta desta skill, comece com estas duas linhas, uma vez só:
`spec-make-build v1.0.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/spec-make/releases/latest`
`spec-make · Etapa 4 de 4 — Build`

## Quick start

1. Receba BRAINSTORM, DEFINE e DESIGN. Sem o DESIGN, indique a skill `spec-make-design`.
2. Confira se a conversa tem o MCP do Make com ferramentas de gravação ([references/MCP_MAKE.md](references/MCP_MAKE.md)). Sem elas, siga **[M1]**.
3. Confira [P1]: fluxo com módulo de IA sem inventário de prompts no DESIGN ⇒ pare antes de criar.
4. Siga a ordem **[B1]** ([references/PROTOCOLO.md](references/PROTOCOLO.md)), avisando antes de gravar ou rodar **[B5]**.
5. Rode o teste de aceite do DEFINE e compare com o resultado esperado.
6. Se falhar, siga **[B3]** ([references/DIAGNOSTICO.md](references/DIAGNOSTICO.md)).
7. Passou: entregue o recibo ([assets/RECIBO_TEMPLATE.md](assets/RECIBO_TEMPLATE.md)) e faça a pergunta **[B2]**.
8. Entregue `FICHA_DO_FLUXO_<FLUXO>.md` ([assets/FICHA_DO_FLUXO_TEMPLATE.md](assets/FICHA_DO_FLUXO_TEMPLATE.md)) e feche com **[E1]**.

## Quando usar / Quando não usar

Usar quando o fluxo já tem BRAINSTORM, DEFINE e DESIGN e a pessoa quer vê-lo funcionando na conta dela.

Não usar sem os três documentos. Não usar para mudar o desenho: se o teste mostrar que o desenho está errado, volte à
skill `spec-make-design`. Não mexe em fluxo, data store ou conexão que esta conversa não criou.

## Dados necessários

- `BRAINSTORM_<FLUXO>.md`, `DEFINE_<FLUXO>.md`, `DESIGN_<FLUXO>.md` e o blueprint.
- O teste de aceite do DEFINE (amostra sem dado pessoal real, resultado esperado, segunda execução se grava).
- `organizationId` e `teamId`.
- O "sim" da pessoa para cada gravação na conta e para ligar o gatilho.

## Procedimento passo a passo

1. **Conferência de entrada.** Três documentos presentes; blueprint com [C1]; [P1] atendida.
2. **Ordem [B1].** Siga PROTOCOLO.md: conta → conexões → validação → criar → interface → ativar → rodar → ler.
3. **Aviso [B5]** antes de criar e antes de cada execução.
4. **Prompts de IA.** Com inventário no DESIGN, gere cada prompt com a skill `sdd-prompt-builder`, passando o
   contrato do DESIGN, e coloque o texto no módulo de IA antes de criar o fluxo.
5. **Teste de aceite.** Rode como o DEFINE manda. Fluxo que grava: rode a mesma amostra uma segunda vez e confira
   que a contagem de registros não mudou.
6. **Resultado.** Compare valor a valor com o esperado e mostre em linguagem de escritório ("a razão social apareceu
   na tabela de clientes: …").
7. **Falha.** [B3].
8. **Recibo e gatilho.** Recibo com operações gastas; depois, a pergunta [B2].
9. **Ficha.** Preencha a ficha do fluxo e feche com [E1].

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

**[C1] Confidencial.** O fluxo é criado com `metadata.scenario.confidential: true`. Se o blueprint do DESIGN não
tiver, corrija antes de criar e diga isso.

**[P1] Prompts de IA.** Fluxo com módulo de IA (OpenAI, Claude, Gemini ou agente de IA do Make) e sem inventário de
prompts no DESIGN: pare antes do `scenarios_create`, diga o que falta e indique voltar à skill `spec-make-design`. O
mesmo vale para IA que grava sem o aceite humano [G1] ou sem o registro do aceite [G2] no DESIGN.

**[M1] Sem o conector do Make.** Se a conversa não tiver o MCP do Make com as ferramentas de gravação, avise em uma
frase, entregue o blueprint como arquivo `.json` e os passos para importar no Make (Cenários → Criar → menu "…" →
Importar blueprint), o roteiro do teste de aceite para a pessoa rodar, e marque como "a confirmar na conta" as
conexões a autorizar, o plano e as operações. Não afirme que criou, rodou ou ligou nada.

**[E1] Etapa 4 de 4.** A primeira resposta traz a linha "spec-make · Etapa 4 de 4 — Build". O fecho entrega o recibo
e o arquivo `FICHA_DO_FLUXO_<FLUXO>.md`, pede para salvá-lo e diz: "Pronto: o fluxo está na sua conta. A ficha diz o
que fazer quando ele falhar."

## Validações e checklist de qualidade

- [ ] Três documentos e [P1] conferidos antes de gravar
- [ ] Ordem [B1] seguida; nenhum nome de módulo inventado
- [ ] [B5] antes de criar e antes de cada execução
- [ ] Fluxo criado sob demanda e com `confidential: true`
- [ ] Teste de aceite rodado; resultado comparado valor a valor
- [ ] Fluxo que grava: segunda execução sem registro novo
- [ ] Operações gastas informadas
- [ ] Gatilho ligado só depois de "Ligar agora" ou "sim" ([B2])
- [ ] Nada alterado fora do que esta conversa criou ([B4])
- [ ] Recibo e ficha entregues

## Tratamento de exceções

- **Teste falhou:** [B3], até 3 tentativas; depois, pare e entregue o resumo.
- **Conexão faltando:** `credential-requests_create` com o app e os módulos do DESIGN; mande o link; espere a pessoa
  dizer que autorizou; confira com `connections_list`.
- **"Scenario is already being executed":** espere a execução em andamento terminar; não rode de novo por cima.
- **O plano não tem operações suficientes no mês:** diga quantas restam (se a conta informar) e não rode.
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
- `references/MCP_MAKE.md` · `references/COPY.md` · `references/RUNTIME_COMPATIBILITY.md`
- `assets/RECIBO_TEMPLATE.md` · `assets/FICHA_DO_FLUXO_TEMPLATE.md`
- `scripts/checar_blueprint.py` — confere confidencial, interface e credencial escrita (Python 3.9+, sem dependências)
- `manifest.json` · `evals/cases.json`

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
