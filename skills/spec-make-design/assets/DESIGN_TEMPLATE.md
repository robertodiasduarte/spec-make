# DESIGN: {nome do fluxo}

> spec-make · Etapa 3 de 4 · {data} · a partir de DEFINE_{FLUXO}.md

## Conta

organizationId {n} · teamId {n} · plano {nome} · conferido pelo MCP: {sim | não: a confirmar na conta}

## O fluxo, módulo a módulo

| # | Módulo (`app:Modulo` vN) | Rótulo no editor | Recebe | Devolve | Conexão | Alcance |
|---|---|---|---|---|---|---|
| 1 | {…} | {…} | {…} | {…} | {nome da conexão · "a autorizar no build" · "não precisa"} | {Supabase: motivo · tabelas · operações ([S1]) · "não se aplica: o fluxo não usa Supabase"} |

{Uma linha por módulo `http:*` ([N1]): "módulo <n>: o app <X> não tem módulo para <operação> — conferido em `app-modules_list` em <data>" · ou "nenhum módulo HTTP"}

## Fontes consultadas

| App | URL | Data | Módulo e versão lidos | Divergência com a conta |
|---|---|---|---|---|
| {app} | https://apps.make.com/{app} | {AAAA-MM-DD} | {…} | {nenhuma · qual · "não consultado"} |

## Quando algo falha

| # | Diretiva | Detalhe | Por quê | Pergunta de negócio e resposta |
|---|---|---|---|---|
| 2 | Break | 3 tentativas, 15 min | {…} | {pergunta} → {resposta} |

## Governança

| Regra | Situação | Como |
|---|---|---|
| [G3] Chave natural | {atendida · não se aplica (não grava)} | {chave e como evita duplicar} |
| [G1] Aceite humano | {atendida · não se aplica (sem IA que grava)} | {forma e quem aceita} |
| [G2] Registro do aceite | {atendida · não se aplica} | {onde e os 6 campos} |

## Prepare o banco

{Fluxo que toca Supabase ([S2], [S5]): o SQL para colar no SQL Editor antes da etapa 4 e a contagem do que a pessoa
faz fora do Make: 1 colagem de SQL, 2 valores copiados do painel (Project ID e chave) e 1 conexão no Make.
Sem Supabase: "não se aplica: o fluxo não usa Supabase".}

```sql
{SQL de SUPABASE.md com os nomes do fluxo}
```

## Relógio

{Agenda do Make com o intervalo, ou sob demanda ([S4]), com o motivo. Sem Supabase: "não se aplica: o fluxo não usa Supabase".}

## Prompts e skills

| Nome | Tipo | Módulo ou cenário | Entrada | Saída e consumidor | Gera na etapa 4 |
|---|---|---|---|---|---|
| {…} | {prompt · skill} | {…} | {…} | {…} | {prompt-builder-by-rdd · skill-builder-by-rdd} |

{Contrato de cada linha (PROMPTS_E_SKILLS.md) · ou "não se aplica: o fluxo não tem módulo de IA nem é acionado pelo assistente"}

## Interface do fluxo

{Só para fluxo sob demanda que recebe dados. Gravada na etapa 4 com scenarios_set-interface; fora do blueprint.}

```json
{"input": [{"name": "…", "type": "text", "label": "…", "required": true}], "output": [{"name": "…", "type": "text"}]}
```

## Custo

{operações por execução} por execução · {execuções por mês} · {total}/mês de {limite}.
Operações paradas por mês (agenda do Make): {disparos por mês} × {operações do disparo vazio} = {n} · ou 0 (sob demanda).

## Validação

| Conferência | Resultado |
|---|---|
| validate_module_configuration (por módulo) | {ok · erros} |
| validate_blueprint_schema | {ok · erros} |
| validate_scenario_interface | {ok · não se aplica} |
| checar_blueprint.py | {OK · problemas} |

Validado não quer dizer testado: o teste de aceite do DEFINE roda na etapa 4.

## Blueprint

Arquivo entregue junto: `{FLUXO}.blueprint.json`.

```json
{blueprint}
```

## Alertas aceitos

{nenhum — ou uma linha por alerta aceito ([A2] de CONDUCAO.md): - ⚠️ AAAA-MM-DD · [regra] · o que falta · risco: 1 linha}

## Próxima etapa

Abra uma conversa nova, anexe o BRAINSTORM, o DEFINE e este DESIGN e diga: Use a skill spec-make-build.
