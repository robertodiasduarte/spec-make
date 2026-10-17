# Prompts e skills do fluxo — regra [P1]

Quando o fluxo tem um módulo de IA (OpenAI, Claude, Gemini ou agente de IA do Make), o texto do prompt não é escrito
nesta etapa. Quando o fluxo é sob demanda com interface e a pessoa vai acioná-lo pelo assistente (o MCP do Make mostra
o cenário como uma ferramenta), ou quando ela pede uma skill em volta do fluxo, a skill também não é escrita aqui. O
DESIGN registra o inventário e o contrato; a etapa 4 gera:

| tipo | Quem gera | Quando | Instalação |
|---|---|---|---|
| prompt | a skill `prompt-builder-by-rdd` | antes de criar o fluxo (o prompt vai no módulo de IA) | `https://github.com/robertodiasduarte/skills-by-rdd/releases/latest/download/prompt-builder-by-rdd.zip` |
| skill | a skill `skill-builder-by-rdd` | depois do teste aprovado (a ferramenta MCP do cenário só tem nome depois que ele existe com a interface gravada) | `https://github.com/robertodiasduarte/skills-by-rdd/releases/latest/download/skill-builder-by-rdd.zip` |

Builder não instalado: a etapa 4 mostra o link e segue — prompt provisório escrito pelo contrato, com alerta; skill não
gerada, com alerta.

## Inventário (1 linha por prompt ou skill)

| Campo | O que escrever |
|---|---|
| nome | ex.: classificar-nota |
| tipo | prompt (módulo de IA) ou skill (fluxo acionado pelo assistente) |
| módulo | o passo do fluxo onde o prompt é usado; para skill, o cenário que ela aciona |
| versão | v1 |
| provedor e modelo | o app e o modelo escolhidos no módulo (só prompt) |
| entrada | o que o módulo recebe (campos do passo anterior); para skill, os campos da interface |
| saída e consumidor | formato exato da resposta e o passo que a usa |
| repetição | uma chamada (one-shot) ou processo que repete com a própria resposta (loop) — só prompt |
| completude | o que a resposta precisa ter para estar completa |

## Contrato por prompt (`tipo: prompt`)

| Campo | O que escrever |
|---|---|
| tom e público | quem lê a resposta (a planilha, o cliente, a pessoa que aprova) |
| formato da saída | texto, JSON com campos nomeados, uma palavra de uma lista fechada |
| se faltar dado | o que responder quando a entrada vier incompleta |
| autônomo ou com aceite | com aceite sempre que grava ([G1]) |
| verificação | como o próprio prompt confere a resposta antes de devolver |
| teste mínimo | 1 entrada de exemplo (sem dado pessoal real) e a saída esperada |
| material de referência | texto literal de regra, tabela ou lista que o prompt precisa (não só um link) |
| decisões fechadas | provedor, modelo, formato — o gerador não reabre |

## Contrato por skill (`tipo: skill`)

| Campo | O que escrever |
|---|---|
| ferramenta MCP | o nome que o MCP do Make dá ao cenário (lido depois de criado, na etapa 4) |
| campos da interface | nome, tipo, obrigatório ou não e um exemplo tirado da amostra (sem dado pessoal real) |
| o que a resposta devolve | os campos de saída do cenário e o que a skill diz à pessoa com eles |
| exemplo de uso | 1 pedido da pessoa e a chamada que a skill faz |
| limite | a skill só chama o cenário; não grava nada fora dele |

## O dado vai na mensagem, não no prompt

O prompt do sistema é genérico e reutilizável. O dado de cada execução (a nota, o e-mail) entra na mensagem do
usuário do módulo, mapeado do passo anterior.
