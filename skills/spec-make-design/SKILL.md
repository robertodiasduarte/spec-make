---
name: spec-make-design
license: MIT
description: "Conduz a etapa 3 de 4 do spec-make: transforma o DEFINE de um fluxo do Make num desenho técnico ancorado na conta da pessoa — só módulos que existem nela (consultados pelo MCP do Make), a diretiva de erro de cada módulo, a chave que impede registro duplicado, o aceite humano antes de a IA gravar e o blueprint já validado e conferido. Use quando a pessoa anexar o BRAINSTORM e o DEFINE de um fluxo do Make e pedir o desenho ou o blueprint. Entrega DESIGN_<FLUXO>.md com o blueprint. Não cria nada na conta (spec-make-build) e não escreve os prompts de agentes de IA do fluxo (sdd-prompt-builder). Período de consulta e de cálculo: não se aplicam."
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: "1.0.0"
  updated: "2026-10"
---

# spec-make — Etapa 3: Design do fluxo

Na primeira resposta desta skill, comece com estas duas linhas, uma vez só:
`spec-make-design v1.0.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/spec-make/releases/latest`
`spec-make · Etapa 3 de 4 — Design`

## Quick start

1. Receba o BRAINSTORM e o DEFINE do fluxo. Sem o DEFINE, indique a skill `spec-make-define`.
2. Com o MCP do Make, confirme cada módulo na conta (`app-modules_list`, `app-module_get`). Sem ele, siga **[M1]**.
3. Desenhe o fluxo módulo a módulo, como ele aparece no editor do Make.
4. Escolha a diretiva de erro de cada módulo e faça à pessoa só a pergunta de negócio ([references/ERROS_E_DIRETIVAS.md](references/ERROS_E_DIRETIVAS.md)).
5. Aplique as regras de governança **[G1]**, **[G2]**, **[G3]** ([references/GOVERNANCA_DO_FLUXO.md](references/GOVERNANCA_DO_FLUXO.md)).
6. Se houver módulo de IA, registre o inventário de prompts **[P1]** ([references/PROMPTS_DE_IA.md](references/PROMPTS_DE_IA.md)).
7. Monte o blueprint com **[C1]**, valide pelo MCP e confira com `scripts/checar_blueprint.py`.
8. Entregue `DESIGN_<FLUXO>.md` usando [assets/DESIGN_TEMPLATE.md](assets/DESIGN_TEMPLATE.md) e feche com **[E1]**.

## Quando usar / Quando não usar

Usar depois do Define, quando os critérios e o teste de aceite do fluxo estão fechados.

Não usar sem o DEFINE. Não usar para criar, ativar ou rodar o fluxo: isso é a etapa 4. Não escreve o texto dos
prompts dos agentes de IA do fluxo: registra o inventário e o contrato, e a etapa 4 os gera com a skill
`sdd-prompt-builder`.

## Dados necessários

- `BRAINSTORM_<FLUXO>.md` e `DEFINE_<FLUXO>.md`.
- `organizationId` e `teamId` (do BRAINSTORM ou de `environment_get`).
- Respostas da pessoa às perguntas de negócio (o que fazer quando cada app falha; quem aprova a sugestão da IA).

## Procedimento passo a passo

Siga [references/PROTOCOLO.md](references/PROTOCOLO.md). Resumo:

1. **Módulos reais.** Para cada passo, `app-modules_list` do app escolhido e `app-module_get` do módulo, no formato
   de instruções. Use só nomes que voltaram dessas chamadas; nunca invente `app:Modulo`.
