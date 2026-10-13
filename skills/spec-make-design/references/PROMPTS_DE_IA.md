# Prompts de IA no fluxo — regra [P1]

Quando o fluxo tem um módulo de IA (OpenAI, Claude, Gemini ou agente de IA do Make), o texto do prompt não é escrito
nesta etapa. O DESIGN registra o inventário e o contrato; a etapa 4 gera cada prompt com a skill `sdd-prompt-builder`
(do SDD Starter), que recebe exatamente este contrato.

## Inventário (1 linha por prompt)

| Campo | O que escrever |
|---|---|
| nome | ex.: classificar-nota |
| módulo | o passo do fluxo onde o prompt é usado |
| versão | v1 |
| provedor e modelo | o app e o modelo escolhidos no módulo |
| entrada | o que o módulo recebe (campos do passo anterior) |
| saída e consumidor | formato exato da resposta e o passo que a usa |
| tipo | uma chamada (one-shot) ou processo que repete com a própria resposta (loop) |
| completude | o que a resposta precisa ter para estar completa |

## Contrato por prompt

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

## O dado vai na mensagem, não no prompt

O prompt do sistema é genérico e reutilizável. O dado de cada execução (a nota, o e-mail) entra na mensagem do
usuário do módulo, mapeado do passo anterior.
