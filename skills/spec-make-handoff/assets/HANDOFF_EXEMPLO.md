# HANDOFF: Boletos — Gmail, leitura com IA, aprovação e lançamento no ERP

> spec-make · ficha do fluxo para continuar depois · 1 arquivo por fluxo · atualizada 2026-10-15
> Fluxo (ou família) = o que você chama de "o fluxo de boletos". Parte = cada cenário dele no Make (1/2, 2/2). Esta
> ficha é sua: a próxima conversa lê só ela e os documentos anexados.
> Exemplo com ids inventados.

## Ficha

| Item | Valor |
|---|---|
| Status | na conta, gatilho ligado · 2 partes |
| Último teste | execução 9c1e7a2b-4d6f8a0c-2e4b6d8f-0a1c3e5b em 2026-10-14 · passou |
| Documentos | BRAINSTORM_BOLETOS.md · DEFINE_BOLETOS.md · DESIGN_BOLETOS.md · FICHA_DO_FLUXO_BOLETOS.md · RECIBO_BOLETOS.md |
| Blueprint publicado | boletos-1-2.blueprint.json · sha256 3f9a1c0e-7b2d4e6f-a8c0e2f4-b6d8fa1c-c3e5a7b9-d1f3b5c7-e9a1c3e5-f7b9d1a3 |
| Conta | organização 6300001 · equipe 1700001 · zona us2 |
| Gerada | com o conector do Make |

## Inventário e custódia

> Lido pelo Make em 2026-10-15. Custódia: o que a próxima conversa pode alterar.

| Recurso | id | Nome na conta | Estado | Custódia |
|---|---|---|---|---|
| Cenário | 6600101 | "Boletos 1/2 – Gmail → leitura (Claude) → pedido de aprovação" | ativo · sob demanda · lastEdit 2026-10-14T19:08:34Z | desta família |
| Cenário | 6600102 | "Boletos 2/2 – decisão (clique) → ERP contas a pagar" | ativo · imediato (webhook) · lastEdit 2026-10-14T19:12:06Z | desta família |
| Webhook | 2900101 | "Boletos – decisão" | ligado à parte 6600102 | desta família |
| Data store | 170101 | "Boletos – aprovação ERP" | 1 registro | desta família |
| Data store | 170102 | "erp_credenciais" | 1 registro | compartilhado com 4 cenários — só ler e acrescentar |
| Conexão | 11000001 · 7000001 | Gmail · Anthropic Claude | ok · Gmail expira em 2027-04-13 | fora do spec-make |

## Feito

- Parte 1/2 lê o boleto do e-mail com IA, grava pendente no data store 170101 e manda o pedido de aprovação (execução
  9c1e7a2b-4d6f8a0c-2e4b6d8f-0a1c3e5b, 2026-10-14).
- Parte 2/2 recebe o clique, pede confirmação e lança a conta a pagar no ERP; o aceite fica registrado no 170101
  (quem aceitou, quando, se editou).

## Falta

- Testar a recusa pelo link (parte 2/2) com um boleto de teste.
- Decidir se o boleto vencido vira aviso no mesmo dia ou só no resumo semanal.

## Casos e testes em aberto

- Boleto de arrecadação (48 dígitos) ainda não passou por um teste de aceite.

## Alertas (não tocar)

- Data store 170102 ("erp_credenciais"): usado por outros 2 fluxos; só ler e acrescentar, nunca apagar nem mudar a
  estrutura.
- Conexões 11000001 e 7000001: se expirarem, reautorize no Make; esta ficha não as altera.

## Prompt de retomada

```text
Use a skill spec-make-build. Anexe HANDOFF_BOLETOS.md e DESIGN_BOLETOS.md.
Onde paramos: as duas partes estão na conta e ligadas; o teste de aceite da aprovação passou em 2026-10-14. Falta
testar a recusa pelo link.
Último teste: execução 9c1e7a2b-4d6f8a0c-2e4b6d8f-0a1c3e5b em 2026-10-14, passou.
Próxima ação: rodar o teste de recusa na parte 6600102 com um boleto de teste.
Não tocar: data store 170102 (compartilhado com 4 cenários); conexões 11000001 e 7000001.
```

## Histórico de sessões

### 2026-10-15 — ficha criada a partir da conta

- As duas partes foram confirmadas pela pessoa (6600101 e 6600102) e lidas pelo Make, sem gravar nada.
- O data store 170102 é usado por 4 cenários: ficou como compartilhado.
- Próximo passo combinado: testar a recusa pelo link.
