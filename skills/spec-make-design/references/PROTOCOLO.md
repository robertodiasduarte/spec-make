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

## 2b. Documentação do Make na web ([W1])

Para cada app do fluxo, uma vez: abra `https://apps.make.com/<app>` e confira o nome dos módulos, a versão e o que a
conexão pede. Anote em `Fontes consultadas` a URL, a data, o módulo e a versão lidos. Se a página divergir de
`app-modules_list` (módulo que a página não cita, versão diferente, módulo marcado como antigo), vale a conta: use o que
a conta devolveu e escreva a divergência na mesma linha. Sem acesso à web nesta conversa, escreva "não consultado".

## 3. Desenho

Lista numerada, na ordem do editor do Make:

```text
1. Entrada sob demanda — recebe: cnpj
2. Brasil API · Buscar CNPJ — usa: {{1.cnpj}} sem pontuação · devolve: razão social, situação, município
3. Data store · Adicionar ou substituir registro — chave: {{2.cnpj}} · grava: razão social, situação, município
4. Saída — devolve: razão social, situação
```

## 3b. Fluxo que toca Supabase ([S1] a [S5])

Fluxo com módulo do app `supabase`, `supabase-management` ou `postgres`, ou com HTTP para o endereço de um projeto Supabase, em qualquer caminho. Leia
SUPABASE.md e preencha:

1. **Conexão ([S1]).** Diálogo padrão do app (Project ID e chave secreta, copiados do painel); coluna `alcance` com o
   motivo, as tabelas e as operações. Troque `postgres` e `supabase-management` pelo app `supabase`. Nunca escreva o
   valor da chave no DESIGN.
2. **Módulos ([S2]).** Só `searchRows`, `createARow`, `upsertARecord`, `getRowsCount` e `deleteRows`. Conte os passos da
   pessoa fora do Make e escreva no `Prepare o banco`: 1 colagem de SQL, 2 valores copiados do painel e 1 conexão.
3. **Fila ([S3]).** Agenda do Make → `searchRows` com `processado` igual a `false` e limite → processa →
   `upsertARecord` na fila regravando a linha inteira (as colunas lidas mais `processado = true` e `processado_em`).
4. **Relógio ([S4]).** Seção `Relógio`: agenda do Make com o intervalo, ou sob demanda, e as operações paradas por mês.
5. **Banco ([S5]).** Seção `Prepare o banco` com o SQL modelo de SUPABASE.md, trocando os `<…>` pelos nomes do fluxo:
   chave natural como chave primária do destino, dinheiro em `numeric(18,2)`, e, com IA aceita, a auditoria com os 6
   campos obrigatórios vindos do passo de aceite e a view da taxa de correção.

Fluxo que não toca Supabase: as seções `Prepare o banco` e `Relógio` e a coluna `alcance` dizem "não se aplica: o
fluxo não usa Supabase".

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
- Fluxo sob demanda que recebe dados: os campos de entrada ficam em `metadata.interface` do módulo 1, e o DESIGN
  traz um bloco "Interface" separado (entrada e saída) que a etapa 4 grava com `scenarios_set-interface`. **Não**
  ponha a chave `interface` no blueprint: o validador do Make a recusa. Exemplo do bloco:
  `{"input": [{"name": "cnpj", "type": "text", "label": "CNPJ", "required": true}], "output": [{"name": "razao_social", "type": "text"}]}`.
  Confira o bloco com `validate_scenario_interface`.
- Nenhuma chave ou senha escrita: conexões são referenciadas pelo id que o Make atribui (`__IMTCONN__`), criadas na
  etapa 4.
- Agendamento: não vai no blueprint; a etapa 4 cria o fluxo `on-demand` (argumento do `scenarios_create`) e só liga o
  agendamento definitivo com o "sim" da pessoa.

Validações, nesta ordem: `validate_module_configuration` por módulo (use `normalizedValues` quando vier) →
`validate_blueprint_schema` → `validate_scenario_interface`. Depois, `checar_blueprint.py`.

## 8. Custo

Operações por execução = módulos que rodam por item. Com a agenda do Make como relógio, some as operações paradas:
disparos por mês × operações do disparo vazio ([S4]). Compare o total com o orçamento do DEFINE.

## 9. Documento e fecho

`assets/DESIGN_TEMPLATE.md` com o blueprint no fim, entregue como `DESIGN_<FLUXO>.md`. Entregue também o blueprint como
arquivo `.json` separado. Feche com [E1].
