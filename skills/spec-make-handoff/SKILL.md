---
name: spec-make-handoff
license: MIT
description: "Mantém a ficha de um fluxo do Make para continuar depois — um arquivo HANDOFF por fluxo, com o que existe na conta da pessoa (ids de cenário, webhook, data store e conexão, lidos pelo MCP do Make), o que a próxima conversa pode alterar, o que já foi testado e o que falta — e escreve o prompt para retomar numa conversa nova. Use quando a pessoa disser que vai parar, que vai continuar outro dia, que quer mudar um fluxo que já roda, ou ao fim da etapa 4 (spec-make-build). Só lê a conta: não cria, não altera, não roda e não apaga nada. Não redesenha o fluxo (spec-make-design) nem o cria (spec-make-build). Período de consulta e de cálculo: não se aplicam."
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: "1.1.0"
  updated: "2026-10"
  fase: "transversal"
---

# spec-make — Handoff: a ficha para continuar depois

Na primeira resposta desta skill, comece com estas duas linhas, uma vez só:
`spec-make-handoff v1.1.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/spec-make/releases/latest`
`spec-make · Handoff — para continuar depois`

## Quick start

1. Abra com as duas linhas de **[E1]** e diga: "Vou ler a sua conta pelo Make — só leitura, não gasta operação e não
   muda nada — e atualizar a ficha."
2. Ache a ficha do fluxo: `HANDOFF_<FLUXO>.md` anexado ou colado. Existe: atualize. Não existe: ela nasce agora
   (**[H3]**).
3. Leia a conta na ordem **[H1]** ([references/PROTOCOLO.md](references/PROTOCOLO.md)). Sem o conector, siga **[M1]**.
4. Preencha a ficha com [assets/HANDOFF_TEMPLATE.md](assets/HANDOFF_TEMPLATE.md) (exemplo pronto em
   [assets/HANDOFF_EXEMPLO.md](assets/HANDOFF_EXEMPLO.md)), sem segredo (**[H2]**).
5. Escreva o prompt de retomada (**[H3]**).
6. Confira a ficha (**[H4]**) com [scripts/checar_handoff.py](scripts/checar_handoff.py).
7. Entregue a ficha e o prompt e feche com **[E1]**.

## Quando usar / Quando não usar

Usar quando a conversa vai parar no meio de qualquer etapa, quando a pessoa quer continuar outro dia ou em outro
assistente, quando quer mudar um fluxo que já roda na conta, e ao fim da etapa 4 (a skill `spec-make-build` entrega a
primeira ficha). Serve também para um fluxo criado direto no Make, sem o spec-make: a primeira ficha nasce a partir dos
cenários que a pessoa confirmar.

Não usar para mudar o fluxo: esta skill só lê a conta e escreve a ficha. A mudança é feita pela etapa 3
(`spec-make-design`, quando o desenho muda) ou pela etapa 4 (`spec-make-build`), com a ficha anexada.

## Dados necessários

- O `HANDOFF_<FLUXO>.md` anterior, se existir.
- Os documentos do fluxo que existirem: BRAINSTORM, DEFINE, DESIGN, FICHA_DO_FLUXO e o recibo do teste.
- Sem ficha anterior: os cenários que fazem parte do fluxo, pelo número (aparece no endereço do cenário no Make) ou
  pelo nome exato.
- O conector do Make ligado na conversa (sem ele, **[M1]**).

## Procedimento passo a passo

1. **Abertura.** As duas linhas de [E1] e a frase do Quick start. Termos explicados uma vez, na primeira vez que
   aparecem: fluxo (ou família) é o que a pessoa chama de "o fluxo de boletos"; parte é cada cenário dele no Make; a
   custódia diz o que a próxima conversa pode alterar.
2. **Uma ficha por fluxo.** Procure a ficha anterior pelo nome do fluxo antes de criar arquivo ([H3]).
3. **Leitura [H1].** Siga [references/PROTOCOLO.md](references/PROTOCOLO.md): `environment_get`, as partes, cada parte,
   webhooks, data stores e conexões — e a custódia de cada recurso.
4. **Ficha.** O estado do fluxo inteiro no topo; o inventário com 1 linha por recurso; "Feito" com o que prova cada
   item (id de execução, arquivo); "Falta" em ordem; "Alertas (não tocar)" com os recursos compartilhados e fora do
   spec-make, pelo id. Sessões antigas encerradas viram 1 linha quando a ficha passar de uns 10 KB.
5. **Prompt de retomada [H3].**
6. **Conferência [H4].**
7. **Fecho [E1].**

**[H2] Só leitura, sem segredo.** Esta skill só lê a conta. Nunca chame `scenarios_create`, `scenarios_update`,
`scenarios_activate`, `scenarios_deactivate`, `scenarios_delete`, `scenarios_run`, `hooks_create`, `hooks_update`,
`hooks_delete`, `data-stores_create`, `data-stores_update`, `data-stores_delete` nem `data-store-records_list` — o
registro de um data store pode guardar senha ou chave. Na ficha, do webhook, guarde só o id e o nome (o endereço dele
carrega o código de acesso; a próxima conversa relê com `hooks_get`); do data store, só o id, o nome e o número de
registros. Nada de e-mail, CNPJ, CPF, chave ou senha na ficha. Mudanças no fluxo não acontecem aqui: quem altera é a
etapa 3 ou 4, sob a custódia da ficha (regra [B6] da skill `spec-make-build`).

