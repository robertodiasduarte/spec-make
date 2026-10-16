---
name: spec-make-design
license: MIT
description: "Conduz a etapa 3 de 4 do spec-make: transforma o DEFINE de um fluxo do Make num desenho técnico ancorado na conta da pessoa — só módulos que existem nela (consultados pelo MCP do Make), a diretiva de erro de cada módulo, a chave que impede registro duplicado, o aceite humano antes de a IA gravar e o blueprint já validado e conferido. Use quando a pessoa anexar o BRAINSTORM e o DEFINE de um fluxo do Make e pedir o desenho ou o blueprint. Entrega DESIGN_NOME-DO-FLUXO.md com o blueprint. Não cria nada na conta (spec-make-build) e não escreve os prompts de agentes de IA do fluxo (sdd-prompt-builder). Período de consulta e de cálculo: não se aplicam."
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: "1.3.0"
  updated: "2026-10"
---

# spec-make — Etapa 3: Design do fluxo

Na primeira resposta desta skill, comece com estas duas linhas, uma vez só:
`spec-make-design v1.3.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/spec-make/releases/latest`
`spec-make · Etapa 3 de 4 — Design`

## Quick start

1. Receba o BRAINSTORM e o DEFINE do fluxo. Sem o DEFINE, indique a skill `spec-make-define`.
2. Com o MCP do Make, confirme cada módulo na conta (`app-modules_list`, `app-module_get`). Sem ele, siga **[M1]**.
   Leia a documentação pública de cada app uma vez **[W1]**.
3. Desenhe o fluxo módulo a módulo, como ele aparece no editor do Make.
4. Escolha a diretiva de erro de cada módulo e faça à pessoa só a pergunta de negócio ([references/ERROS_E_DIRETIVAS.md](references/ERROS_E_DIRETIVAS.md)).
5. Aplique as regras de governança **[G1]**, **[G2]**, **[G3]** ([references/GOVERNANCA_DO_FLUXO.md](references/GOVERNANCA_DO_FLUXO.md)).
   Se o fluxo toca Supabase, aplique também **[S1]** a **[S5]** ([references/SUPABASE.md](references/SUPABASE.md)).
6. Se houver módulo de IA, registre o inventário de prompts **[P1]** ([references/PROMPTS_DE_IA.md](references/PROMPTS_DE_IA.md)).
7. Monte o blueprint com **[C1]**, valide pelo MCP e confira com `scripts/checar_blueprint.py`.
8. Entregue `DESIGN_<FLUXO>.md` usando [assets/DESIGN_TEMPLATE.md](assets/DESIGN_TEMPLATE.md) e feche com **[E1]**.

## Quando usar / Quando não usar

Usar depois do Define, quando os critérios e o teste de aceite do fluxo estão fechados. Com o `HANDOFF_<FLUXO>.md`
anexado, o desenho parte dos ids que a ficha marca como `desta família`: altere o que existe em vez de desenhar um fluxo
novo, e não planeje mudar recurso `compartilhado` ou `fora do spec-make`.

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
4. **Governança.** [G1], [G2] e [G3] abaixo. Fluxo que toca Supabase: [S1] a [S5], com as receitas de
   SUPABASE.md (alcance da conexão, os 5 módulos do banco, o laço da fila, o relógio e o SQL do `Prepare o banco`).
5. **Prompts de IA.** [P1] abaixo.
6. **Blueprint.** Monte o JSON com [C1]. Valide cada módulo com `validate_module_configuration`, o todo com
   `validate_blueprint_schema` e a interface com `validate_scenario_interface`. Depois, rode
   `python3 scripts/checar_blueprint.py <arquivo>` (ou faça a mesma conferência lendo, se o ambiente não executa
   código). Validado não quer dizer testado: o teste é a etapa 4.
7. **Custo.** Confirme as operações por execução contra o orçamento do DEFINE, somando as operações paradas quando o
   relógio é a agenda do Make ([S4]).
8. **Documento.** Preencha o template com o blueprint no fim e feche com [E1].

