---
name: spec-make-brainstorm
license: MIT
description: "Conduz a etapa 1 de 4 do spec-make: transforma uma rotina do escritório contábil num documento de ideia para um fluxo no Make, conferindo na conta da pessoa, pelo MCP do Make, se existe app nativo para cada passo, quais conexões ela já tem e quanto o plano permite. Use quando alguém quiser automatizar uma rotina no Make e ainda não tiver o BRAINSTORM do fluxo, ou disser 'quero criar um fluxo no Make'. Entrega BRAINSTORM_<FLUXO>.md. Não escreve requisitos formais (etapa spec-make-define), não desenha o blueprint (spec-make-design) e não cria nada na conta (spec-make-build). Período de consulta e de cálculo: não se aplicam (não há regra tributária nem cálculo profissional)."
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: "1.0.0"
  updated: "2026-10"
---

# spec-make — Etapa 1: Brainstorm do fluxo

Na primeira resposta desta skill, comece com estas duas linhas, uma vez só:
`spec-make-brainstorm v1.0.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/spec-make/releases/latest`
`spec-make · Etapa 1 de 4 — Brainstorm`

## Quick start

1. Descubra se a conversa tem o MCP do Make ([references/MCP_MAKE.md](references/MCP_MAKE.md)). Sem ele, siga **[M1]**.
2. Com ele, chame `environment_get` e `organizations_list` e anote organização, equipe, plano e operações por mês.
3. Pergunte qual rotina a pessoa quer automatizar. Se ela não souber por onde começar, ofereça os exemplos de [references/PROTOCOLO.md](references/PROTOCOLO.md).
4. Faça perguntas uma por vez até entender: o que dispara a rotina, o que ela produz, onde os dados moram, quem confere.
5. Confira a viabilidade na conta: `apps_recommend` para cada passo e `connections_list` para o que já está conectado.
6. Peça uma amostra sem dado pessoal real.
7. Proponha 2 ou 3 jeitos de montar o fluxo, com a recomendação primeiro.
8. Corte o que não é necessário agora e valide em 2 blocos curtos.
9. Entregue `BRAINSTORM_<FLUXO>.md` usando [assets/BRAINSTORM_TEMPLATE.md](assets/BRAINSTORM_TEMPLATE.md) e feche com a regra **[E1]**.

## Quando usar / Quando não usar

Usar quando a pessoa quer automatizar uma rotina no Make e a ideia ainda não está escrita, ou quando ela traz uma ideia
solta ("todo mês eu baixo as notas e lanço numa planilha").

Não usar quando já existe um BRAINSTORM do fluxo: siga para a skill `spec-make-define`. Não usar para tirar dúvida
pontual sobre um módulo do Make, nem para consertar um fluxo que já roda (descreva o problema e comece pelo
brainstorm de uma versão nova). Não cria nem altera nada na conta do Make.

## Dados necessários

- A rotina, contada pela pessoa: gatilho, entradas, saídas, frequência, quem confere.
- Uma amostra do que entra no fluxo (um e-mail, uma linha de planilha, um número de nota), **sem dado pessoal
  real**: CPF, nome de pessoa, salário e dado de cliente ficam de fora; use dado público ou inventado
  ([references/COPY.md](references/COPY.md)).
- Da conta, pelo MCP: organização, equipe, plano, operações por mês, conexões existentes e apps disponíveis.
- Opcional: quanto tempo a rotina leva hoje, por mês (só para mostrar o "hoje × amanhã" com a conta dela).

Se faltar algum item, registre como "a confirmar" no documento; nunca preencha com suposição.

## Procedimento passo a passo

Siga [references/PROTOCOLO.md](references/PROTOCOLO.md). Resumo:

1. **Conta.** `environment_get` → `organizations_list`. Guarde `organizationId`, `teamId`, plano e operações por mês.
2. **Rotina.** Uma pergunta por mensagem. Cubra no mínimo: o que dispara, o que entra, o que sai, onde grava, quem
   confere, com que frequência, o que acontece hoje quando dá errado.
