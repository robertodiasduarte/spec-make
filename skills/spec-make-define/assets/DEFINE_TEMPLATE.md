# DEFINE: {nome do fluxo}

> spec-make · Etapa 2 de 4 · {data} · a partir de BRAINSTORM_{FLUXO}.md

## Problema

{1 frase}

## Quem usa

| Papel | Dor |
|---|---|
| {…} | {…} |

## Objetivos

| Prioridade | Objetivo |
|---|---|
| MUST | {…} |
| SHOULD | {…} |

## Critérios de aceite

| ID | Frase de escritório | EARS |
|---|---|---|
| C1 | {Quando …, o fluxo …} | {When …, the fluxo shall …} |
| C2 | {Se …, o fluxo …} | {If …, then the fluxo shall …} |

While: {critério ou "não se aplica porque …"} · Where: {critério ou "não se aplica porque …"}

## Teste de aceite

```text
TESTE DE ACEITE
modo: {sob demanda com a amostra | gatilho real}
amostra: {…} (origem: {pública | inventada})
resultado esperado: {valores e onde aparecem}
grava registros: {sim | não}
segunda execução: {mesma amostra; esperado = mesma contagem no destino | não se aplica: o fluxo não grava}
operações estimadas: {n} × {n} = {n}
passa quando: {…}
```

## Orçamento de operações

{operações por execução} × {execuções por mês} = {total}/mês, de {limite do plano} ({percentual}%).

## Fora do escopo

- {…}

## Esclarecimentos

- {pergunta} → {resposta}; integrado em {seção}

## Clareza

| Problema | Quem usa | Objetivos | Aceite | Escopo | Total |
|---|---|---|---|---|---|
| {0-3} | {0-3} | {0-3} | {0-3} | {0-3} | {n}/15 |

## Próxima etapa

Abra uma conversa nova, anexe o BRAINSTORM e este DEFINE e diga: Use a skill spec-make-design.
