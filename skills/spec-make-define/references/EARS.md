# EARS — a gramática dos critérios de aceite

EARS (Easy Approach to Requirements Syntax, Alistair Mavin, 2009) dá a cada critério uma forma que vira teste. As
palavras-chave ficam em inglês; o resto em português.

| Padrão | Forma | Exemplo de fluxo do Make | Como testar |
|---|---|---|---|
| Sempre | The fluxo **shall** … | The fluxo shall gravar a data de processamento em cada registro | Roda e confere o campo |
| Quando | **When** …, the fluxo **shall** … | When chega e-mail com nota, the fluxo shall gravar número e valor na planilha | Coloca o e-mail de teste e confere a linha |
| Enquanto | **While** …, the fluxo **shall** … | While a planilha de clientes estiver vazia, the fluxo shall não enviar nenhum e-mail | Prepara o estado e roda |
| Se der errado | **If** …, **then** the fluxo **shall** … | If o CNPJ não existir na Receita, then the fluxo shall gravar "não encontrado" e não parar | Roda com um CNPJ inválido |
| Se a opção estiver ligada | **Where** …, the fluxo **shall** … | Where o aviso por e-mail estiver ligado, the fluxo shall avisar quem confere | Roda com a opção ligada e desligada |

Regras:

1. Um critério, um comportamento observável.
2. Sem adjetivo sem número: "rápido" vira "em menos de 1 minuto".
3. Pelo menos um "Se der errado" quando o fluxo depende de app externo (quase sempre).
4. De 3 a 8 critérios por fluxo.

## Como ensinar (1 vez por conversa)

Na primeira vez que um critério aparecer, explique em 3 linhas, com um critério do fluxo da própria pessoa (nunca o do
CNPJ, que é só o exemplo deste arquivo):

1. "EARS é um jeito padronizado de escrever o que o fluxo tem de fazer, para virar teste."
2. "Cada critério começa por uma palavra que diz quando ele vale: When (quando), If/Then (se der errado), While
   (enquanto), Where (se a opção estiver ligada)."
3. O critério da pessoa nas três linhas: a frase de escritório, o EARS e `Em outras palavras: <frase do dia a dia>`.

Depois disso, não explique de novo: só escreva as três linhas de cada critério.
