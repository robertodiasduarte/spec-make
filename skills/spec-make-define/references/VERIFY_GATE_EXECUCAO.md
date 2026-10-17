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
segunda execução: <se grava: rodar a mesma amostra de novo (gatilho real: um item com a mesma chave natural — ver a tabela abaixo); esperado = mesma contagem de registros no destino>
operações estimadas: <por execução> × <execuções do teste> = <total>
passa quando: <resultado esperado igual ao obtido> e <segunda execução processou o item (operações > 0) sem registro novo, se grava>
```

## Como escolher o modo

| O fluxo começa com | Modo | Como a etapa 4 roda |
|---|---|---|
| Entrada que você informa (sob demanda) | sob demanda com a amostra | `scenarios_run` com os dados da amostra |
| Webhook | sob demanda com a amostra | Envia a amostra ao endereço do webhook ou roda com os dados |
| E-mail, planilha, pasta, agenda | gatilho real | Coloca a amostra numa **origem de teste** (um rótulo, aba ou pasta só para o teste, nunca a caixa, planilha ou pasta real do escritório) e roda uma vez. Se o fluxo grava: a 2ª passada tem de levar ao fluxo um item com a **mesma chave natural** do DESIGN. Chave de conteúdo (chave de acesso da nota, CNPJ, número do documento): ponha na origem de teste um item novo com o mesmo conteúdo (reenvie o e-mail de teste, copie a linha ou o arquivo) — a contagem no destino não pode mudar. Chave que é o id do item na origem (id do e-mail, do arquivo, número da linha): um item novo é outro registro, e um 2º registro aí é o certo; marque o mesmo e-mail de novo como não lido e rode; se o gatilho não o pegar de novo: alerta [A1] — a chave pelo id do item não prova a 2ª passada; recomende trocar, na etapa 3, por uma chave de conteúdo. Em qualquer caso, confira em `executions_get` que a 2ª execução processou o item (operações maiores que zero, iguais às da 1ª): execução que não processou nada não testa nada. |

## O que vira alerta

- "O blueprint foi validado" como teste: alerta [A1]; peça amostra e resultado esperado.
- Resultado esperado sem valor ("tem que dar certo"): pergunte o que deve aparecer.
- Fluxo que grava sem a segunda execução: alerta [A1] — sem ela, um fluxo que repete o mesmo item duplica registros sem
  ninguém perceber (e-mail reaberto, linha reprocessada, tentativa depois de falha).
- Amostra com dado pessoal real: bloqueio ([X1]); troque por dado inventado ou público.
