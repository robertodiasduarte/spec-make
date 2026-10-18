# spec-make

Método em quatro etapas para criar fluxos no **Make** conversando com a IA, com o **MCP do Make** conectado no
Claude ou no ChatGPT. Cada etapa é uma skill e entrega um documento; a última cria o fluxo na sua conta, testa com a
sua amostra e só liga o gatilho quando você disser sim.

| Etapa | Skill | Você sai com |
|---|---|---|
| 1 | `spec-make-brainstorm` | A ideia do fluxo, conferida na sua conta: apps nativos, conexões, plano |
| 2 | `spec-make-define` | O que o fluxo tem de fazer e o teste de aceite (amostra + resultado esperado) |
| 3 | `spec-make-design` | O fluxo módulo a módulo, o que fazer quando cada app falha e o blueprint validado |
| 4 | `spec-make-build` | O fluxo criado e testado na sua conta, o recibo do teste, a ficha do fluxo e a ficha para continuar depois |
| — | `spec-make-handoff` | A ficha do fluxo com os números da sua conta e a frase para retomar numa conversa nova |

Para parar e continuar outro dia — em qualquer etapa — ou para mudar um fluxo que já roda, use a `spec-make-handoff`:
ela lê a sua conta (sem gravar nada), guarda a ficha do fluxo com os números de cada cenário, webhook e data store, diz
o que a próxima conversa pode alterar e escreve a frase para retomar.

Fluxo com agente de IA dentro (OpenAI, Claude, Gemini)? Instale também a
[`prompt-builder-by-rdd`](https://github.com/robertodiasduarte/skills-by-rdd/releases/latest/download/prompt-builder-by-rdd.zip),
que escreve os prompts a partir do contrato que a etapa 3 registra. Vai acionar o fluxo pelo assistente? A
[`skill-builder-by-rdd`](https://github.com/robertodiasduarte/skills-by-rdd/releases/latest/download/skill-builder-by-rdd.zip)
cria a skill que chama o fluxo. Sem elas, a etapa 4 mostra como instalar e segue, com um alerta.

## Antes de começar

1. Uma conta no Make. Testado no plano Core; o plano Free não foi testado.
2. O conector do Make ligado no seu assistente, com as ferramentas que gravam. Para conferir, pergunte a ele:
   *"Liste as ferramentas do Make que você tem e diga se consegue criar, ativar e rodar um cenário."* Deu certo
   quando aparecem criar, ativar e rodar.

Sem o conector, as skills funcionam no papel: os documentos saem completos, com os itens da conta marcados
"a confirmar na conta", e a etapa 4 entrega o blueprint para você importar no Make.

## O que o método garante

Toda resposta diz em que etapa e em que passo você está, explica cada termo na primeira vez e termina com o próximo
comando pronto para colar.

Três coisas a skill nunca faz, nem com a sua confirmação:

- Usar segredo, chave ou endereço de webhook no fluxo, na amostra ou nos documentos: conexões são autorizadas por link,
  dentro do Make.
- Ligar o gatilho sem você responder "Ligar agora" — antes de gravar ou rodar, ela diz o que vai acontecer e quantas
  operações gasta.
- Apagar ou alterar o que esta conversa não criou, ou o que outro fluxo também usa: ela oferece criar um novo.

O seu arquivo real é bem-vindo: anexe o extrato, a nota, a folha ou o CSV da rotina. A skill lê o arquivo e o usa para
entender o layout e os casos de borda; os documentos que ela entrega guardam só a estrutura, com exemplo mascarado
(`***.123.456-**`); o teste roda na origem de teste, com o fluxo confidencial.

O resto a skill avisa e você decide: quando algo está fora do padrão (falta a chave que evita registro duplicado, o
teste não prova o que devia, o custo passa do plano), ela mostra o risco, recomenda e espera você escolher entre
"Corrigir agora" e "Seguir assim e registrar o alerta". O que você aceitou fica registrado no documento da etapa e na
ficha do fluxo.

O fluxo nasce confidencial (o Make não guarda os dados de cada passo no histórico): se o desenho vier sem isso, a
etapa 4 corrige sozinha e avisa.

O que a skill recomenda e só deixa de fazer com a sua escolha, registrada como alerta:

- O teste de aceite é uma execução de verdade, não uma validação de texto.
- O módulo oficial de cada app vem antes da chamada HTTP genérica.
- Quem retoma um fluxo confere na conta, antes de alterar, se nada mudou desde a ficha.

## Instalação

Baixe os zips da [última Release](../../releases/latest).

- **Claude (claude.ai):** Configurações → Capacidades → Skills → envie cada `.zip` **sem descompactar**.
- **ChatGPT:** Configurações → Habilidades → **+** → arraste o `.zip`. Sem acesso? Crie um Projeto, envie os arquivos
  e peça: *"Siga o SKILL.md que está nos arquivos deste projeto."*
- **Claude Code / Codex:** peça ao agente, dentro do projeto: *"Instale as skills do repositório
  robertodiasduarte/spec-make."*

Para começar: *"Use a skill spec-make-brainstorm. Quero automatizar: [a rotina em uma frase]."*

## Para quem mantém

```bash
python3 -I scripts/sync-compartilhados.py      # copia compartilhado/ para as skills
python3 -I -m unittest discover -s tests -t tests
bash scripts/publish-check.sh && python3 -I scripts/check-versions.py
bash scripts/package.sh                         # dist/*.zip + dist/SHA256SUMS.txt
```

Mudou o texto de uma regra (qualquer `.md` das skills ou de `compartilhado/`)? O teste `test_regras` reprova até você
revisar a mudança e rodar `python3 -I tests/regras.py --atualizar` no mesmo commit.

## Licença e autoria

MIT. Construído com a metodologia de Roberto Dias Duarte.