**[H3] Uma ficha por fluxo e o prompt de retomada.** O fluxo inteiro, com todas as partes, tem uma ficha só:
`HANDOFF_<FLUXO>.md`. Cada sessão nova entra como subseção no topo do "Histórico de sessões"; nunca crie um arquivo novo
para a mesma família (nada de `HANDOFF_<FLUXO>_2.md`). Mudança de escopo ou pausa vira linha nova, sem apagar o que
estava escrito. O prompt de retomada é um bloco para colar numa conversa nova e funciona sozinho, nesta ordem: qual
skill abrir ("Use a skill spec-make-design." quando o desenho muda; "Use a skill spec-make-build." quando só
implementa; a etapa em que a conversa parou, se parou no meio), quais arquivos anexar (pelo nome exato), onde paramos
(2 ou 3 linhas), último teste (execução, data, resultado), próxima ação (1 ação, com o id do recurso) e o que não tocar
(pelo id). Entregue o bloco sem nenhum trecho entre « » nem entre chaves: o que não tem valor concreto você busca agora
ou apaga.

**[H4] Conferência da ficha.** Antes de entregar, rode `python3 scripts/checar_handoff.py HANDOFF_<FLUXO>.md` se o
ambiente executar código; ele sai 0 quando está tudo certo. Sem Python, confira à mão os mesmos itens: as quatro seções
obrigatórias (Ficha, Inventário e custódia, Prompt de retomada, Histórico de sessões) com o título exato; nenhum
trecho de modelo sobrando; nenhuma URL de webhook; nenhuma sequência de 11 ou mais dígitos (o id de execução e o
resumo do blueprint vão em grupos de 8 separados por hífen); nenhum recurso sem id no inventário. Não entregue ficha
com problema.

**[M1] Sem o conector do Make.** Se a conversa não tiver o MCP do Make, avise em uma frase, escreva "sem o conector" na
linha "Gerada" da ficha e preencha o inventário com os ids que a pessoa ou os documentos trouxerem, marcando como
"a confirmar na conta" em cada estado. Não afirme `lastEdit`, custódia nem contagem de registros sem ter lido a conta.

**[E1] Para continuar depois.** A primeira resposta traz a linha "spec-make · Handoff — para continuar depois". O
fecho entrega o arquivo `HANDOFF_<FLUXO>.md`, pede para salvá-lo junto dos outros documentos do fluxo e mostra o
prompt de retomada pronto para colar — ele começa por "Use a skill spec-make-" e o nome da etapa — com a frase: "Para
continuar, abra uma conversa nova, anexe os arquivos e cole este bloco."

## Validações e checklist de qualidade

- [ ] Ficha anterior procurada antes de criar arquivo ([H3])
- [ ] Leitura na ordem [H1], só com ferramentas de leitura ([H2])
- [ ] Sem ficha anterior: cenários confirmados pela pessoa antes de qualquer custódia
- [ ] Custódia em um dos três textos, por recurso; compartilhado com N = total de cenários que usam o recurso
- [ ] `lastEdit` de cada cenário copiado da conta
- [ ] Nenhuma URL de webhook, registro de data store, e-mail, CNPJ, CPF, chave ou senha na ficha
- [ ] Prompt de retomada na ordem [H3], sem trecho de modelo
- [ ] Ficha conferida ([H4]) antes de entregar
- [ ] Sem o conector: "a confirmar na conta" em cada estado ([M1])

## Tratamento de exceções

- **A pessoa pede para mudar ou apagar algo no fluxo:** diga que esta skill só lê e escreve a ficha; entregue a ficha
  e o prompt de retomada para a etapa 3 ou 4 fazer a mudança.
- **A conta mudou depois da ficha anterior** (`lastEdit` diferente): registre os dois horários na sessão desta conversa
  e atualize a ficha com o que está na conta agora.
- **Um cenário da ficha sumiu da conta:** marque a linha como "não encontrado na conta em AAAA-MM-DD" e diga isso à
  pessoa; não invente substituto.
- **Um data store da família passou a ser usado por outro fluxo:** a custódia dele vira
  `compartilhado com N cenários — só ler e acrescentar`, e a sessão desta conversa registra a mudança.
- **O conector caiu no meio da leitura:** grave o que foi lido e marque o resto como "a confirmar na conta".
- **A pessoa deu só o nome de um cenário e há mais de um com esse nome:** mostre os candidatos (nome e número) e
  pergunte qual; não escolha sozinho.

## Examples

**Caso positivo (sintético, ids inventados).** "Vou parar por hoje; amanhã quero testar a recusa do fluxo de boletos."
Não há ficha anterior. A skill pergunta quais cenários fazem parte; a pessoa responde 6600101 e 6600102. A skill lê a
conta ([H1]), marca as duas partes, o webhook 2900101 e o data store 170101 como `desta família`, o data store 170102
como `compartilhado com 4 cenários — só ler e acrescentar` e as duas conexões como `fora do spec-make`; confere a ficha
([H4]) e entrega `HANDOFF_BOLETOS.md` com o prompt "Use a skill spec-make-build. Anexe HANDOFF_BOLETOS.md e
DESIGN_BOLETOS.md. …" — como em [assets/HANDOFF_EXEMPLO.md](assets/HANDOFF_EXEMPLO.md).

**Contraexemplo.** "Aproveita e apaga o data store 170102, que eu não uso mais." A skill não apaga ([H2]): diz que só lê
a conta, que 170102 é usado por outros fluxos e que a mudança é com a etapa 4, que vai perguntar antes de gravar.

## Inventário do bundle

- `SKILL.md`
- `references/PROTOCOLO.md` — a leitura [H1] e a custódia, passo a passo
- `references/MCP_MAKE.md` · `references/COPY.md` · `references/RUNTIME_COMPATIBILITY.md`
- `assets/HANDOFF_TEMPLATE.md` · `assets/HANDOFF_EXEMPLO.md`
- `scripts/checar_handoff.py` — confere a ficha (Python 3.9+, sem dependências)
- `manifest.json` · `evals/cases.json`

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
