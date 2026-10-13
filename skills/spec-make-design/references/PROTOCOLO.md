# Protocolo da etapa 3 — Design do fluxo

## 1. Abertura

As duas linhas da regra [E1]. Depois: "Vamos desenhar o fluxo com os módulos que existem na sua conta e deixar o
blueprint pronto e validado. Nada é criado na conta nesta etapa."

## 2. Módulos reais da conta

Para cada passo do DEFINE:

1. `app-modules_list(organizationId, appName, appVersion)` do app escolhido no BRAINSTORM.
2. Escolha o módulo pelo rótulo; confirme com `app-module_get(…, format: "instructions")`, que traz os campos de
   entrada e saída.
3. Anote `app:Modulo` e a versão exatamente como voltaram. Nunca invente.
4. Módulo de app premium (`premiumApp: true`) num plano sem apps premium: troque.

## 3. Desenho

Lista numerada, na ordem do editor do Make:

```text
1. Entrada sob demanda — recebe: cnpj
2. Brasil API · Buscar CNPJ — usa: {{1.cnpj}} sem pontuação · devolve: razão social, situação, município
3. Data store · Adicionar ou substituir registro — chave: {{2.cnpj}} · grava: razão social, situação, município
4. Saída — devolve: razão social, situação
```

## 4. Erros por módulo

Use ERROS_E_DIRETIVAS.md. Para cada módulo que fala com sistema externo, escolha a diretiva e escreva o motivo. À
pessoa, faça só a pergunta de negócio, uma por mensagem.

## 5. Governança

[G1], [G2] e [G3] da SKILL.md, com os detalhes de GOVERNANCA_DO_FLUXO.md. Cada uma sai como "atendida (como)" ou
"não se aplica (por quê)".

## 6. Prompts de IA

[P1] com PROMPTS_DE_IA.md, quando houver módulo de IA.

## 7. Blueprint

Parta de `assets/blueprint-minimo.json`. Regras:

- `metadata.scenario.confidential: true` ([C1]).
- Fluxo sob demanda que recebe dados: `interface.input` no topo, com os mesmos campos da entrada do módulo 1, e
  `interface.output` se o fluxo devolve resultado.
- Nenhuma chave ou senha escrita: conexões são referenciadas pelo id que o Make atribui (`__IMTCONN__`), criadas na
  etapa 4.
- Agendamento: `on-demand` no blueprint. O agendamento definitivo só é ligado na etapa 4, com o "sim" da pessoa.

Validações, nesta ordem: `validate_module_configuration` por módulo (use `normalizedValues` quando vier) →
`validate_blueprint_schema` → `validate_scenario_interface`. Depois, `checar_blueprint.py`.

## 8. Custo

Operações por execução = módulos que rodam por item. Compare com o orçamento do DEFINE.

## 9. Documento e fecho

`assets/DESIGN_TEMPLATE.md` com o blueprint no fim, entregue como `DESIGN_<FLUXO>.md`. Entregue também o blueprint como
arquivo `.json` separado. Feche com [E1].
