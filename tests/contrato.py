"""Contrato das skills por âncoras de regra (Decision 2 do DESIGN da plataforma).

Cada regra vive num bloco que começa em `**[XN]` e vai até a próxima âncora `**[` ou o próximo título. A asserção
olha só dentro do bloco: tokens que precisam aparecer (todos) e tokens que precisam aparecer NESTA ORDEM — tanto em
sequência quanto pela primeira menção de cada um (nenhum token citado antes do anterior).
test_contrato.py roda cada regra contra o texto real e contra um mutante, que tem de reprovar.

Regra com polaridade (nunca, não, recuse, pare) exige a FRASE inteira, com a palavra que vem antes: "Sem a chave, recuse o
DESIGN" e não só "recuse o", senão "Sem a chave, não recuse o DESIGN" passa (achado 2 do avaliador, ciclo 3). A comparação
ignora quebra de linha e espaço repetido.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


@dataclass
class Regra:
    ancora: str            # ex.: "B1"
    arquivo: str           # relativo a skills/
    contem: list[str] = field(default_factory=list)
    em_ordem: list[str] = field(default_factory=list)
    at: str = ""


def _skill(nome: str, arq: str = "SKILL.md") -> str:
    return f"{nome}/{arq}"


ETAPAS = [("spec-make-brainstorm", 1, "Brainstorm", "Use a skill spec-make-define."),
          ("spec-make-define", 2, "Define", "Use a skill spec-make-design."),
          ("spec-make-design", 3, "Design", "Use a skill spec-make-build."),
          ("spec-make-build", 4, "Build", "Pronto: o fluxo está na sua conta.")]

# SPEC_MAKE_SUPABASE (AT-001): a condição com que toda âncora [S*] do design começa
COND = "Se o fluxo toca Supabase"

REGRAS: list[Regra] = [
    Regra("B1", _skill("spec-make-build", "references/PROTOCOLO.md"), at="AT-002",
          contem=['"on-demand"', "confidential: true", "credential-requests_create",
                  "esperar a pessoa autorizar e conferir de novo. Nunca peça chave no chat.",
                  # SPEC_MAKE_S5: o banco preparado vem antes das validações; o webhook não existe mais no kit
                  "Fluxo que toca Supabase: confirme com a pessoa que o SQL do `Prepare o banco` rodou sem erro no SQL "
                  "Editor; o teste do passo 10 prova o resto.",
                  "(operações maiores que zero; ela pode gastar menos que a 1ª)"],
          em_ordem=["environment_get", "credential-requests_create", "validate_module_configuration",
                    "validate_blueprint_schema", "scenarios_create", "scenarios_set-interface",
                    "scenarios_activate", "scenarios_run", "executions_get-detail"]),
    Regra("B2", _skill("spec-make-build"), at="AT-003",
          contem=["Ligar agora", "Deixar só sob demanda", "aguardando OK para ligar o gatilho",
                  "scenarios_update", "on-demand",
                  'Só troque o agendamento (`scenarios_update` com `scheduling` diferente de `on-demand`) ou ligue o '
                  'gatilho real depois de a pessoa responder "Ligar agora" ou "sim".',
                  # a consequência da falta do "sim", inteira (M8 do avaliador, ciclo 2: trocá-la passava)
                  "Qualquer outra resposta, ou nenhuma, mantém o fluxo sob demanda, sem agenda nem webhook ligados"]),
    Regra("B3", _skill("spec-make-build", "references/DIAGNOSTICO.md"), at="AT-004",
          contem=["o que aconteceu", "o que eu já fiz", "o que você faz agora", "operações",
                  "**Teto: 3 tentativas** de correção para o mesmo teste: o teste roda no máximo 4 vezes",
                  "ainda falhar, pare: não corrija nem rode de novo, deixe o fluxo sob demanda"],
          em_ordem=["**interface**", "**módulo**", "**conexão**", "**mapeamento**"]),
    Regra("B4", _skill("spec-make-build"), at="AT-004",
          contem=["Só o que você criou.** Nunca chame `scenarios_update`, `scenarios_delete`",
                  "ou qualquer alteração em fluxo, data store ou conexão que esta conversa não criou."]),
    Regra("B5", _skill("spec-make-build"), at="UX MUST 5",
          contem=["Antes de criar qualquer coisa na conta", "antes de cada execução", "operações"]),
    Regra("C1", _skill("spec-make-build"), at="AT-005",
          contem=["O fluxo é criado com `metadata.scenario.confidential: true`. Se"]),
    Regra("C1", _skill("spec-make-design"), at="AT-005",
          contem=["Todo blueprint sai com `metadata.scenario.confidential: true`. O"]),
    Regra("P1", _skill("spec-make-design"), at="AT-007",
          contem=["inventário de prompts", "sdd-prompt-builder",
                  "Fluxo com módulo de IA e sem esse inventário: recuse o DESIGN como pronto e diga o que falta."]),
    # SPEC_MAKE_HANDOFF (s3): custódia pela ficha na build — lastEdit e usos relidos ANTES de gravar (A2 da review do DESIGN)
    # avaliador fresco do s3, ciclo 1: a conferência do lastEdit e a regra do compartilhado, com a polaridade inteira
    # ("se for diferente, diga … e siga só depois do sim"; "compartilhado: só ler … — nunca chame") — trechos soltos
    # passavam com a regra invertida
    Regra("B6", _skill("spec-make-build"), at="AT-003",
          contem=["contam como criados por esta conversa para [B4] — e só eles",
                  "editado no Make depois da ficha", 'siga só depois do "sim" da pessoa',
                  "Primeiro leia `scenarios_get` de cada parte e compare o `lastEdit` com o da ficha: se for diferente, "
                  'diga em 1 frase os dois horários ("editado no Make depois da ficha") e siga só depois do "sim" da '
                  "pessoa.",
                  "releia `data-stores_list` e `hooks_list` e recalcule a custódia",
                  "Só então chame `scenarios_update`, `scenarios_set-interface`, `data-stores_update` ou `hooks_update`, "
                  "com o aviso [B5].",
                  "nunca chame `data-stores_delete`, `data-stores_update` de estrutura nem `hooks_delete` sobre ele",
                  "Recurso `compartilhado com N cenários`: só ler e acrescentar registro — nunca chame "
                  "`data-stores_delete`, `data-stores_update` de estrutura nem `hooks_delete` sobre ele;",
                  # avaliador fresco do s3, ciclo 2 (B6e/B6e2/B6h, B6f): a consequência do uso novo fora da família e o
                  # [B4] do recurso fora da ficha, inteiros — "recalcule a custódia" solto passava com "continua `desta
                  # família`, sem avisar a pessoa" e com "fora do spec-make: altere também"
                  "Depois releia `data-stores_list` e `hooks_list` e recalcule a custódia pelos `scenarioUsages` e "
                  "`scenarioId` de agora: recurso que ganhou uso fora da família passa a `compartilhado com N cenários`, "
                  "e você diz isso à pessoa.",
                  "Recurso ausente da ficha ou `fora do spec-make`: [B4] como sempre."],
          em_ordem=["lastEdit", "scenarioUsages", "scenarios_update"]),
    # avaliador fresco do s3, ciclo 2 (E1i, E1h): o fecho NORMAL inteiro, do "dois arquivos" ao "como continuar depois" —
    # "Pronto: o fluxo está na sua conta." solto é achado no texto de reserva ("Sem a skill de handoff instalada…")
    Regra("E1", _skill("spec-make-build"), at="AT-006",
          contem=["`HANDOFF_<FLUXO>.md`", "o handoff, como continuar depois",
                  "O fecho entrega o recibo e dois arquivos, `FICHA_DO_FLUXO_<FLUXO>.md` e `HANDOFF_<FLUXO>.md`, pede para "
                  'salvar os dois e diz: "Pronto: o fluxo está na sua conta. A ficha diz o que fazer quando ele falhar; o '
                  'handoff, como continuar depois."']),
    # skill de handoff: fora de ETAPAS (não é etapa — a 1ª linha não diz "Etapa N de 4")
    # avaliador fresco do s3, ciclo 1: as 3 classes de custódia, a pergunta da 1ª ficha e o `scenarios_list` com a
    # linha inteira — "compartilhado com N cenários" solto passava com a classe redefinida como `desta família`
    Regra("H1", _skill("spec-make-handoff", "references/PROTOCOLO.md"), at="AT-002",
          contem=["desta família", "compartilhado com N cenários", "fora do spec-make", "scenarioUsages", "lastEdit",
                  "Sem ficha anterior, pergunte quais cenários fazem parte do fluxo antes de escrever qualquer custódia",
                  "Use `scenarios_list` só quando a pessoa der o nome sem o id: procure o nome exato e confirme com ela o "
                  "cenário achado.",
                  "Cenário que a pessoa não confirmou nunca entra como `desta família`.",
                  "- `desta família` — cenário confirmado como parte; data store em que todo `scenarioUsages` é parte da "
                  "família; webhook ligado a uma parte.",
                  "- `compartilhado com N cenários — só ler e acrescentar` — data store usado também fora da família; N é "
                  "o total de cenários em `scenarioUsages`.",
                  "- `fora do spec-make` — toda conexão (ela se reautoriza no Make), webhook ligado a outro cenário e todo "
                  "cenário que a pessoa não confirmou."],
          em_ordem=["environment_get", "scenarios_get", "hooks_list", "data-stores_list", "connections_list"]),
    # avaliador fresco do s3, ciclo 1: a lista do "Nunca chame" até o `data-store-records_list` e o motivo, numa frase só,
    # e o que a ficha guarda do webhook com o parêntese que vem depois — trechos soltos passavam com "Leia
    # `data-store-records_list`" e com "e também a URL completa"
    Regra("H2", _skill("spec-make-handoff"), at="AT-005",
          contem=["Nunca chame `scenarios_create`, `scenarios_update`", "`data-store-records_list`",
                  "Esta skill só lê a conta. Nunca chame `scenarios_create`, `scenarios_update`, `scenarios_activate`, "
                  "`scenarios_deactivate`, `scenarios_delete`, `scenarios_run`, `hooks_create`, `hooks_update`, "
                  "`hooks_delete`, `data-stores_create`, `data-stores_update`, `data-stores_delete` nem "
                  "`data-store-records_list` — o registro de um data store pode guardar senha ou chave.",
                  "do webhook, guarde só o id e o nome",
                  "Na ficha, do webhook, guarde só o id e o nome (o endereço dele carrega o código de acesso; a próxima "
                  "conversa relê com `hooks_get`); do data store, só o id, o nome e o número de registros.",
                  "quem altera é a etapa 3 ou 4, sob a custódia da ficha"]),
    Regra("H3", _skill("spec-make-handoff"), at="AT-006",
          contem=["nunca crie um arquivo novo para a mesma família", "Use a skill spec-make-", "sem nenhum trecho entre « »",
                  # avaliador fresco do s3, ciclo 2 (H3d): design e build trocados no mapeamento passavam
                  'qual skill abrir ("Use a skill spec-make-design." quando o desenho muda; "Use a skill '
                  'spec-make-build." quando só implementa; a etapa em que a conversa parou, se parou no meio)'],
          em_ordem=["qual skill abrir", "quais arquivos anexar", "onde paramos", "último teste", "próxima ação"]),
    Regra("H4", _skill("spec-make-handoff"), at="AT-004",
          contem=["checar_handoff.py", "URL de webhook", "11 ou mais dígitos", "sem id"]),
    Regra("E1", _skill("spec-make-handoff"), at="AT-007",
          contem=["spec-make · Handoff — para continuar depois", "Use a skill spec-make-"]),
    Regra("P1", _skill("spec-make-build"), at="AT-007",
          contem=["sem inventário", "[G1]", "[G2]",
                  "sem inventário de prompts no DESIGN: pare antes do `scenarios_create`, diga o que falta"]),
    Regra("G1", _skill("spec-make-design"), at="AT-007",
          contem=["pessoa identificada antes da gravação",
                  "Sem esse passo, recuse o DESIGN como pronto e diga o que falta."]),
    Regra("G2", _skill("spec-make-design"), at="AT-007",
          contem=["fora do histórico", "planilha ou data store",
                  # SPEC_MAKE_SUPABASE AT-006: com Supabase, a auditoria só de acréscimo é a 1ª opção
                  "quando o fluxo já usa Supabase, a 1ª opção é uma tabela de auditoria só de acréscimo", "modelo", "versão do prompt", "sugestão original", "quem aceitou",
                  "(UTC)", "se editou", "Sem esse registro, recuse o DESIGN como pronto."]),
    Regra("G3", _skill("spec-make-design"), at="AT-011",
          contem=["chave natural", "já existe ⇒ não grava de novo",
                  "consultar antes de gravar, ou gravar substituindo pela chave",
                  "Quando o destino é uma tabela do Supabase, a chave existe nela como restrição ([S5]).",
                  "Sem a chave, recuse o DESIGN como pronto e peça a chave."]),
    # SPEC_MAKE_S5: toda âncora S* começa pela condição e prende a recusa INTEIRA, com a palavra de polaridade que vem
    # antes (R2@opus da review do DESIGN: "e a pessoa não faz … mais que", "que não é", "sem o gatilho ou sem a view"
    # passavam quando só o final da frase era prendido)
    Regra("S1", _skill("spec-make-design"), at="AT-002",
          contem=[COND, "o diálogo padrão do app no Make",
                  '`alcance` com o motivo ("o app Supabase do Make só conecta com chave secreta; ela ignora o RLS"), as '
                  "tabelas e as operações.",
                  "Se o fluxo toca Supabase (app `supabase`, `supabase-management`, `postgres` ou HTTP para o endereço de "
                  "um projeto Supabase, em qualquer caminho), a conexão Supabase usa o diálogo padrão do app no Make "
                  "(Project ID e chave secreta, copiados do painel do Supabase) e o DESIGN preenche a coluna `alcance` "
                  "com o motivo (\"o app Supabase do Make só conecta com chave secreta; ela ignora o RLS\"), as tabelas "
                  "e as operações.",
                  "`postgres` (conexão direta) e `supabase-management` nunca entram no fluxo.",
                  "Sem isso, recuse o DESIGN como pronto e diga o que falta."]),
    Regra("S2", _skill("spec-make-design"), at="AT-002",
          contem=[COND, "do app `supabase` entram só `searchRows`, `createARow`, `upsertARecord`, `getRowsCount` e "
                  "`deleteRows`",
                  "e a pessoa não faz, antes do 1º fluxo rodar, mais que 1 colagem de SQL, copiar o Project ID e a chave "
                  "do painel e criar 1 conexão no Make.",
                  "Edge function, webhook de qualquer tipo, Database Webhook, `pg_cron`, `supabase:watchEvents`, "
                  "`supabase:makeAnApiCall` e módulo HTTP para o endereço de um projeto Supabase ficam fora: recuse o "
                  "DESIGN como pronto e proponha o caminho só com o banco."]),
    Regra("S3", _skill("spec-make-design"), at="AT-004",
          contem=[COND, "`processado` igual a `false`", "regrava a linha inteira",
                  "Se o fluxo toca Supabase e lê uma fila, o DESIGN desenha o laço agenda do Make → `searchRows` com "
                  "`processado` igual a `false` e um limite → processa → `upsertARecord` pela primary key da fila, que "
                  "regrava a linha inteira (as colunas lidas mais `processado = true` e `processado_em`).",
                  # 1.3.1 (teste de ponta a ponta de 16/10/2026): valor em texto e filtro "existe" depois da busca
                  "No blueprint, o valor do filtro de verdade/falso vai em texto (`\"false\"`, nunca o booleano `false`: "
                  "o Make ignora a condição e a busca lê qualquer linha).",
                  "Sem pendente, a busca devolve 1 pacote vazio: o módulo seguinte leva o filtro \"`{{id da busca.<coluna>}}` "
                  "existe\", senão ele roda com campos vazios e falha.",
                  "Filtro por coluna vazia, ou gatilho que não seja a agenda do Make nem a execução sob demanda: recuse o "
                  "DESIGN como pronto."]),
    Regra("S4", _skill("spec-make-design"), at="AT-004",
          contem=[COND, "agenda do Make com o intervalo, ou sob demanda", "disparos por mês × operações do disparo vazio",
                  "Se o fluxo toca Supabase, o DESIGN declara no bloco `Relógio` como o fluxo dispara — agenda do Make "
                  "com o intervalo, ou sob demanda — e, com agenda, soma no custo as operações paradas: disparos por mês "
                  "× operações do disparo vazio.",
                  "Se o total passar do orçamento do DEFINE, recuse o DESIGN como pronto e ofereça um intervalo maior."]),
    Regra("S5", _skill("spec-make-design"), at="AT-005",
          contem=[COND, "a chave natural como `primary key` da tabela de destino que o `upsertARecord` grava (a fila, que "
                  "aceita a chave repetida, tem o `id` como `primary key` e o marcador a grava por ele)",
                  "`numeric(18,2)`", "os 6 campos de [G2] `not null`", "a view da taxa de correção",
                  # 1.3.3 (avaliador, ciclo 2): a pessoa lê a view no SQL Editor
                  "O DESIGN diz que a pessoa lê a view da taxa de correção no SQL Editor do Supabase "
                  "(`select * from public.<auditoria>_taxa_de_correcao`).",
                  'Os 6 campos vêm do passo de aceite, gravados antes do "processa" e nunca recalculados, para a repetição '
                  "do mesmo aceite ser idêntica.",
                  "Chave natural que não é a `primary key` da tabela de destino do `upsertARecord`, coluna de valor em "
                  "`real`, `float4`, `float8` ou `double precision`, rateio sem a regra do centavo residual, campo da "
                  "auditoria anulável, auditoria sem o gatilho ou sem a view: recuse o DESIGN como pronto e nomeie a "
                  "coluna, o campo ou o rateio que falta corrigir."]),
    Regra("W1", _skill("spec-make-design"), at="AT-007",
          contem=["uma vez", "a URL, a data, o módulo e a versão", "vale a conta",
                  "Para cada app do fluxo, consulte a documentação pública do Make (`https://apps.make.com/<app>`) uma "
                  "vez e anote em `Fontes consultadas` a URL, a data, o módulo e a versão.",
                  "Se ela divergir de `app-modules_list`, vale a conta, e o DESIGN anota a divergência.",
                  'Sem acesso à web, escreva "não consultado"; nunca afirme uma consulta que não fez.']),
    Regra("B7", _skill("spec-make-build"), at="AT-008",
          contem=["Se o DESIGN toca Supabase", "coluna `alcance` preenchida com o motivo, as tabelas e as operações",
                  "seção `Prepare o banco` com o SQL quando o fluxo grava no banco",
                  "do app `supabase` só `searchRows`, `createARow`, `upsertARecord`, `getRowsCount` e `deleteRows`",
                  "nenhum módulo `postgres` ou `supabase-management`, nenhum HTTP para o projeto",
                  "gatilho só pela agenda do Make ou sob demanda; bloco `Relógio` com o gatilho e, quando é agenda, o "
                  "intervalo e a linha de operações paradas na seção `Custo`.",
                  'Faltando qualquer um, não crie o fluxo: diga o que falta e indique "Use a skill spec-make-design." '
                  "antes de qualquer `scenarios_create`.",
                  # 1.3.3 (avaliador, ciclo 2): o verificador do blueprint manda parar o build
                  "Rode também `scripts/checar_blueprint.py` sobre o blueprint do DESIGN: se ele reprovar, não crie o "
                  "fluxo; diga o problema e indique a mesma skill."]),
    Regra("D1", _skill("spec-make-define"), at="AT-008",
          contem=["sem dado pessoal real", "resultado esperado", "segunda execução da mesma", "mesma contagem",
                  "no destino. Recuse como incompleto o teste que só confere uma execução",
                  ', e recuse "blueprint validado" como teste de aceite']),
]
# [M1] com a polaridade inteira em cada etapa (R3@opus, rodada 6)
M1 = {"spec-make-brainstorm": ['como "a confirmar na conta". Não afirme que um app existe ou que uma conexão está pronta '
                               'sem ter consultado.'],
      "spec-make-define": ['ficam "a confirmar na conta" se o BRAINSTORM não os trouxer.'],
      "spec-make-design": ['marque cada um como "a confirmar na conta" e não declare o blueprint validado.'],
      "spec-make-build": ["a confirmar na conta", "e as operações. Não afirme que criou, rodou ou ligou nada.",
                          "Importar blueprint"]}
# avaliador fresco do s3, ciclo 2 (M1b, M1c): o aviso em 1 frase e o "sem o conector" na linha "Gerada", inteiros
M1["spec-make-handoff"] = ['"a confirmar na conta" em cada estado. Não afirme `lastEdit`, custódia nem contagem de registros '
                           'sem ter lido a conta.',
                           'Se a conversa não tiver o MCP do Make, avise em uma frase, escreva "sem o conector" na linha '
                           '"Gerada" da ficha e preencha o inventário']
REGRAS.append(Regra("M1", _skill("spec-make-handoff"), at="AT-009", contem=M1["spec-make-handoff"]))
for _nome, _n, _rot, _prox in ETAPAS:
    REGRAS.append(Regra("M1", _skill(_nome), at="AT-006", contem=M1[_nome]))
    REGRAS.append(Regra("E1", _skill(_nome), at="UX MUST 4",
                        contem=[f"spec-make · Etapa {_n} de 4 — {_rot}", _prox]))


# Regras que vivem nos arquivos de referência (fora das âncoras), com a polaridade inteira (avaliador, ciclo 4). Uma frase
# ACRESCENTADA que desmente a regra é pega pelo snapshot de tests/regras.py. Vale também para o trecho de um SKILL.md que
# fica fora de qualquer âncora (o passo a passo numerado).
FRASES: dict[str, list[str]] = {
    # avaliador fresco do s3, ciclo 2 (B9): o passo 9 da build entrega o handoff com os ids lidos agora e a sessão
    "spec-make-build/SKILL.md": [
        "9. **Fichas.** Preencha a ficha do fluxo e o handoff — `HANDOFF_<FLUXO>.md` pela skill `spec-make-handoff`, "
        "com os ids lidos agora e esta sessão no histórico — e feche com [E1]."],
    "spec-make-design/references/GOVERNANCA_DO_FLUXO.md": [
        "**Sem a chave:** recuse o DESIGN como pronto e peça a chave.",
        "**Sem o passo:** recuse o DESIGN e diga o que falta; a etapa 4 para antes de criar o fluxo.",
        "**Sem o registro:** recuse o DESIGN como pronto."],
    "spec-make-design/references/PROMPTS_DE_IA.md": [
        "| nome |", "| módulo |", "| versão | v1 |", "| provedor e modelo |", "| entrada |", "| saída e consumidor |",
        "| tipo |", "| completude |", "| se faltar dado |", "| autônomo ou com aceite | com aceite sempre que grava ([G1]) |",
        "| teste mínimo | 1 entrada de exemplo (sem dado pessoal real) e a saída esperada |"],
    "spec-make-define/references/VERIFY_GATE_EXECUCAO.md": [
        "amostra: <descrição; sem dado pessoal real; origem: pública | inventada>",
        '"O blueprint foi validado" como teste: recuse e peça amostra e resultado esperado.',
        "Fluxo que grava sem a segunda execução: recuse como incompleto.",
        "Amostra com dado pessoal real: troque por dado inventado ou público."],
    "spec-make-build/references/PROTOCOLO.md": [
        "a contagem não pode mudar e a 2ª execução tem de ter processado o item",
        "Execução que não processou nada também gasta 1 operação: com fila, confira que a linha nova voltou como "
        "`processado = true`.",
        "use a chave natural `TESTE-1` e acrescente ao filtro do `searchRows`",
        "o destino segue com 1 linha com essa chave, as operações são maiores que zero **e** a linha nova voltou como "
        "`processado = true`",
        "acrescente ao filtro do `searchRows` a condição `chave_natural` igual a `TESTE-1` (as duas condições juntas), para "
        "o teste nunca ler nem marcar um pendente real",
        # 1.3.3: o verificador é obrigatório no build com Supabase e reprovar para o fluxo
        "Fluxo que toca Supabase: o verificador é obrigatório; se ele reprovar, não crie o fluxo: diga o problema e indique "
        "\"Use a skill spec-make-design.\"",
        # 1.3.1: a 3ª execução, com a fila vazia, prova o filtro e o pacote vazio
        "Com fila, rode também uma 3ª execução com a fila vazia: ela termina em sucesso e gasta exatamente 1 operação.",
        "Faça ainda a **3ª execução com a fila vazia**: ela termina em sucesso e gasta exatamente 1 operação",
        # R2@opus (rodada 2): o passo 10 inteiro, que a linha "Gatilho real" não repete
        "a 2ª execução tem de ter processado o item (operações maiores que zero; ela pode gastar menos que a 1ª). "
        "Execução que não processou nada também gasta 1 operação",
        # R1@opus + A2@fable (rodada 2): ligar de verdade tira o filtro de teste, valida e confere
        "no mesmo `scenarios_update` tire a condição `TESTE-1` do `searchRows`",
        "o filtro ficou só com `processado` igual a `false`",
        "A chave do aceite (`chave_do_aceite`) também começa com `TESTE-`",
        "(operações maiores que zero; ela pode gastar menos que a 1ª): execução que não processou nada não testa nada"],
    # SPEC_MAKE_S5: as receitas com polaridade (o "nunca", o "sempre" e as travas do SQL inteiros)
    "spec-make-design/references/SUPABASE.md": [
        "Do app `supabase` entram só estes cinco módulos:",
        "- `postgres` (conexão direta com a senha do banco): abre o banco inteiro e esbarra na restrição de rede do projeto;",
        "**Dinheiro é sempre `numeric(18,2)`**, nunca `real` nem `float`",
        "nunca recalcule a sugestão da IA nem use \"agora\" no campo `quando` na hora de gravar a auditoria",
        "Marcar só `id` e `processado` falha em \"coluna obrigatória vazia\"",
        "revoke all on public.<auditoria> from anon, authenticated;",
        "if tg_op = 'UPDATE' and new is not distinct from old then return new; end if;",
        "with (security_invoker = true)",
        "where chave_do_aceite not like 'TESTE-%' group by 1, 2;",
        "if to_regclass('public.<fila>') is not null then",
        "if to_regclass('public.<auditoria>') is not null then",
        "if to_regclass('public.<destino>') is not null then",
        "pg_get_expr(d.adbin, d.adrelid) = 'false'",
        "and format_type(a.atttypid, a.atttypmod) <> 'numeric(18,2)'))) then",
        "escreva aqui o nome de CADA coluna de dinheiro do fluxo, entre aspas e com vírgula",
        "where a.attrelid = 'public.<fila>'::regclass and a.attname = 'id' and a.attidentity = 'd') then",
        "a condição `chave_natural` *Equals* `TESTE-1`, para o teste nunca ler nem marcar um pendente real",
        "A pessoa lê essa view no SQL Editor do Supabase (`select * from public.<auditoria>_taxa_de_correcao`),",
        "No blueprint, o valor do\n   filtro vai **em texto** (`\"b\": \"false\"`): com o booleano `false` o Make ignora a condição",
        "devolve **1 pacote vazio** (não zero): o 1º módulo depois da busca leva o filtro",
        "if not exists (select 1 from pg_attribute a\n                    where a.attrelid = 'public.<fila>'::regclass and a.attname = 'processado_em'",
        "raise exception 'Prepare o banco: <fila>.processado_em (timestamptz) não existe",
        "raise exception 'Prepare o banco: a auditoria precisa dos 6 campos de [G2]"],
    "spec-make-design/references/PROTOCOLO.md": [
        'Sem acesso à web nesta conversa, escreva "não consultado".',
        "Nunca escreva o valor da chave no DESIGN."],
    "spec-make-build/references/DIAGNOSTICO.md": [
        "Correções só no fluxo que esta conversa criou ([B4])."],
    # SPEC_MAKE_HANDOFF, review pós-build R2@opus: o handoff não desarma a conferência de lastEdit da [B6]
    "spec-make-handoff/references/PROTOCOLO.md": [
        'Nunca troque o `lastEdit` da ficha pelo da conta sem o "sim" da pessoa.',
        "**Sem o \"sim\":** a ficha mantém o `lastEdit` antigo"],
}


# AT-007 (R5 da review do DESIGN do s3): jargão do harness que a pessoa não lê no corpo da skill de handoff.
JARGAO = ("transversal", "etapa 5")


def jargao(texto: str) -> list[str]:
    """Palavras de JARGAO fora do frontmatter (o `metadata.fase: "transversal"` do frontmatter não conta)."""
    corpo = re.sub(r"\A---\n.*?\n---\n", "", texto, count=1, flags=re.S).lower()
    return [j for j in JARGAO if j in corpo]


def checar_frases(arquivo: str, texto: str) -> list[str]:
    t = _junto(texto)
    return [f"{arquivo}: falta {f!r}" for f in FRASES.get(arquivo, []) if _junto(f) not in t]


def bloco(texto: str, ancora: str) -> str | None:
    marca = f"**[{ancora}] "          # definição: "**[B2] Pergunta…"; a menção "**[B2]**" não conta
    i = texto.find(marca)
    if i < 0:
        return None
    resto = texto[i + len(marca):]
    fim = len(resto)
    for m in re.finditer(r"\*\*\[[A-Z]\d\] |\n#{1,3} ", resto):
        fim = m.start()
        break
    return resto[:fim]


def _junto(s: str) -> str:
    """Quebra de linha e espaço repetido viram 1 espaço: a frase pode estar quebrada em linhas no Markdown."""
    return " ".join(s.split())


def checar_texto(regra: Regra, texto: str) -> list[str]:
    b = bloco(texto, regra.ancora)
    if b is None:
        return [f"[{regra.ancora}] âncora ausente em {regra.arquivo}"]
    b = _junto(b)
    erros = [f"[{regra.ancora}] {regra.arquivo}: falta {t!r}" for t in regra.contem if _junto(t) not in b]
    pos = -1
    for t in regra.em_ordem:
        j = b.find(t, pos + 1)
        if j < 0:
            erros.append(f"[{regra.ancora}] {regra.arquivo}: {t!r} ausente ou fora da ordem")
            break
        pos = j
    # Ordem estrita das PRIMEIRAS menções: um token citado antes do anterior ("3. `scenarios_create` e depois
    # `validate_module_configuration`") manda fazer fora da ordem, mesmo que uma menção posterior esteja no lugar.
    primeiras = [(t, b.find(t)) for t in regra.em_ordem if t in b]
    for (ant, i_ant), (t, i) in zip(primeiras, primeiras[1:]):
        if i < i_ant:
            erros.append(f"[{regra.ancora}] {regra.arquivo}: {t!r} citado antes de {ant!r}")
    return erros


def checar(regra: Regra) -> list[str]:
    caminho = RAIZ / "skills" / regra.arquivo
    if not caminho.is_file():
        return [f"[{regra.ancora}] arquivo ausente: {regra.arquivo}"]
    return checar_texto(regra, caminho.read_text(encoding="utf-8"))


def mutantes(regra: Regra, texto: str) -> list[tuple[str, str]]:
    """Textos alterados que a regra TEM de reprovar: cada token removido do bloco e, se houver ordem, um par trocado."""
    b = bloco(texto, regra.ancora)
    if b is None:
        return []
    saida = []
    j = _junto(b) + "\n\n"
    for t in regra.contem + regra.em_ordem:
        if _junto(t) in j:
            saida.append((f"sem {t!r}", texto.replace(b, j.replace(_junto(t), "XXX"))))
    if len(regra.em_ordem) >= 2:
        a, c = regra.em_ordem[0], regra.em_ordem[-1]
        trocado = b.replace(a, "\x00").replace(c, a).replace("\x00", c)
        saida.append((f"ordem {a!r}↔{c!r}", texto.replace(b, trocado)))
    return saida
