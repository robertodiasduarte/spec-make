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
