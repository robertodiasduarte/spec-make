# spec-make

Método em quatro etapas para criar fluxos no **Make** conversando com a IA, com o **MCP do Make** conectado no
Claude ou no ChatGPT. Cada etapa é uma skill e entrega um documento; a última cria o fluxo na sua conta, testa com a
sua amostra e só liga o gatilho quando você disser sim.

| Etapa | Skill | Você sai com |
|---|---|---|
| 1 | `spec-make-brainstorm` | A ideia do fluxo, conferida na sua conta: apps nativos, conexões, plano |
| 2 | `spec-make-define` | O que o fluxo tem de fazer e o teste de aceite (amostra + resultado esperado) |
| 3 | `spec-make-design` | O fluxo módulo a módulo, o que fazer quando cada app falha e o blueprint validado |
| 4 | `spec-make-build` | O fluxo criado e testado na sua conta, o recibo do teste e a ficha do fluxo |

Fluxo com agente de IA dentro (OpenAI, Claude, Gemini)? Instale também a
[`sdd-prompt-builder`](https://github.com/robertodiasduarte/sdd-starter/releases/latest/download/sdd-prompt-builder.zip),
que escreve os prompts a partir do contrato que a etapa 3 registra.

## Antes de começar

1. Uma conta no Make. Testado no plano Core; o plano Free não foi testado.
2. O conector do Make ligado no seu assistente, com as ferramentas que gravam. Para conferir, pergunte a ele:
   *"Liste as ferramentas do Make que você tem e diga se consegue criar, ativar e rodar um cenário."* Deu certo
   quando aparecem criar, ativar e rodar.

Sem o conector, as skills funcionam no papel: os documentos saem completos, com os itens da conta marcados
"a confirmar na conta", e a etapa 4 entrega o blueprint para você importar no Make.

## O que o método garante

- Nada é ligado na sua conta sem o seu "sim"; antes de gravar ou rodar, a skill diz o que vai acontecer e quantas
  operações gasta.
- O teste de aceite é uma execução de verdade, não uma validação de texto.
- O fluxo nasce confidencial: o Make não guarda os dados de cada passo no histórico.
- Fluxo que grava não duplica registro (chave natural); IA que decide não grava sem aceite de uma pessoa, e cada
  aceite fica registrado.
- Nenhuma chave ou senha passa pelo chat: conexões são autorizadas por link, dentro do Make.

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
