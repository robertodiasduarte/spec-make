---
name: spec-make-define
license: MIT
description: "Conduz a etapa 2 de 4 do spec-make: transforma o BRAINSTORM de um fluxo do Make em requisitos verificáveis, escritos como 'Quando X, o fluxo faz Y' com a gramática EARS por baixo, mais um teste de aceite que é uma execução de verdade (amostra, resultado esperado e segunda rodada sem duplicar) e o orçamento de operações contra o plano. Use quando a pessoa anexar um BRAINSTORM_NOME-DO-FLUXO.md ou pedir para fechar os requisitos de um fluxo do Make. Entrega DEFINE_NOME-DO-FLUXO.md. Não desenha módulos (spec-make-design) e não cria nada na conta (spec-make-build). Período de consulta e de cálculo: não se aplicam."
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: "1.4.0"
  updated: "2026-10"
---

# spec-make — Etapa 2: Define do fluxo

Na primeira resposta desta skill, comece com a linha de versão, uma vez só:
`spec-make-define v1.4.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/spec-make/releases/latest`
Em seguida, e em toda resposta, o mapa de posição ([E1]). A conversa segue
[references/CONDUCAO.md](references/CONDUCAO.md): mapa, glossário, pergunta de decisão, alerta e bloqueios.

## Quick start

1. Receba o `BRAINSTORM_<FLUXO>.md` (anexado ou colado). Sem ele: [A3] de references/CONDUCAO.md. Liste no começo os
   alertas aceitos das etapas anteriores ([A2]).
2. Extraia problema, quem usa, objetivo, escopo e o que ficou de fora — só o que o BRAINSTORM sustenta.
3. Escreva os critérios de aceite em três linhas **[D3]**: "Quando X, o fluxo faz Y", a forma EARS e "Em outras palavras"
   ([references/EARS.md](references/EARS.md)).
4. Escreva o teste de aceite pela regra **[D1]** ([references/VERIFY_GATE_EXECUCAO.md](references/VERIFY_GATE_EXECUCAO.md)).
5. Calcule o orçamento de operações por mês contra o plano (com o MCP do Make: `organizations_list`).
6. Marque o que for ambíguo e pergunte, uma pergunta por mensagem.
7. Entregue `DEFINE_<FLUXO>.md` usando [assets/DEFINE_TEMPLATE.md](assets/DEFINE_TEMPLATE.md) e feche com **[E1]**.

## Quando usar / Quando não usar

Usar depois do brainstorm, quando a ideia do fluxo já está escrita e é hora de dizer, de forma verificável, o que ele
tem de fazer.

Sem o BRAINSTORM, siga o [A3]. Não usar para escolher módulos, diretivas de erro ou montar o blueprint: isso é a
etapa 3. Não cria nem altera nada na conta do Make.

## Dados necessários

- O `BRAINSTORM_<FLUXO>.md`.
- A amostra e o resultado esperado registrados nele (sem dado pessoal real).
- Plano e operações por mês da conta (do BRAINSTORM ou consultados de novo pelo MCP).
- Respostas da pessoa às ambiguidades.

## Procedimento passo a passo

Siga [references/PROTOCOLO.md](references/PROTOCOLO.md). Resumo:

1. **Leitura.** Leia o BRAINSTORM inteiro. Liste o que está decidido e o que está "a confirmar". Liste no começo os
   alertas aceitos das etapas anteriores ([A2]).
2. **Requisitos.** Problema em 1 frase; quem usa; objetivos MUST/SHOULD; o que fica de fora.
3. **Critérios de aceite.** De 3 a 8, cada um em três linhas ([D3]). Inclua pelo menos um "Se der
   errado" (If/Then): app fora do ar, dado faltando, conexão expirada.
4. **Teste de aceite.** Regra [D1].
5. **Orçamento.** Operações por execução × execuções por mês, contra o limite do plano. Acima de 80% do limite: [D2].
6. **Ambiguidades.** Marque `A CONFIRMAR:` no ponto exato e pergunte, uma por mensagem, com a opção recomendada
   primeiro. Integre a resposta no corpo do documento.
7. **Clareza.** [D2].
8. **Documento.** Preencha o template e feche com [E1].

**[D1] Gate de execução.** O teste de aceite do fluxo é uma execução de verdade, não uma validação de texto. Ele
traz: a amostra (sem dado pessoal real), o resultado esperado escrito com valores, o modo de teste (sob demanda com
os dados da amostra, ou gatilho real) e, quando o fluxo grava registros em algum lugar, a segunda execução da mesma
amostra com a mesma contagem de registros no destino. Teste que só confere uma execução de um fluxo que grava, ou
"blueprint validado" como teste de aceite: alerta [A1] — os validadores do Make já aprovaram blueprint que falhou na
primeira execução, e sem a 2ª execução um fluxo que duplica registros passa no teste (ver
[references/MCP_MAKE.md](references/MCP_MAKE.md), fato 1).

