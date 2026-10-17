---
name: spec-make-design
license: MIT
description: "Conduz a etapa 3 de 4 do spec-make: transforma o DEFINE de um fluxo do Make num desenho técnico ancorado na conta da pessoa — só módulos que existem nela (consultados pelo MCP do Make), a diretiva de erro de cada módulo, a chave que impede registro duplicado, o aceite humano antes de a IA gravar e o blueprint já validado e conferido. Use quando a pessoa anexar o BRAINSTORM e o DEFINE de um fluxo do Make e pedir o desenho ou o blueprint. Entrega DESIGN_NOME-DO-FLUXO.md com o blueprint. Não cria nada na conta (spec-make-build) e não escreve os prompts de agentes de IA nem as skills do fluxo (prompt-builder-by-rdd e skill-builder-by-rdd). Período de consulta e de cálculo: não se aplicam."
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: "1.4.0"
  updated: "2026-10"
---

# spec-make — Etapa 3: Design do fluxo

Na primeira resposta desta skill, comece com a linha de versão, uma vez só:
`spec-make-design v1.4.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/spec-make/releases/latest`
Em seguida, e em toda resposta, o mapa de posição ([E1]). A conversa segue
[references/CONDUCAO.md](references/CONDUCAO.md): mapa, glossário, pergunta de decisão, alerta e bloqueios.

## Quick start

1. Receba o BRAINSTORM e o DEFINE do fluxo. Sem o DEFINE: [A3] de references/CONDUCAO.md. Liste no começo os alertas
   aceitos das etapas anteriores ([A2]).
2. Com o MCP do Make, confirme cada módulo na conta (`app-modules_list`, `app-module_get`), o módulo oficial antes do
   HTTP **[N1]**. Sem o MCP, siga **[M1]**.
   Leia a documentação pública de cada app uma vez **[W1]**.
3. Desenhe o fluxo módulo a módulo, como ele aparece no editor do Make.
4. Escolha a diretiva de erro de cada módulo e faça à pessoa só a pergunta de negócio ([references/ERROS_E_DIRETIVAS.md](references/ERROS_E_DIRETIVAS.md)).
5. Aplique as regras de governança **[G1]**, **[G2]**, **[G3]** ([references/GOVERNANCA_DO_FLUXO.md](references/GOVERNANCA_DO_FLUXO.md)).
   Se o fluxo toca Supabase, aplique também **[S1]** a **[S5]** ([references/SUPABASE.md](references/SUPABASE.md)).
6. Se houver módulo de IA, ou o fluxo for acionado pelo assistente, registre o inventário de prompts e skills **[P1]**
   ([references/PROMPTS_E_SKILLS.md](references/PROMPTS_E_SKILLS.md)).
7. Monte o blueprint com **[C1]**, valide pelo MCP e confira com `scripts/checar_blueprint.py`.
8. Entregue `DESIGN_<FLUXO>.md` usando [assets/DESIGN_TEMPLATE.md](assets/DESIGN_TEMPLATE.md) e feche com **[E1]**.

## Quando usar / Quando não usar

Usar depois do Define, quando os critérios e o teste de aceite do fluxo estão fechados. Com o `HANDOFF_<FLUXO>.md`
anexado, o desenho parte dos ids que a ficha marca como `desta família`: altere o que existe em vez de desenhar um fluxo
novo, e não planeje mudar recurso `compartilhado` ou `fora do spec-make`.

Sem o DEFINE, siga o [A3]. Não usar para criar, ativar ou rodar o fluxo: isso é a etapa 4. Não escreve o texto dos
prompts nem as skills do fluxo: registra o inventário e o contrato, e a etapa 4 os gera com as skills
`prompt-builder-by-rdd` e `skill-builder-by-rdd`.

## Dados necessários

- `BRAINSTORM_<FLUXO>.md` e `DEFINE_<FLUXO>.md`.
- `organizationId` e `teamId` (do BRAINSTORM ou de `environment_get`).
- Respostas da pessoa às perguntas de negócio (o que fazer quando cada app falha; quem aprova a sugestão da IA).