2. **Desenho.** Lista numerada de módulos, na ordem do editor, com o que entra e o que sai de cada um.
3. **Erros.** Diretiva por módulo (ERROS_E_DIRETIVAS.md); à pessoa, só a pergunta de negócio ("se o Omie estiver fora
   do ar: tento de novo em 15 min ou te aviso?").
4. **Governança.** [G1], [G2] e [G3] abaixo.
5. **Prompts de IA.** [P1] abaixo.
6. **Blueprint.** Monte o JSON com [C1]. Valide cada módulo com `validate_module_configuration`, o todo com
   `validate_blueprint_schema` e a interface com `validate_scenario_interface`. Depois, rode
   `python3 scripts/checar_blueprint.py <arquivo>` (ou faça a mesma conferência lendo, se o ambiente não executa
   código). Validado não quer dizer testado: o teste é a etapa 4.
7. **Custo.** Confirme as operações por execução contra o orçamento do DEFINE.
8. **Documento.** Preencha o template com o blueprint no fim e feche com [E1].

**[G1] Aceite humano.** Se a saída de um módulo de IA grava, classifica ou altera lançamento, documento fiscal ou
cadastro do escritório, o fluxo tem um passo de aceite por pessoa identificada antes da gravação (fila de sugestões
numa planilha, aprovação por e-mail ou formulário; a gravação só acontece pela ação da pessoa). Sem esse passo,
recuse o DESIGN como pronto e diga o que falta.

**[G2] Registro do aceite.** Quando o fluxo tem IA cuja sugestão é aceita, cada aceite é registrado fora do histórico
de execução do Make (planilha ou data store da pessoa) com seis campos: modelo, versão do prompt, sugestão original,
quem aceitou, quando (UTC) e se editou antes de aceitar. Sem esse registro, recuse o DESIGN como pronto.

**[G3] Chave natural.** Se o fluxo cria registros num sistema do escritório (ERP, planilha, CRM, data store), o DESIGN
declara a chave natural do registro (id do e-mail, chave de acesso da nota, CNPJ, id da transação) e a regra "já existe ⇒ não grava de novo"
(consultar antes de gravar, ou gravar substituindo pela chave). Sem a chave, recuse o
DESIGN como pronto e peça a chave.

**[P1] Prompts de IA.** Se o fluxo tem módulo de IA (OpenAI, Claude, Gemini ou agente de IA do Make), registre o
inventário de prompts com os campos de PROMPTS_DE_IA.md. O texto do prompt não é escrito aqui: a etapa 4 gera cada um
com a skill `sdd-prompt-builder` a partir desse contrato. Fluxo com módulo de IA e sem esse inventário: recuse o DESIGN
como pronto e diga o que falta.

**[C1] Confidencial.** Todo blueprint sai com `metadata.scenario.confidential: true`. O escritório trata dado de
cliente; com a opção ligada, o Make não guarda os dados de cada passo no histórico.

**[M1] Sem o conector do Make.** Se a conversa não tiver o MCP do Make, avise em uma frase e siga no papel: escolha
módulos pela documentação pública, marque cada um como "a confirmar na conta" e não declare o blueprint validado.

**[E1] Etapa 3 de 4.** A primeira resposta traz a linha "spec-make · Etapa 3 de 4 — Design". O fecho entrega o arquivo
`DESIGN_<FLUXO>.md`, pede para salvá-lo e diz a frase exata da próxima etapa: "Abra uma conversa nova, anexe o
BRAINSTORM, o DEFINE e este DESIGN e diga: Use a skill spec-make-build."

## Validações e checklist de qualidade

- [ ] Todo `module` do blueprint voltou de `app-modules_list` (ou está marcado "a confirmar na conta" em [M1])
- [ ] Diretiva de erro escolhida e justificada por módulo
- [ ] [G1], [G2] e [G3] atendidas ou declaradas "não se aplica" com o motivo
- [ ] Inventário [P1] quando há módulo de IA
- [ ] `confidential: true`; fluxo sob demanda com entrada: campos no módulo 1, bloco "Interface" no DESIGN e nenhuma chave `interface` no blueprint
- [ ] Três validações do MCP sem erro e `checar_blueprint.py` OK
- [ ] Operações por execução dentro do orçamento do DEFINE
- [ ] Fecho com a frase da próxima etapa

## Tratamento de exceções

- **Módulo não existe na conta:** procure alternativa (`apps_recommend`) ou HTTP genérico; registre a troca.
- **App premium fora do plano:** avise e ofereça alternativa.
- **Validação falha:** corrija pelo erro devolvido e valide de novo; depois de 3 tentativas no mesmo módulo, pare e
  explique o que o Make diz.
- **DESIGN recusado por [G1], [G2] ou [G3]:** diga exatamente o que falta e ofereça o desenho com o passo incluído.
- **A pessoa quer a IA gravando direto:** explique em uma frase por que o aceite fica (quem responde pelo lançamento é
  o profissional) e mantenha a recusa.

## Examples

**Caso positivo (sintético).** DEFINE do cadastro por CNPJ. Módulos confirmados: entrada sob demanda, `brasil-api`
Buscar CNPJ, data store "Adicionar ou substituir registro" com a chave = CNPJ ([G3]). Erro na Brasil API: tenta de novo
(Break) 3 vezes. Sem IA ([G1], [G2], [P1] não se aplicam). Blueprint com `confidential: true`; a interface (campo `cnpj`) vai no DESIGN, para a etapa 4 gravar.

**Contraexemplo.** "A IA classifica a nota e lança direto no ERP." A skill recusa por [G1] e propõe: a IA grava a
sugestão numa planilha, a pessoa marca "aprovado", outro passo lança e registra o aceite ([G2]).

## Inventário do bundle

- `SKILL.md`
- `references/PROTOCOLO.md` · `references/ERROS_E_DIRETIVAS.md` · `references/GOVERNANCA_DO_FLUXO.md` · `references/PROMPTS_DE_IA.md`
- `references/MCP_MAKE.md` · `references/COPY.md` · `references/RUNTIME_COMPATIBILITY.md`
- `assets/DESIGN_TEMPLATE.md` · `assets/blueprint-minimo.json`
- `scripts/checar_blueprint.py` — confere confidencial, interface e credencial escrita (Python 3.9+, sem dependências)
- `manifest.json` · `evals/cases.json`

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
