# HANDOFF: {nome do fluxo}

> spec-make · ficha do fluxo para continuar depois · 1 arquivo por fluxo · atualizada {AAAA-MM-DD}
> Fluxo (ou família) = o que você chama de "o fluxo de {…}". Parte = cada cenário dele no Make (1/2, 2/2). Esta
> ficha é sua: a próxima conversa lê só ela e os documentos anexados.

## Ficha

| Item | Valor |
|---|---|
| Status | {na conta, gatilho ligado · na conta, sob demanda · em desenho · pausado} · {N} partes |
| Último teste | execução {id em 4 grupos de 8 com hífen} em {AAAA-MM-DD} · {passou · falhou} |
| Documentos | {BRAINSTORM_, DEFINE_, DESIGN_, FICHA_DO_FLUXO_ e RECIBO_ do fluxo, os que existirem} |
| Blueprint publicado | {arquivo .blueprint.json} · sha256 {8 grupos de 8 com hífen} |
| Conta | organização {id} · equipe {id} · zona {zona} |
| Gerada | {com o conector do Make · sem o conector do Make: os estados abaixo estão a confirmar na conta} |

## Inventário e custódia

> Lido pelo Make em {AAAA-MM-DD}. Custódia: o que a próxima conversa pode alterar.

| Recurso | id | Nome na conta | Estado | Custódia |
|---|---|---|---|---|
| Cenário | {id} | "{nome}" | {ativo · sob demanda · lastEdit AAAA-MM-DDTHH:MM:SSZ} | desta família |
| Webhook | {id} | "{nome}" | ligado à parte {id} | desta família |
| Data store | {id} | "{nome}" | {N} registros | {desta família · compartilhado com N cenários — só ler e acrescentar} |
| Conexão | {id} · {id} | {app} · {app} | {ok · expira em AAAA-MM-DD} | fora do spec-make |

## Feito

- {o que está pronto, com o que prova: execução, arquivo}

## Falta

- {o que falta, em ordem, começando por verbo}

## Alertas aceitos

{nenhum — ou uma linha por alerta aceito ([A2] de CONDUCAO.md): - ⚠️ AAAA-MM-DD · [regra] · o que falta · risco: 1 linha — continua em "Falta" até alguém corrigir}

## Casos e testes em aberto

- {caso não coberto · teste que ainda não rodou}

## Alertas (não tocar)

- {recurso compartilhado ou fora do spec-make, pelo id, e o motivo}

## Prompt de retomada

```text
Use a skill spec-make-{design · build}. Anexe HANDOFF_{FLUXO}.md e {DESIGN_{FLUXO}.md}.
Onde paramos: {2 ou 3 linhas}.
Último teste: execução {id em 4 grupos de 8} em {AAAA-MM-DD}, {passou · falhou}.
Próxima ação: {1 ação, com o id do recurso}.
Não tocar: {ids dos recursos compartilhados e fora do spec-make}.
```

## Histórico de sessões

### {AAAA-MM-DD} — {o que esta sessão fez}

- {3 a 6 linhas}