## Procedimento passo a passo

Siga [references/PROTOCOLO.md](references/PROTOCOLO.md). Resumo:

1. **Módulos reais.** Para cada passo, `app-modules_list` do app escolhido e `app-module_get` do módulo, no formato
   de instruções, pelo [N1]. Use só nomes que voltaram dessas chamadas; nunca invente `app:Modulo`.
2. **Desenho.** Lista numerada de módulos, na ordem do editor, com o que entra e o que sai de cada um.
3. **Erros.** Diretiva por módulo (ERROS_E_DIRETIVAS.md); à pessoa, só a pergunta de negócio ("se o Omie estiver fora
   do ar: tento de novo em 15 min ou te aviso?").
4. **Governança.** [G1], [G2] e [G3] abaixo. Fluxo que toca Supabase: [S1] a [S5], com as receitas de
   SUPABASE.md (alcance da conexão, os 5 módulos do banco, o laço da fila, o relógio e o SQL do `Prepare o banco`).
5. **Prompts e skills.** [P1] abaixo.
6. **Blueprint.** Monte o JSON com [C1]. Valide cada módulo com `validate_module_configuration`, o todo com
   `validate_blueprint_schema` e a interface com `validate_scenario_interface`. Depois, rode
   `python3 scripts/checar_blueprint.py <arquivo>` (ou faça a mesma conferência lendo, se o ambiente não executa
   código). Validado não quer dizer testado: o teste é a etapa 4.
7. **Custo.** Confirme as operações por execução contra o orçamento do DEFINE, somando as operações paradas quando o
   relógio é a agenda do Make ([S4]).
8. **Documento.** Preencha o template com o blueprint no fim e feche com [E1].

**[G1] Aceite humano.** Se a saída de um módulo de IA grava, classifica ou altera lançamento, documento fiscal ou
cadastro do escritório, o fluxo tem um passo de aceite por pessoa identificada antes da gravação (fila de sugestões
numa planilha, aprovação por e-mail ou formulário; a gravação só acontece pela ação da pessoa). Sem esse passo: alerta
[A1] — a IA grava lançamento, documento ou cadastro sem que ninguém responda por ele.

**[G2] Registro do aceite.** Quando o fluxo tem IA cuja sugestão é aceita, cada aceite é registrado fora do histórico
de execução do Make (planilha ou data store da pessoa; quando o fluxo já usa Supabase, a 1ª opção é uma tabela de
auditoria só de acréscimo, com o SQL de [S5]) com seis campos: modelo, versão do prompt, sugestão original,
quem aceitou, quando (UTC) e se editou antes de aceitar. Sem esse registro: alerta [A1] — não há como provar quem
aceitou cada sugestão nem medir quanto a IA erra.

**[G3] Chave natural.** Se o fluxo cria registros num sistema do escritório (ERP, planilha, CRM, data store), o DESIGN
declara a chave natural do registro (id do e-mail, chave de acesso da nota, CNPJ, id da transação) e a regra "já existe ⇒ não grava de novo"
(consultar antes de gravar, ou gravar substituindo pela chave). Quando o destino é uma tabela do Supabase, a chave
existe nela como restrição ([S5]). Sem a chave: alerta [A1] —
o mesmo item processado de novo (e-mail reaberto, nova tentativa) vira registro duplicado.

**[S1] Chave do Supabase.** Se o fluxo toca Supabase (app `supabase`, `supabase-management`, `postgres` ou HTTP para
o endereço de um projeto Supabase, em qualquer caminho), a conexão Supabase usa o diálogo padrão do app no Make
(Project ID e chave secreta, copiados do painel do Supabase) e o DESIGN preenche a coluna `alcance` com o motivo ("o app
Supabase do Make só conecta com chave secreta; ela ignora o RLS"), as tabelas e as operações. `postgres` (conexão direta)
e `supabase-management` ficam fora do alcance do kit ([X2]). Sem o alcance: alerta [A1] — quem mexer no fluxo depois
não sabe o que a chave secreta alcança.

**[S2] Só módulos do banco.** Se o fluxo toca Supabase, do app `supabase` entram só `searchRows`, `createARow`,
`upsertARecord`, `getRowsCount` e `deleteRows`, e a pessoa não faz, antes do 1º fluxo rodar, mais que 1 colagem de SQL,
copiar o Project ID e a chave do painel e criar 1 conexão no Make. Edge function, webhook de qualquer tipo, Database
Webhook, `pg_cron`, `supabase:watchEvents`, `supabase:makeAnApiCall` e módulo HTTP para o endereço de um projeto Supabase
ficam fora do alcance do kit ([X2]): diga isso e proponha o caminho só com o banco, sem perguntar.

**[S3] Fila de pendentes.** Se o fluxo toca Supabase e lê uma fila, o DESIGN desenha o laço agenda do Make →
`searchRows` com `processado` igual a `false` e um limite → processa → `upsertARecord` pela primary key da fila, que
regrava a linha inteira (as colunas lidas mais `processado = true` e `processado_em`). No blueprint, o valor do filtro
de verdade/falso vai em texto (`"false"`, nunca o booleano `false`: o Make ignora a condição e a busca lê qualquer linha).
Sem pendente, a busca devolve 1 pacote vazio: o módulo seguinte leva o filtro "`{{id da busca.<coluna>}}` existe", senão
ele roda com campos vazios e falha. Gatilho que não seja a agenda do Make nem a execução sob demanda fica fora do alcance
do kit ([X2]). Filtro por coluna vazia: alerta [A1] — o Make não filtra coluna vazia, e a busca lê a fila inteira de
novo a cada disparo.

**[S4] Relógio.** Se o fluxo toca Supabase, o DESIGN declara no bloco `Relógio` como o fluxo dispara — agenda do Make
com o intervalo, ou sob demanda — e, com agenda, soma no custo as operações paradas: disparos por mês × operações do
disparo vazio. Se o total passar do orçamento do DEFINE: alerta [A1] — o plano acaba antes do fim do mês e o fluxo
para; recomende um intervalo maior.

**[S5] Banco preparado.** Se o fluxo toca Supabase e grava no banco, o `Prepare o banco` traz o SQL para o SQL Editor:
a chave natural como `primary key` da tabela de destino que o `upsertARecord` grava (a fila, que aceita a chave repetida,
tem o `id` como `primary key` e o marcador a grava por ele), `processado` e `processado_em` quando o fluxo lê pendentes,
RLS ligado sem política, coluna de valor em dinheiro como `numeric(18,2)` e, com IA aceita, a tabela de auditoria só de
acréscimo (chave do aceite como `primary key`, os 6 campos de [G2] `not null`, gatilho que recusa alterar, apagar e
truncar, e a view da taxa de correção). Os 6 campos vêm do passo de aceite, gravados antes do "processa" e nunca
recalculados, para a repetição do mesmo aceite ser idêntica. O DESIGN diz que a pessoa lê a view da taxa de correção no
SQL Editor do Supabase (`select * from public.<auditoria>_taxa_de_correcao`). Chave natural que não é a `primary key` da tabela de
destino do `upsertARecord`, coluna de valor em `real`, `float4`, `float8` ou `double precision`, rateio sem a regra do
centavo residual, campo da auditoria anulável, auditoria sem o gatilho ou sem a view: alerta [A1] — nomeie a coluna, o
campo ou o rateio; o risco é duplicar lançamento, arredondar dinheiro errado ou perder a prova do aceite.

**[W1] Documentação do Make.** Para cada app do fluxo, consulte a documentação pública do Make
(`https://apps.make.com/<app>`) uma vez e anote em `Fontes consultadas` a URL, a data, o módulo e a versão. Se ela
divergir de `app-modules_list`, vale a conta, e o DESIGN anota a divergência. Sem acesso à web, escreva "não
consultado" — nunca afirme uma consulta que não fez — e faça o alerta [A1]: o módulo pode ter mudado desde a
documentação que você conhece.

**[P1] Prompts e skills do fluxo.** Se o fluxo tem módulo de IA (OpenAI, Claude, Gemini ou agente de IA do Make),
registre cada prompt no inventário de PROMPTS_E_SKILLS.md com `tipo: prompt`. Se o fluxo é sob demanda com interface e a
pessoa vai acioná-lo pelo assistente, ou ela pede uma skill em volta do fluxo, registre também uma linha `tipo: skill`.
O texto não é escrito aqui: a etapa 4 gera cada prompt com a skill `prompt-builder-by-rdd` e cada skill com a skill
`skill-builder-by-rdd`, a partir desse contrato. Fluxo com módulo de IA e sem esse inventário: alerta [A1] — sem o
contrato, a etapa 4 escreve um prompt provisório que ninguém conferiu.

**[N1] Módulo oficial primeiro.** Para cada passo do fluxo, procure primeiro o módulo do próprio app no Make
(`apps_recommend`, depois `app-modules_list` e `app-module_get`) e só depois considere o módulo HTTP genérico
(`http:*`). HTTP só entra com o motivo escrito no documento: "o app <X> não tem módulo para <operação> — conferido em
`app-modules_list` em <data>". HTTP sem esse motivo, ou com módulo oficial disponível: alerta [A1] — a chamada HTTP pede
endereço, cabeçalho e autenticação montados à mão, e o módulo oficial já traz a conexão e os campos. Os apps embutidos do
Make (data store, roteador, entrada sob demanda) não contam como HTTP. Com o Supabase, HTTP fica fora do alcance ([X2]).

**[C1] Confidencial.** Todo blueprint sai com `metadata.scenario.confidential: true`. O escritório trata dado de
cliente; com a opção ligada, o Make não guarda os dados de cada passo no histórico.

**[M1] Sem o conector do Make.** Se a conversa não tiver o MCP do Make, avise em uma frase e siga no papel: escolha
módulos pela documentação pública, marque cada um como "a confirmar na conta" e não declare o blueprint validado.

**[E1] Etapa 3 de 4.** Toda resposta abre com o mapa de posição ([K1] de references/CONDUCAO.md), que começa por
"Etapa 3 de 4 · Design"; a primeira resposta traz antes a linha de versão. O fecho segue [K5]: entrega o arquivo
`DESIGN_<FLUXO>.md`, pede para salvá-lo e diz a frase exata da próxima etapa: "Abra uma conversa nova, anexe o
BRAINSTORM, o DEFINE e este DESIGN e diga: Use a skill spec-make-build."

## Validações e checklist de qualidade

- [ ] Toda resposta com o mapa de posição; alertas aceitos das etapas anteriores listados no começo ([A2])
- [ ] Todo `module` do blueprint voltou de `app-modules_list` (ou está marcado "a confirmar na conta" em [M1])
- [ ] [N1]: módulo oficial por passo; todo `http:*` com a linha de motivo
- [ ] Diretiva de erro escolhida e justificada por módulo
- [ ] [G1], [G2] e [G3] atendidas, declaradas "não se aplica" com o motivo, ou com o alerta [A1] aceito e registrado
- [ ] Fluxo que toca Supabase: [S1] a [S5] atendidas (coluna `alcance`, `Prepare o banco`, `Relógio`); sem Supabase, as 3 seções dizem "não se aplica: o fluxo não usa Supabase"
- [ ] `Fontes consultadas` com URL e data de cada app, ou "não consultado" [W1]
- [ ] Inventário [P1] de prompts e skills quando há módulo de IA ou o fluxo é acionado pelo assistente
- [ ] `confidential: true`; fluxo sob demanda com entrada: campos no módulo 1, bloco "Interface" no DESIGN e nenhuma chave `interface` no blueprint
- [ ] Três validações do MCP sem erro e `checar_blueprint.py` OK
- [ ] Operações por execução dentro do orçamento do DEFINE
- [ ] Seção `Alertas aceitos` preenchida (ou "nenhum") e fecho [K5] com a frase da próxima etapa

## Tratamento de exceções

- **Módulo não existe na conta:** procure alternativa (`apps_recommend`); HTTP genérico só pelo [N1], com o motivo.
- **App premium fora do plano:** avise e ofereça alternativa.
- **Validação falha:** corrija pelo erro devolvido e valide de novo. Depois de 3 tentativas no mesmo módulo: alerta [A1]
  — o módulo pode não aceitar essa configuração na sua conta; com "Seguir assim", o DESIGN sai com o módulo marcado
  "validação falhou" e a etapa 4 confere de novo.
- **Alerta de [G1], [G2] ou [G3]:** diga exatamente o que falta e ofereça o desenho com o passo incluído.
- **A pessoa quer `postgres` ou `supabase-management` "porque é mais fácil":** fora do alcance do kit ([X2]): explique
  em uma frase o alcance da senha ou do token (o banco inteiro, ou todos os projetos) e ofereça o app `supabase` com os
  módulos do banco ([S1], [S2]).
- **A pessoa quer a IA gravando direto:** alerta [A1] pelo [G1]: explique em uma frase por que o aceite importa (quem
  responde pelo lançamento é o profissional) e recomende manter o passo de aceite.

## Examples

**Caso positivo (sintético).** DEFINE do cadastro por CNPJ. Módulos confirmados: entrada sob demanda, `brasil-api`
Buscar CNPJ, data store "Adicionar ou substituir registro" com a chave = CNPJ ([G3]). Erro na Brasil API: tenta de novo
(Break) 3 vezes. Sem IA ([G1], [G2], [P1] não se aplicam). Blueprint com `confidential: true`; a interface (campo `cnpj`) vai no DESIGN, para a etapa 4 gravar.

**Caso positivo com Supabase (sintético).** Lançamentos novos entram numa tabela e o fluxo os leva ao destino: agenda do
Make a cada 15 minutos ([S4], 2.880 operações paradas por mês) → `supabase:searchRows` na fila com `processado` igual a
`false` e limite 50, com o filtro "o `id` existe" no módulo seguinte ([S3]) → `supabase:upsertARecord` no destino, com a chave natural como `primary key` ([S5]) →
`supabase:upsertARecord` na fila, regravando a linha inteira com `processado = true`. Conexão com Project ID e chave
secreta, alcance = 2 tabelas, ler e gravar ([S1]). Antes do 1º fluxo rodar, a pessoa cola 1 SQL, copia 2 valores do
painel e cria 1 conexão ([S2]).

**Contraexemplo.** "A IA classifica a nota e lança direto no ERP." A skill faz o alerta do [G1] e recomenda: a IA grava
a sugestão numa planilha, a pessoa marca "aprovado", outro passo lança e registra o aceite ([G2]).

## Inventário do bundle

- `SKILL.md`
- `references/PROTOCOLO.md` · `references/ERROS_E_DIRETIVAS.md` · `references/GOVERNANCA_DO_FLUXO.md` · `references/PROMPTS_E_SKILLS.md`
- `references/CONDUCAO.md` — mapa de posição, glossário, pergunta de decisão, alerta, alertas aceitos e bloqueios
- `references/MCP_MAKE.md` · `references/COPY.md` · `references/RUNTIME_COMPATIBILITY.md` · `references/SUPABASE.md`
- `assets/DESIGN_TEMPLATE.md` · `assets/blueprint-minimo.json`
- `scripts/checar_blueprint.py` — confere flow, confidencial, interface, credencial escrita, o Supabase só como banco e o HTTP genérico [N1]; sai 1 com ERRO, 3 só com AVISO (Python 3.9+, sem dependências)
- `manifest.json` · `evals/cases.json`

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