**[G1] Aceite humano.** Se a saída de um módulo de IA grava, classifica ou altera lançamento, documento fiscal ou
cadastro do escritório, o fluxo tem um passo de aceite por pessoa identificada antes da gravação (fila de sugestões
numa planilha, aprovação por e-mail ou formulário; a gravação só acontece pela ação da pessoa). Sem esse passo,
recuse o DESIGN como pronto e diga o que falta.

**[G2] Registro do aceite.** Quando o fluxo tem IA cuja sugestão é aceita, cada aceite é registrado fora do histórico
de execução do Make (planilha ou data store da pessoa; quando o fluxo já usa Supabase, a 1ª opção é uma tabela de
auditoria só de acréscimo, com o SQL de [S5]) com seis campos: modelo, versão do prompt, sugestão original,
quem aceitou, quando (UTC) e se editou antes de aceitar. Sem esse registro, recuse o DESIGN como pronto.

**[G3] Chave natural.** Se o fluxo cria registros num sistema do escritório (ERP, planilha, CRM, data store), o DESIGN
declara a chave natural do registro (id do e-mail, chave de acesso da nota, CNPJ, id da transação) e a regra "já existe ⇒ não grava de novo"
(consultar antes de gravar, ou gravar substituindo pela chave). Quando o destino é uma tabela do Supabase, a chave
existe nela como restrição ([S5]). Sem a chave, recuse o
DESIGN como pronto e peça a chave.