**[D2] Clareza e pendências.** Dê nota de 0 a 3 para problema, quem usa, objetivos, aceite e escopo. Nota abaixo de 12
de 15, ou `A CONFIRMAR:` ainda aberto na entrega: alerta [A1] — a etapa 3 vai desenhar sobre uma suposição, e o teste
pode aprovar o fluxo errado. Orçamento acima de 80% do plano: alerta [A1] — o plano pode acabar antes do fim do mês.

**[D3] Critério em três linhas.** Cada critério sai com a frase de escritório, a forma EARS e, logo abaixo,
`Em outras palavras: <frase do dia a dia>`. Na primeira vez, ensine o EARS em 3 linhas com um critério do próprio fluxo
da pessoa (references/EARS.md).

**[M1] Sem o conector do Make.** Se a conversa não tiver o MCP do Make, avise em uma frase e siga no papel; o plano e
as operações por mês ficam "a confirmar na conta" se o BRAINSTORM não os trouxer.

**[E1] Etapa 2 de 4.** Toda resposta abre com o mapa de posição ([K1] de references/CONDUCAO.md), que começa por
"Etapa 2 de 4 · Define"; a primeira resposta traz antes a linha de versão. O fecho segue [K5]: entrega o arquivo
`DEFINE_<FLUXO>.md`, pede para salvá-lo e diz a frase exata da próxima etapa: "Abra uma conversa nova, anexe o
BRAINSTORM e este DEFINE e diga: Use a skill spec-make-design."

## Validações e checklist de qualidade

- [ ] Só fatos sustentados pelo BRAINSTORM; nada inventado
- [ ] Toda resposta com o mapa de posição; alertas aceitos das etapas anteriores listados no começo ([A2])
- [ ] 3 a 8 critérios, cada um em três linhas: frase de escritório, EARS e "Em outras palavras" ([D3])
- [ ] Pelo menos 1 critério "Se der errado" (If/Then)
- [ ] Teste de aceite pela [D1], com resultado esperado em valores
- [ ] Fluxo que grava: segunda execução da mesma amostra com a mesma contagem
- [ ] Orçamento de operações contra o plano
- [ ] `A CONFIRMAR:` aberto ou clareza abaixo de 12 de 15: alerta [D2] feito e, se aceito, registrado
- [ ] Seção `Alertas aceitos` preenchida (ou "nenhum") e fecho [K5] com a frase da próxima etapa

## Tratamento de exceções

- **Sem BRAINSTORM:** [A3].
- **Amostra com dado pessoal:** bloqueio [X1]: não use; peça uma inventada ou pública.
- **Resultado esperado vago ("tem que funcionar"):** pergunte o valor concreto que deve aparecer.
- **Orçamento acima do plano:** [D2]; mostre a conta e recomende menos execuções, menos passos ou outro plano.
- **A pessoa pede para pular o teste:** alerta [A1] pelo [D1]: sem ele, a etapa 4 não tem como saber se o fluxo
  funciona; o teste é a amostra que ela já deu.

## Examples

**Caso positivo (sintético).** BRAINSTORM do cadastro por CNPJ. Critério: "Quando eu informar um CNPJ, o fluxo
guarda razão social, situação e município na tabela de clientes." EARS: "When a pessoa informa um CNPJ, the fluxo
shall gravar razão social, situação e município no data store de clientes." Teste [D1]: amostra = CNPJ de uma
companhia aberta; esperado = razão social e situação "ATIVA"; segunda execução da mesma amostra = continua 1 registro.

**Contraexemplo.** "O teste é: o Make validou o blueprint." A skill faz o alerta do [D1] e recomenda a amostra e o
resultado esperado.

## Inventário do bundle

- `SKILL.md`
- `references/PROTOCOLO.md` — roteiro detalhado
- `references/VERIFY_GATE_EXECUCAO.md` — o teste de aceite por execução
- `references/EARS.md` — a gramática dos critérios e como ensiná-la
- `references/CONDUCAO.md` — mapa de posição, glossário, pergunta de decisão, alerta, alertas aceitos e bloqueios
- `references/MCP_MAKE.md` · `references/COPY.md` · `references/RUNTIME_COMPATIBILITY.md` · `references/SUPABASE.md`
- `assets/DEFINE_TEMPLATE.md`
- `manifest.json` · `evals/cases.json`

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
