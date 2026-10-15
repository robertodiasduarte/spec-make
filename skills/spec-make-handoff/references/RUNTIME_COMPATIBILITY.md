# Compatibilidade

Este arquivo é igual em todas as skills do spec-make.

## O que a skill precisa do ambiente

| Capacidade | Para quê | Sem ela |
|---|---|---|
| Ler e seguir instruções em Markdown | Tudo | A skill não funciona |
| MCP do Make conectado | Ler a conta, validar, criar e rodar o fluxo | Trabalho no papel (regra [M1]): documentos completos, itens da conta marcados "a confirmar na conta"; a etapa de build entrega o blueprint e os passos de importação manual |
| MCP do Make com ferramentas de gravação | Etapa de build | Igual à linha acima, só na etapa de build |
| Execução de Python 3.9+ | `scripts/checar_blueprint.py` (etapas de design e build) e `scripts/checar_handoff.py` (skill de handoff) | A skill faz a mesma conferência lendo o blueprint ou a ficha, item a item |
| Anexar e devolver arquivos | Passar o documento de uma etapa para a próxima | O agente mostra o documento inteiro; a pessoa copia e cola na próxima conversa |

## Onde instalar

O pacote segue o formato aberto Agent Skills (pasta com `SKILL.md`). A instalação varia por
aplicativo e plano; consulte a documentação atual do seu aplicativo. Se ele não aceitar skills,
crie um Projeto, envie os arquivos da pasta e peça: "Siga o SKILL.md que está nos arquivos deste
projeto."

## O que foi testado

- Claude (claude.ai) com o conector oficial do Make, plano Core do Make: sequência completa do
  build medida em 13/10/2026.
- ChatGPT com o conector do Make: não medido. Funciona se o conector expor as mesmas ferramentas
  de gravação; confira com a pergunta de teste da página do spec-make.
- Plano Free do Make: não medido.

Comportamento idêntico entre modelos não é garantido; o texto da skill é o mesmo.