**[S1] Chave do Supabase.** Se o fluxo toca Supabase (app `supabase`, `supabase-management`, `postgres` ou HTTP para
o endereço de um projeto Supabase, em qualquer caminho), a conexão Supabase usa o diálogo padrão do app no Make
(Project ID e chave secreta, copiados do painel do Supabase) e o DESIGN preenche a coluna `alcance` com o motivo ("o app
Supabase do Make só conecta com chave secreta; ela ignora o RLS"), as tabelas e as operações. `postgres` (conexão direta)
e `supabase-management` nunca entram no fluxo. Sem isso, recuse o DESIGN como pronto e diga o que falta.

**[S2] Só módulos do banco.** Se o fluxo toca Supabase, do app `supabase` entram só `searchRows`, `createARow`,
`upsertARecord`, `getRowsCount` e `deleteRows`, e a pessoa não faz, antes do 1º fluxo rodar, mais que 1 colagem de SQL,
copiar o Project ID e a chave do painel e criar 1 conexão no Make. Edge function, webhook de qualquer tipo, Database
Webhook, `pg_cron`, `supabase:watchEvents`, `supabase:makeAnApiCall` e módulo HTTP para o endereço de um projeto Supabase
ficam fora: recuse o DESIGN como pronto e proponha o caminho só com o banco.

**[S3] Fila de pendentes.** Se o fluxo toca Supabase e lê uma fila, o DESIGN desenha o laço agenda do Make →
`searchRows` com `processado` igual a `false` e um limite → processa → `upsertARecord` pela primary key da fila, que
regrava a linha inteira (as colunas lidas mais `processado = true` e `processado_em`). Filtro por coluna vazia, ou
gatilho que não seja a agenda do Make: recuse o DESIGN como pronto.

**[S4] Relógio.** Se o fluxo toca Supabase, o DESIGN declara no bloco `Relógio` como o fluxo dispara — agenda do Make
com o intervalo, ou sob demanda — e, com agenda, soma no custo as operações paradas: disparos por mês × operações do
disparo vazio. Se o total passar do orçamento do DEFINE, recuse o DESIGN como pronto e ofereça um intervalo maior.

**[S5] Banco preparado.** Se o fluxo toca Supabase e grava no banco, o `Prepare o banco` traz o SQL para o SQL Editor:
a chave natural como `primary key` da tabela de destino que o `upsertARecord` grava (a fila, que aceita a chave repetida,
tem o `id` como `primary key` e o marcador a grava por ele), `processado` e `processado_em` quando o fluxo lê pendentes,
RLS ligado sem política, coluna de valor em dinheiro como `numeric(18,2)` e, com IA aceita, a tabela de auditoria só de
acréscimo (chave do aceite como `primary key`, os 6 campos de [G2] `not null`, gatilho que recusa alterar, apagar e
truncar, e a view da taxa de correção). Os 6 campos vêm do passo de aceite, gravados antes do "processa" e nunca
recalculados, para a repetição do mesmo aceite ser idêntica. Chave natural que não é a `primary key` da tabela de
destino do `upsertARecord`, coluna de valor em `real`, `float4`, `float8` ou `double precision`, rateio sem a regra do
centavo residual, campo da auditoria anulável, auditoria sem o gatilho ou sem a view: recuse o DESIGN como pronto e
nomeie a coluna, o campo ou o rateio que falta corrigir.

**[W1] Documentação do Make.** Para cada app do fluxo, consulte a documentação pública do Make
(`https://apps.make.com/<app>`) uma vez e anote em `Fontes consultadas` a URL, a data, o módulo e a versão. Se ela
divergir de `app-modules_list`, vale a conta, e o DESIGN anota a divergência. Sem acesso à web, escreva "não
consultado"; nunca afirme uma consulta que não fez.

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
- [ ] Fluxo que toca Supabase: [S1] a [S5] atendidas (coluna `alcance`, `Prepare o banco`, `Relógio`); sem Supabase, as 3 seções dizem "não se aplica: o fluxo não usa Supabase"
- [ ] `Fontes consultadas` com URL e data de cada app, ou "não consultado" [W1]
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
- **A pessoa quer `postgres` ou `supabase-management` "porque é mais fácil":** explique em uma frase o alcance da senha
  ou do token (o banco inteiro, ou todos os projetos) e ofereça o app `supabase` com os módulos do banco ([S1], [S2]).
- **A pessoa quer a IA gravando direto:** explique em uma frase por que o aceite fica (quem responde pelo lançamento é
  o profissional) e mantenha a recusa.

## Examples

**Caso positivo (sintético).** DEFINE do cadastro por CNPJ. Módulos confirmados: entrada sob demanda, `brasil-api`
Buscar CNPJ, data store "Adicionar ou substituir registro" com a chave = CNPJ ([G3]). Erro na Brasil API: tenta de novo
(Break) 3 vezes. Sem IA ([G1], [G2], [P1] não se aplicam). Blueprint com `confidential: true`; a interface (campo `cnpj`) vai no DESIGN, para a etapa 4 gravar.

**Caso positivo com Supabase (sintético).** Lançamentos novos entram numa tabela e o fluxo os leva ao destino: agenda do
Make a cada 15 minutos ([S4], 2.880 operações paradas por mês) → `supabase:searchRows` na fila com `processado` igual a
`false` e limite 50 ([S3]) → `supabase:upsertARecord` no destino, com a chave natural como `primary key` ([S5]) →
`supabase:upsertARecord` na fila, regravando a linha inteira com `processado = true`. Conexão com Project ID e chave
secreta, alcance = 2 tabelas, ler e gravar ([S1]). Antes do 1º fluxo rodar, a pessoa cola 1 SQL, copia 2 valores do
painel e cria 1 conexão ([S2]).

**Contraexemplo.** "A IA classifica a nota e lança direto no ERP." A skill recusa por [G1] e propõe: a IA grava a
sugestão numa planilha, a pessoa marca "aprovado", outro passo lança e registra o aceite ([G2]).

## Inventário do bundle

- `SKILL.md`
- `references/PROTOCOLO.md` · `references/ERROS_E_DIRETIVAS.md` · `references/GOVERNANCA_DO_FLUXO.md` · `references/PROMPTS_DE_IA.md`
- `references/MCP_MAKE.md` · `references/COPY.md` · `references/RUNTIME_COMPATIBILITY.md` · `references/SUPABASE.md`
- `assets/DESIGN_TEMPLATE.md` · `assets/blueprint-minimo.json`
- `scripts/checar_blueprint.py` — confere flow, confidencial, interface, credencial escrita e o Supabase só como banco (Python 3.9+, sem dependências)
- `manifest.json` · `evals/cases.json`

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
