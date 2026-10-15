# Protocolo do handoff — ler a conta e montar a ficha

## Abertura

As duas linhas da regra [E1]. Depois: "Vou ler a sua conta pelo Make — só leitura, não gasta operação e não muda
nada — e atualizar a ficha."

**[H1] Leitura da conta e custódia.** Leia nesta ordem, só com ferramentas de leitura:

1. `environment_get` — organização, equipe e zona. Anote `organizationId` e `teamId` na ficha.
2. As partes do fluxo. Com ficha anterior da família, as partes são os cenários que o inventário dela marca como
   `desta família`. Sem ficha anterior, pergunte quais cenários fazem parte do fluxo antes de escrever qualquer
   custódia: "Quais cenários do Make fazem parte deste fluxo? O número aparece no endereço do cenário
   (…/scenarios/número); o nome também serve." Use `scenarios_list` só quando a pessoa der o nome sem o id: procure o
   nome exato e confirme com ela o cenário achado.
   Cenário que a pessoa não confirmou nunca entra como `desta família`.
3. `scenarios_get` de cada parte — o nome como está na conta, se está ativo, o agendamento (`scheduling.type`), o
   `lastEdit`, o `hookId` e os ids de data store e de conexão que os módulos usam (`datastore`, `__IMTCONN__`).
4. `hooks_list` — para cada webhook das partes, o `scenarioId` a que ele está ligado. Guarde só o id e o nome.
5. `data-stores_list` — para cada data store das partes, o número de registros (`records`) e a lista
   `scenarioUsages` (quais cenários o usam).
6. `connections_list` — nome, app e data em que expira, de cada conexão das partes.

Com o que leu, escreva a custódia de cada recurso, em um destes três textos:

- `desta família` — cenário confirmado como parte; data store em que todo `scenarioUsages` é parte da família;
  webhook ligado a uma parte.
- `compartilhado com N cenários — só ler e acrescentar` — data store usado também fora da família; N é o total de
  cenários em `scenarioUsages`.
- `fora do spec-make` — toda conexão (ela se reautoriza no Make), webhook ligado a outro cenário e todo cenário que a
  pessoa não confirmou.

Copie o `lastEdit` de cada cenário para a ficha: é por ele que a próxima conversa descobre se alguém mexeu no fluxo
depois.

## Sem o conector do Make

Regra [M1] da skill: avise em uma frase, escreva "sem o conector" na linha "Gerada" da ficha e use "a confirmar na
conta" no id que ninguém trouxe e em cada estado e custódia. Os ids que a pessoa ou os documentos trouxerem entram
como vieram.

## Montar a ficha

Use [assets/HANDOFF_TEMPLATE.md](../assets/HANDOFF_TEMPLATE.md). Regras de forma:

- **Ficha** no topo, com o estado do fluxo inteiro: está na conta? gatilho ligado? quantas partes? último teste.
- **Inventário e custódia**: 1 linha por recurso, id na 2ª coluna. O título da seção é exato; a data da leitura vai
  na linha de baixo.
- **Feito**: cada item com o que prova (id de execução, arquivo). **Falta**: em ordem, cada item começando por verbo.
- **Alertas (não tocar)**: os recursos `compartilhado` e `fora do spec-make`, pelo id.
- **Histórico de sessões**: a sessão desta conversa no topo, em 3 a 6 linhas. Sessões antigas encerradas viram 1
  linha cada quando a ficha passar de uns 10 KB.
- Datas por extenso no formato AAAA-MM-DD. O id de execução e o resumo (sha256) do blueprint vão em grupos de 8
  caracteres separados por hífen.

## Quando a conta mudou depois da ficha

A ficha anterior traz um `lastEdit` e a conta outro: alguém mexeu no fluxo direto no Make. Diga isso à pessoa em
três partes — o que aconteceu ("o cenário X foi editado no Make em AAAA-MM-DD, depois da ficha de AAAA-MM-DD"), o que
você já fez ("não alterei nada; só li a conta") e o que ela faz agora: "A versão que está na conta passa a ser a base
do fluxo?", com as opções "Sim, usar a da conta" e "Não, conferir antes". Nunca troque o `lastEdit` da ficha pelo da
conta sem o "sim" da pessoa.

- **Sem o "sim":** a ficha mantém o `lastEdit` antigo, a linha do cenário ganha "editado no Make depois da ficha em
  AAAA-MM-DD" e o aviso entra em "Alertas (não tocar)". É esse descompasso que faz a etapa 4 parar e perguntar antes
  de gravar (regra [B6] da skill `spec-make-build`).
- **Com o "sim":** a ficha passa a ter o `lastEdit` da conta, a linha "Blueprint publicado" ganha "desatualizado:
  exporte de novo do Make" e a sessão desta conversa registra a decisão e a data.
