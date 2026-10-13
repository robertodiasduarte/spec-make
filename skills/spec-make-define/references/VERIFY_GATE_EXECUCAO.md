# Teste de aceite por execução — regra [D1]

## Por que execução e não validação

O MCP do Make tem validadores de blueprint e de módulo. Eles conferem a forma, não o funcionamento: num teste real
(13/10/2026), os dois aprovaram um blueprint que falhou na primeira execução. O único teste que diz se o fluxo
funciona é rodá-lo com uma amostra e comparar o resultado.

## O bloco (vai no DEFINE)

```text
TESTE DE ACEITE
modo: sob demanda com a amostra | gatilho real
amostra: <descrição; sem dado pessoal real; origem: pública | inventada>
resultado esperado: <valores concretos que devem aparecer, e onde>
grava registros: sim | não
segunda execução: <se grava: rodar a mesma amostra de novo (gatilho real: recolocar a mesma amostra na origem de teste antes); esperado = mesma contagem de registros no destino>
operações estimadas: <por execução> × <execuções do teste> = <total>
passa quando: <resultado esperado igual ao obtido> e <segunda execução sem registro novo, se grava>
```

## Como escolher o modo

| O fluxo começa com | Modo | Como a etapa 4 roda |
|---|---|---|
| Entrada que você informa (sob demanda) | sob demanda com a amostra | `scenarios_run` com os dados da amostra |
| Webhook | sob demanda com a amostra | Envia a amostra ao endereço do webhook ou roda com os dados |
| E-mail, planilha, pasta, agenda | gatilho real | Coloca a amostra numa **origem de teste** (um rótulo, aba ou pasta só para o teste, nunca a caixa, planilha ou pasta real do escritório) e roda uma vez. Se o fluxo grava, coloca a **mesma** amostra de novo na origem de teste (reenvia o mesmo e-mail de teste ou o marca de novo como não lido; recoloca a mesma linha ou o mesmo arquivo) e roda de novo: a contagem no destino tem de ser a mesma |

## O que recusar

- "O blueprint foi validado" como teste: recuse e peça amostra e resultado esperado.
- Resultado esperado sem valor ("tem que dar certo"): pergunte o que deve aparecer.
- Fluxo que grava sem a segunda execução: recuse como incompleto. Sem ela, um fluxo que repete o mesmo item
  (e-mail reaberto, linha reprocessada, tentativa depois de falha) duplica registros sem ninguém perceber.
- Amostra com dado pessoal real: troque por dado inventado ou público.