3. **Viabilidade na conta.** Para cada passo, `apps_recommend` com a intenção em uma frase. Mostre no máximo 3 apps
   por passo, pelo rótulo do módulo ("Buscar CNPJ"), não pelo nome técnico. Prefira app nativo a chamada HTTP genérica.
   Em seguida, `connections_list`: diga o que já está conectado e o que faltará autorizar no build.
4. **Amostra.** Peça uma amostra sem dado pessoal real e anote o resultado esperado com ela.
5. **Abordagens.** 2 ou 3 jeitos de montar, cada um com prós, contras e custo aproximado em operações por mês contra
   o plano. Recomende um e explique por quê.
6. **Corte.** Para cada parte, pergunte se é necessária agora. Registre o que saiu e por quê.
7. **Validação.** Apresente o fluxo em 2 blocos curtos (o que faz e com quais apps; o que acontece quando falha) e
   peça confirmação de cada um.
8. **Documento.** Preencha o template, entregue o arquivo e feche com **[E1]**.

**[M1] Sem o conector do Make.** Se a conversa não tiver o MCP do Make, avise em uma frase, siga o mesmo roteiro no
papel e marque cada item que depende da conta (apps nativos, conexões, plano) como "a confirmar na conta". Não afirme
que um app existe ou que uma conexão está pronta sem ter consultado.

**[E1] Etapa 1 de 4.** A primeira resposta traz a linha "spec-make · Etapa 1 de 4 — Brainstorm". O fecho entrega o
arquivo `BRAINSTORM_<FLUXO>.md`, pede para salvá-lo e diz a frase exata da próxima etapa: "Abra uma conversa nova,
anexe este arquivo e diga: Use a skill spec-make-define."

## Validações e checklist de qualidade

- [ ] `environment_get` chamado (ou [M1] declarado) e plano anotado
- [ ] Mínimo de 3 perguntas sobre a rotina antes das abordagens, uma por mensagem
- [ ] Viabilidade por passo com app nativo ou motivo para HTTP genérico
- [ ] Conexões existentes e faltantes listadas
- [ ] Amostra sem dado pessoal real e resultado esperado anotado
- [ ] 2 ou 3 abordagens, uma recomendada, com custo em operações
- [ ] Cortes registrados
- [ ] 2 validações confirmadas pela pessoa
- [ ] Documento a partir do template, sem item inventado
- [ ] Fecho com a frase da próxima etapa

## Tratamento de exceções

- **Sem MCP do Make:** [M1].
- **A rotina mistura várias:** proponha começar pela que mais toma tempo e registre as outras como próximas.
- **Nenhum app nativo:** registre "HTTP genérico" e o endereço da API pública, se houver; se depender de API sem
  documentação, registre como risco.
- **Plano sem operações suficientes:** mostre a conta (operações por execução × execuções por mês) e ofereça
  reduzir a frequência ou o número de passos.
- **A pessoa traz dado pessoal na amostra:** não use; peça para trocar por dado inventado.
- **A pessoa quer pular para o fluxo pronto:** explique em uma frase que a próxima etapa precisa deste documento e
  ofereça um brainstorm curto (3 perguntas).

## Examples

**Caso positivo (sintético).** "Quero que, quando eu informar o CNPJ de um cliente novo, o fluxo busque os dados
na Receita e guarde numa tabela." A skill confere a conta, acha o app nativo `brasil-api` (Buscar CNPJ) e o data store
do Make, mostra que não precisa de conexão, pede um CNPJ de companhia aberta como amostra, propõe "sob demanda" ×
"planilha que dispara", recomenda o primeiro e entrega o BRAINSTORM.

**Contraexemplo.** "Crie agora um fluxo que lança as notas no meu ERP." A skill não cria nada: explica que esta é a
etapa de ideia, faz as perguntas da rotina e confere na conta se o ERP tem app nativo.

## Inventário do bundle

- `SKILL.md`
- `references/PROTOCOLO.md` — roteiro detalhado e exemplos de rotinas
- `references/MCP_MAKE.md` — ferramentas e fatos medidos do MCP do Make
- `references/COPY.md` — como falar com a pessoa
- `references/RUNTIME_COMPATIBILITY.md` — o que a skill precisa do ambiente
- `assets/BRAINSTORM_TEMPLATE.md` — molde do documento
- `manifest.json` · `evals/cases.json`

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
