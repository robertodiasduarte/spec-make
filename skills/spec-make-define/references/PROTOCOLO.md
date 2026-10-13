# Protocolo da etapa 2 — Define do fluxo

## 1. Abertura

As duas linhas da regra [E1]. Depois: "Vamos fechar o que o fluxo tem de fazer e como saber que ele funciona.
Nada é criado na conta nesta etapa."

## 2. Leitura do BRAINSTORM

Liste para você mesmo: decidido · a confirmar · cortado. Itens "a confirmar" viram pergunta ou ficam marcados.

## 3. Requisitos

| Campo | Regra |
|---|---|
| Problema | 1 frase: quem sofre, com quê, quanto custa hoje |
| Quem usa | Papel no escritório + a dor |
| Objetivos | MUST (sem isso o fluxo não serve) e SHOULD |
| Fora do escopo | Os cortes do BRAINSTORM + o que surgir aqui |

## 4. Critérios de aceite

Cada critério tem duas linhas: a frase de escritório e o EARS (ver EARS.md).

| ID | Frase de escritório | EARS |
|---|---|---|
| C1 | Quando chegar e-mail com nota, o fluxo guarda número, valor e emitente na planilha | When chega e-mail com anexo de nota, the fluxo shall gravar número, valor e emitente numa linha da planilha |
| C2 | Se a planilha estiver fora do ar, o fluxo tenta de novo e me avisa | If o Google Sheets falhar, then the fluxo shall tentar de novo em 15 min e avisar por e-mail depois da 3ª falha |

Mínimo de 1 critério If/Then. Considere também: While (enquanto um estado vale) e Where (se uma opção estiver ligada);
se não se aplicarem, escreva por quê em 1 linha.

## 5. Teste de aceite — regra [D1]

Use o bloco de VERIFY_GATE_EXECUCAO.md. Ele é o que a etapa 4 vai rodar.

## 6. Orçamento de operações

`operações por execução` = número de módulos que rodam por item (contando iteradores: cada item repete os módulos
dentro do laço). `execuções por mês` = frequência × volume. Mostre a conta e compare com o limite do plano.

## 7. Ambiguidades

Varra: escopo, dados, o que a pessoa vê, volume, integrações, o que pode dar errado, restrições, termos com duas
leituras, como saber que acabou. Cada lacuna vira `A CONFIRMAR: <pergunta>` no ponto exato e uma pergunta na conversa,
uma por mensagem. A resposta substitui a marca no corpo e entra no registro de esclarecimentos.

## 8. Clareza

0 = ausente · 1 = vago · 2 = claro mas incompleto · 3 = pronto. Problema, quem usa, objetivos, aceite, escopo.
Abaixo de 12, pergunte o que falta.

## 9. Documento e fecho

`assets/DEFINE_TEMPLATE.md`, entregue como `DEFINE_<FLUXO>.md`. Feche com [E1].
