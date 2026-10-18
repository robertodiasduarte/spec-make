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
                  # rodada 1b (R1@codex): sem a seção (alerta do [B7] aceito), o 2b não exige o SQL
                  "Sem a seção no DESIGN (alerta do [B7] aceito), diga que o banco pode não ter as travas e siga para o "
                  "passo 3.",
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
                  # SPEC_MAKE_S6: depois da 3ª correção, alerta; "Seguir assim" libera mais 1 (R8@opus: sem teto fixo junto)
                  "**Teto: 3 tentativas** de correção para o mesmo teste sem perguntar: o teste roda até 4 vezes antes do "
                  "alerta",
                  "Se a execução depois da 3ª correção ainda falhar: alerta [A1] — cada nova tentativa gasta operações e o "
                  "problema pode estar no desenho; recomende parar e entregar o resumo.",
                  'Sem a escolha de "Seguir assim", não corrija nem rode de novo, deixe o fluxo sob demanda e entregue o resumo',
                  'cada "Seguir assim" libera mais 1 correção.'],
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
    # SPEC_MAKE_S6 AT-009: builders by RDD e alerta no lugar da recusa
    Regra("P1", _skill("spec-make-design"), at="AT-009",
          contem=["registre cada prompt no inventário de PROMPTS_E_SKILLS.md com `tipo: prompt`.",
                  "Se o fluxo é sob demanda com interface e a pessoa vai acioná-lo pelo assistente, ou ela pede uma skill em "
                  "volta do fluxo, registre também uma linha `tipo: skill`.",
                  "a etapa 4 gera cada prompt com a skill `prompt-builder-by-rdd` e cada skill com a skill "
                  "`skill-builder-by-rdd`, a partir desse contrato.",
                  "Fluxo com módulo de IA e sem esse inventário: alerta [A1] — sem o contrato, a etapa 4 escreve um prompt "
                  "provisório que ninguém conferiu."]),
    # SPEC_MAKE_HANDOFF (s3): custódia pela ficha na build — lastEdit e usos relidos ANTES de gravar (A2 da review do DESIGN)
    # avaliador fresco do s3, ciclo 1: a conferência do lastEdit e a regra do compartilhado, com a polaridade inteira
    # ("se for diferente, diga … e siga só depois do sim"; "compartilhado: só ler … — nunca chame") — trechos soltos
    # passavam com a regra invertida
    Regra("B6", _skill("spec-make-build"), at="AT-003",
          contem=["contam como criados por esta conversa para [B4] — e só eles",
                  # SPEC_MAKE_S6: o "sim" vira o alerta [A1] com a escolha "Seguir assim"
                  "editado no Make depois da ficha",
                  "Primeiro leia `scenarios_get` de cada parte e compare o `lastEdit` com o da ficha: se for diferente, "
                  'diga em 1 frase os dois horários ("editado no Make depois da ficha") e faça o alerta [A1]: a mudança '
                  'pode apagar o que alguém fez no Make depois da ficha; siga só depois de a pessoa escolher "Seguir assim '
                  'e registrar o alerta".',
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
                  "O fecho segue [K5] e entrega o recibo e dois arquivos, `FICHA_DO_FLUXO_<FLUXO>.md` e `HANDOFF_<FLUXO>.md`, pede para "
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
          contem=["checar_handoff.py", "checar_documento.py", "URL de webhook", "11 ou mais dígitos", "sem id",
                  # SPEC_MAKE_S6 AT-007: ERRO (ou 2) não entrega; AVISO vira alerta. SPEC_MAKE_S7: a ficha passa também pelo [F2]
                  "Saiu 1 (ERRO: URL de webhook, credencial, CPF ou CNPJ inteiro, ou sequência de 11 ou mais dígitos) ou 2 "
                  "(a ficha não pôde ser lida): não entregue — troque o trecho pela máscara do [F1] (segredo: pelo id) ou grave "
                  "a ficha de novo e confira outra vez ([X1]).",
                  "Saiu 3 (AVISO: seção faltando, trecho de modelo, recurso sem id): alerta [A1] para cada aviso — a próxima "
                  "conversa pode retomar pelo recurso errado."]),
    Regra("E1", _skill("spec-make-handoff"), at="AT-001",
          contem=["Toda resposta abre com o mapa de posição ([K1] de references/CONDUCAO.md), que começa",
                  'por "Handoff (fora das etapas)"; a primeira resposta traz antes a linha de versão.', "O fecho segue [K5]",
                  "Use a skill spec-make-"]),
    Regra("P1", _skill("spec-make-build"), at="AT-009",
          contem=["gere cada linha `tipo: prompt` com a skill `prompt-builder-by-rdd`",
                  "gere cada linha `tipo: skill` com a skill `skill-builder-by-rdd` só depois do teste aprovado, quando o "
                  "cenário já existe com a interface gravada e a ferramenta MCP dele tem nome",
                  "(`https://github.com/robertodiasduarte/skills-by-rdd/releases/latest/download/<builder>.zip`) e siga",
                  "para prompt, escreva um prompt provisório pelo contrato, com alerta [A1]",
                  "para skill, siga sem ela, com alerta [A1].",
                  "Fluxo com módulo de IA e sem inventário de prompts e skills no DESIGN, ou IA que grava sem o aceite humano "
                  "[G1] ou sem o registro do aceite [G2]: alerta [A1] antes do `scenarios_create` — sem o contrato o prompt "
                  "sai sem conferência, e sem o aceite a IA grava sozinha."]),
    Regra("G1", _skill("spec-make-design"), at="AT-007",
          contem=["pessoa identificada antes da gravação",
                  "Sem esse passo: alerta [A1] — a IA grava lançamento, documento ou cadastro sem que ninguém responda por "
                  "ele."]),
    Regra("G2", _skill("spec-make-design"), at="AT-007",
          contem=["fora do histórico", "planilha ou data store",
                  # SPEC_MAKE_SUPABASE AT-006: com Supabase, a auditoria só de acréscimo é a 1ª opção
                  "quando o fluxo já usa Supabase, a 1ª opção é uma tabela de auditoria só de acréscimo", "modelo", "versão do prompt", "sugestão original", "quem aceitou",
                  "(UTC)", "se editou",
                  "Sem esse registro: alerta [A1] — não há como provar quem aceitou cada sugestão nem medir quanto a IA "
                  "erra."]),
    Regra("G3", _skill("spec-make-design"), at="AT-011",
          contem=["chave natural", "já existe ⇒ não grava de novo",
                  "consultar antes de gravar, ou gravar substituindo pela chave",
                  "Quando o destino é uma tabela do Supabase, a chave existe nela como restrição ([S5]).",
                  "Sem a chave: alerta [A1] — o mesmo item processado de novo (e-mail reaberto, nova tentativa) vira "
                  "registro duplicado."]),
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
                  # SPEC_MAKE_S6: postgres/supabase-management fora do alcance ([X2]); alcance vazio é alerta
                  "`postgres` (conexão direta) e `supabase-management` ficam fora do alcance do kit ([X2]).",
                  "Sem o alcance: alerta [A1] — quem mexer no fluxo depois não sabe o que a chave secreta alcança."]),
    Regra("S2", _skill("spec-make-design"), at="AT-002",
          contem=[COND, "do app `supabase` entram só `searchRows`, `createARow`, `upsertARecord`, `getRowsCount` e "
                  "`deleteRows`",
                  "e a pessoa não faz, antes do 1º fluxo rodar, mais que 1 colagem de SQL, copiar o Project ID e a chave "
                  "do painel e criar 1 conexão no Make.",
                  "Edge function, webhook de qualquer tipo, Database Webhook, `pg_cron`, `supabase:watchEvents`, "
                  "`supabase:makeAnApiCall` e módulo HTTP para o endereço de um projeto Supabase ficam fora do alcance do "
                  "kit ([X2]): diga isso e proponha o caminho só com o banco, sem perguntar."]),
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
                  "Gatilho que não seja a agenda do Make nem a execução sob demanda fica fora do alcance do kit ([X2]).",
                  "Filtro por coluna vazia: alerta [A1] — o Make não filtra coluna vazia, e a busca lê a fila inteira de novo "
                  "a cada disparo."]),
    Regra("S4", _skill("spec-make-design"), at="AT-004",
          contem=[COND, "agenda do Make com o intervalo, ou sob demanda", "disparos por mês × operações do disparo vazio",
                  "Se o fluxo toca Supabase, o DESIGN declara no bloco `Relógio` como o fluxo dispara — agenda do Make "
                  "com o intervalo, ou sob demanda — e, com agenda, soma no custo as operações paradas: disparos por mês "
                  "× operações do disparo vazio.",
                  "Se o total passar do orçamento do DEFINE: alerta [A1] — o plano acaba antes do fim do mês e o fluxo para; "
                  "recomende um intervalo maior."]),
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
                  "auditoria anulável, auditoria sem o gatilho ou sem a view: alerta [A1] — nomeie a coluna, o campo ou o "
                  "rateio; o risco é duplicar lançamento, arredondar dinheiro errado ou perder a prova do aceite."]),
    Regra("W1", _skill("spec-make-design"), at="AT-007",
          contem=["uma vez", "a URL, a data, o módulo e a versão", "vale a conta",
                  "Para cada app do fluxo, consulte a documentação pública do Make (`https://apps.make.com/<app>`) uma "
                  "vez e anote em `Fontes consultadas` a URL, a data, o módulo e a versão.",
                  "Se ela divergir de `app-modules_list`, vale a conta, e o DESIGN anota a divergência.",
                  'Sem acesso à web, escreva "não consultado" — nunca afirme uma consulta que não fez — e faça o alerta '
                  "[A1]: o módulo pode ter mudado desde a documentação que você conhece."]),
    # SPEC_MAKE_S6: o que falta de documentação vira alerta ([B7]); o fora do alcance e o ERRO do verificador param ([B8])
    Regra("B7", _skill("spec-make-build"), at="AT-004",
          contem=["Se o DESIGN toca Supabase", "coluna `alcance` preenchida com o motivo, as tabelas e as operações",
                  "seção `Prepare o banco` com o SQL quando o fluxo grava no banco",
                  "bloco `Relógio` com o gatilho e, quando é agenda, o intervalo e a linha de operações paradas na seção "
                  "`Custo`.",
                  "Faltando algum: alerta [A1] antes de qualquer `scenarios_create` — sem eles, ninguém sabe o que a chave "
                  "alcança, o banco pode não ter as travas e o custo parado não foi somado."]),
    Regra("B8", _skill("spec-make-build"), at="AT-005",
          contem=["Pare antes de qualquer `scenarios_create`, sem alerta nem pergunta, em dois casos.",
                  "do app `supabase` algo além de `searchRows`, `createARow`, `upsertARecord`, `getRowsCount` e `deleteRows`",
                  "ou módulo `postgres` ou `supabase-management`, ou HTTP para o projeto, ou gatilho que não seja a agenda do "
                  "Make nem sob demanda: fica fora do alcance do kit ([X2]); diga o que falta e indique \"Use a skill "
                  "spec-make-design.\".",
                  "(2) `scripts/checar_blueprint.py` sai 1 (ERRO) ou 2 (não leu o arquivo: nada foi conferido): não crie o "
                  "fluxo; diga o problema e indique a mesma skill.",
                  # rodada 1b (R3@opus): confidencial e interface se corrigem sozinhos; [N1] com motivo do módulo não alerta
                  "Saída 3 (AVISO): confidencial desligado e chave `interface` no blueprint você corrige sozinho e avisa "
                  "([C1]; a interface vai por `scenarios_set-interface`)",
                  "o aviso de HTTP ([N1]) de módulo que tem no DESIGN a linha de motivo do [N1] com o número dele não vira "
                  "alerta — o design já decidiu; cada outro aviso vira alerta [A1].",
                  "Rode o verificador em todo fluxo; se o ambiente não executa código, faça a mesma conferência lendo."]),
    Regra("D1", _skill("spec-make-define"), at="AT-008",
          contem=["agregados ou mascarados quando a amostra é real", "resultado esperado", "segunda execução da mesma", "mesma contagem",
                  # SPEC_MAKE_S6 (varredura de polaridade numa cópia): o trecho curto aparece 2× no bloco; tirar o "sem" de
                  # 1 deles passava
                  "Ele traz: a amostra (a estrutura, com exemplo mascarado, e de onde veio), o resultado esperado escrito com valores",
                  # SPEC_MAKE_S6: o gate de execução continua; a falta dele vira alerta
                  'Teste que só confere uma execução de um fluxo que grava, ou "blueprint validado" como teste de aceite: '
                  "alerta [A1] — os validadores do Make já aprovaram blueprint que falhou na primeira execução, e sem a 2ª "
                  "execução um fluxo que duplica registros passa no teste"]),
    Regra("D2", _skill("spec-make-define"), at="AT-004",
          contem=["Dê nota de 0 a 3 para problema, quem usa, objetivos, aceite e escopo.",
                  "Nota abaixo de 12 de 15, ou `A CONFIRMAR:` ainda aberto na entrega: alerta [A1] — a etapa 3 vai desenhar "
                  "sobre uma suposição, e o teste pode aprovar o fluxo errado.",
                  "Orçamento acima de 80% do plano: alerta [A1] — o plano pode acabar antes do fim do mês."]),
    Regra("D3", _skill("spec-make-define"), at="AT-003",
          contem=["Cada critério sai com a frase de escritório, a forma EARS e, logo abaixo, `Em outras palavras: <frase do "
                  "dia a dia>`.",
                  "Na primeira vez, ensine o EARS em 3 linhas com um critério do próprio fluxo da pessoa"]),
    Regra("E2", _skill("spec-make-brainstorm"), at="AT-001",
          contem=["Na primeira resposta, depois da linha de versão e do mapa, explique em 4 a 6 linhas",
                  "o que é o spec-make, as 4 etapas e o handoff, o que a pessoa recebe no fim",
                  "conta no Make, o conector do Make com as ferramentas que gravam e uma amostra da rotina — pode ser o arquivo "
                  "real.",
                  "Depois do parágrafo, escreva o aviso do [F1] em até 3 linhas, sem ícone de alerta e sem pergunta.",
                  "`environment_get` (conta e equipe), as ferramentas `scenarios_create`, `scenarios_activate` e "
                  "`scenarios_run`, e `connections_list`",
                  "Faltando algum, diga como resolver em passos numerados (references/PROTOCOLO.md) e siga a conversa; nunca "
                  "encerre nem peça para voltar depois.",
                  "A resposta termina com uma única pergunta: qual rotina a pessoa quer automatizar."]),
]
# [M1] com a polaridade inteira em cada etapa (R3@opus, rodada 6)
M1 = {"spec-make-brainstorm": ['como "a confirmar na conta". Não afirme que um app existe ou que uma conexão está pronta '
                               'sem ter consultado.',
                               # SPEC_MAKE_S6 AT-002: sem o conector, os passos para ligá-lo
                               "Mostre também como ligar o conector, em passos numerados ([E2])."],
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
    # SPEC_MAKE_S6 AT-001: o mapa de posição em toda resposta substitui a linha "spec-make · Etapa n de 4 — X"
    REGRAS.append(Regra("E1", _skill(_nome), at="AT-001",
                        contem=["Toda resposta abre com o mapa de posição ([K1] de references/CONDUCAO.md), que começa por",
                                f'"Etapa {_n} de 4 · {_rot}"; a primeira resposta traz antes a linha de versão.',
                                "O fecho segue [K5]", _prox]))


# SPEC_MAKE_S6 AT-008: [N1] igual nas 3 skills que escolhem módulo
N1 = ["Para cada passo do fluxo, procure primeiro o módulo do próprio app no Make",
      # rodada 1b (R4@opus): o motivo nomeia o módulo, para o build casar o aviso do verificador com a linha certa
      "HTTP só entra com o motivo escrito no documento, uma linha por módulo, com o número dele",
      "e só depois considere o módulo HTTP genérico",
      "HTTP sem esse motivo, ou com módulo oficial disponível: alerta [A1] — a chamada HTTP pede endereço, cabeçalho e "
      "autenticação montados à mão, e o módulo oficial já traz a conexão e os campos.",
      "Com o Supabase, HTTP fica fora do alcance ([X2])."]
for _nome in ("spec-make-brainstorm", "spec-make-design", "spec-make-build"):
    REGRAS.append(Regra("N1", _skill(_nome), at="AT-008", contem=N1))

# SPEC_MAKE_S6: compartilhado/CONDUCAO.md, prendido pela cópia do brainstorm (test_compartilhados garante as 5 iguais)
CONDUCAO = _skill("spec-make-brainstorm", "references/CONDUCAO.md")
GLOSSARIO = ["fluxo", "cenário", "módulo", "conexão", "gatilho", "operação", "data store", "interface", "blueprint", "EARS",
             "critério de aceite", "alerta"]
REGRAS += [
    Regra("K1", CONDUCAO, at="AT-001",
          contem=["Toda resposta, inclusive a primeira, abre com uma linha neste formato:",
                  "`📍 Etapa <n> de 4 · <Etapa> — passo <k> de <K>: <passo> · depois: <próxima etapa>`",
                  "`📍 Handoff (fora das etapas) — passo <k> de <K>: <passo> · depois: <etapa que o prompt de retomada abre>`",
                  'O número e o nome de cada passo vêm da tabela "Passos do mapa"', "a linha tem até 80 caracteres."]),
    Regra("K2", CONDUCAO, at="AT-003",
          contem=["Na primeira vez que um destes termos aparecer na conversa, explique-o em uma frase, entre parênteses ou "
                  "depois de travessão, nunca num parágrafo:"] + [f"- {g} — " for g in GLOSSARIO]),
    Regra("K3", CONDUCAO, at="AT-003",
          contem=["faça uma pergunta por mensagem, com 2 ou 3 opções; para cada opção, 1 linha de prós, 1 de contras e 1 de "
                  "risco; feche com `✅ Recomendo: <opção>, porque <motivo em 1 linha>`. Até 10 linhas no total."]),
    Regra("K4", CONDUCAO, at="AT-003",
          contem=["Não pergunte o que o MCP do Make responde (plano, operações por mês, conexões, módulos de cada app) nem o "
                  "que tem resposta padrão: aplique e avise em 1 linha",
                  "o módulo oficial do app antes da chamada HTTP ([N1]); fluxo confidencial; sob demanda durante o teste",
                  "Rollback quando toda gravação do fluxo é idempotente pela chave natural"]),
    Regra("K5", CONDUCAO, at="AT-001",
          contem=["Ao terminar, escreva nesta ordem: `✅ Etapa <n> de 4 concluída`",
                  "o arquivo, pelo nome exato, e onde salvá-lo; os alertas aceitos, se houver ([A2]); e o próximo comando "
                  "num bloco de código único, que já diz quais arquivos anexar, pelo nome."]),
    Regra("A1", CONDUCAO, at="AT-004",
          contem=['Quando uma regra marcada "alerta [A1]" não for atendida, a etapa continua: escreva o alerta neste formato '
                  "e espere a escolha da pessoa.",
                  "⚠️ ALERTA (alerta <i> de <n>) — <o que falta, em 1 linha>", "1. Corrigir agora",
                  "2. Seguir assim e registrar o alerta", "A opção recomendada vem primeiro.",
                  'Só a escolha de "Seguir assim e registrar o alerta" — a opção ou a frase dela — libera o passo; "sim" '
                  'solto, "ok", outra resposta ou nenhuma resposta valem "Corrigir agora".',
                  "Mais de um alerta no mesmo ponto: um por mensagem, o de maior risco primeiro"]),
    Regra("A2", CONDUCAO, at="AT-006",
          contem=["Cada alerta aceito vira uma linha na seção `## Alertas aceitos` do documento da etapa",
                  'sem nenhum, a seção diz "nenhum".',
                  "A etapa seguinte lista os alertas aceitos das anteriores logo no começo da conversa; a etapa 4 os repete "
                  "no recibo e na seção `Alertas aceitos` da ficha do fluxo, e o handoff os mantém em \"Falta\" até alguém "
                  "corrigir."]),
    Regra("A3", CONDUCAO, at="AT-004",
          # rodada 1b (R6@opus): cada documento que falta, e o teste de aceite sempre na versão curta
          contem=["Sem um documento que a etapa precisa (o BRAINSTORM na etapa 2; o BRAINSTORM e o DEFINE na 3; os três na "
                  "4): alerta [A1] — a etapa vai trabalhar sem o que a anterior decidiu e conferiu na conta.",
                  '"Corrigir agora" é o comando pronto da primeira etapa que falta',
                  "e sempre a amostra e o resultado esperado do teste de aceite"]),
    Regra("X1", CONDUCAO, at="AT-005",
          contem=["Estes três não viram alerta e nenhuma confirmação os libera; diga o que fazer no lugar, na mesma mensagem, "
                  "sem culpar a pessoa:",
                  # SPEC_MAKE_S7: dado pessoal saiu do bloqueio; o item 1 é só segredo (test_contrato prende "3 itens, 0 dado pessoal")
                  "Segredo, credencial ou endereço de webhook (que carrega o código de acesso) no blueprint, na amostra, na "
                  "ficha ou em qualquer documento.",
                  "No lugar: conexão autorizada por link, ou só o id.",
                  'Ligar o gatilho sem a resposta "Ligar agora" à pergunta do gatilho da etapa 4 ([B2]).',
                  "Apagar, mudar a estrutura ou alterar recurso que esta conversa não criou e que a ficha não marca como "
                  "`desta família`, ou marcado `compartilhado`"]),
    # SPEC_MAKE_S7 AT-001/AT-002/AT-006/AT-007: o arquivo real da rotina e a conferência do documento
    Regra("F1", CONDUCAO, at="AT-001",
          contem=["A pessoa pode anexar ou colar o arquivo real da rotina (extrato, nota fiscal, folha, CSV com CNPJ ou CPF) em "
                  "qualquer etapa.",
                  "Nunca peça dado inventado ou público no lugar dele.",
                  "diga em até 6 linhas o que entendeu do arquivo",
                  "Se leu só parte, diga quanto leu",
                  "guardam só a estrutura e a regra, com exemplo mascarado, e uma linha dizendo o que foi mascarado. "
                  "Nunca copie linha do arquivo.",
                  "| CPF | `***.123.456-**` |", "| CNPJ de cliente | `12.345.***/****-90` |",
                  "| Nome de pessoa | o papel:", "| Salário ou valor de pessoa |", "| E-mail pessoal | `m***@dominio.com.br` |",
                  "CNPJ de companhia aberta é público: escreva inteiro, com `(CNPJ público)` logo depois do número.",
                  "Se o documento anterior diz `origem: real`, abra com uma linha:",
                  "Dado real só na origem de teste, com 1 item por execução e o fluxo confidencial ([B1]).",
                  "teste com dado real da rotina · confidencial · origem de teste: <nome>",
                  "escreva em até 3 linhas, sem ícone de alerta e sem pergunta:",
                  "Sobre o seu arquivo: pode anexar o real.",
                  'Sem o conector do Make ([M1]), tire o trecho "(zona <zona>)" e não invente uma zona.',
                  "Isto é aviso, não alerta [A1]."]),
    Regra("F2", CONDUCAO, at="AT-003",
          contem=["rode `python3 scripts/checar_documento.py <arquivo>`",
                  "Sem Python, confira à mão os mesmos itens: endereço de webhook, sequência de 11 ou mais dígitos, CPF e CNPJ "
                  "inteiros, chave ou senha escrita no texto.",
                  "Saiu 1 (ERRO): não entregue.",
                  "diga em 3 partes o que achou, o que já fez e que a pessoa não precisa fazer nada.",
                  "Saiu 2 (arquivo ilegível): grave o documento de novo e confira outra vez.",
                  "Saiu 3 (AVISO: e-mail pessoal inteiro): alerta [A1]",
                  "Saiu 0: entregue."]),
    Regra("X2", CONDUCAO, at="AT-005",
          contem=["e, num fluxo com Supabase, gatilho que não seja a agenda do Make nem a execução sob demanda ([S3])",
                  "não viram alerta nem pergunta: diga que o spec-make não desenha esse caminho, porque usa o Supabase só "
                  "como banco, e proponha o caminho só com o banco."]),
]

# Regras que vivem nos arquivos de referência (fora das âncoras), com a polaridade inteira (avaliador, ciclo 4). Uma frase
# ACRESCENTADA que desmente a regra é pega pelo snapshot de tests/regras.py. Vale também para o trecho de um SKILL.md que
# fica fora de qualquer âncora (o passo a passo numerado).
FRASES: dict[str, list[str]] = {
    # SPEC_MAKE_S6 AT-006 (contrato C2 #4): define, design e handoff listam os alertas aceitos das etapas anteriores
    "spec-make-design/SKILL.md": ["Liste no começo os alertas aceitos das etapas anteriores ([A2]).",
                                  "Preencha o template com o blueprint no fim, confira-o pelo **[F2]** e feche com [E1].",
                                  "Se a amostra diz `origem: real`, diga a linha de continuidade do **[F1]**.",
                                  "Sem o DEFINE, siga o [A3].",
                                  "Depois de 3 tentativas no mesmo módulo: alerta [A1] — o módulo pode não aceitar essa "
                                  "configuração na sua conta",
                                  "**A pessoa quer a IA gravando direto:** alerta [A1] pelo [G1]"],
    "spec-make-handoff/SKILL.md": ['Mantenha em "Falta" os alertas aceitos das etapas ([A2]).',
                                   # SPEC_MAKE_S7 AT-003: a ficha também passa por checar_documento ([F2])
                                   "e depois `python3 scripts/checar_documento.py HANDOFF_<FLUXO>.md` ([F2]).",
                                   "troque o trecho pela máscara do [F1] (segredo: pelo id) ou grave a ficha de novo"],
    # SPEC_MAKE_S7 AT-003: o passo "documento" cita o [F2] nas 4 skills que entregam documento
    "spec-make-brainstorm/SKILL.md": ["Preencha o template, confira-o pelo **[F2]**, entregue o arquivo e feche com **[E1]**.",
                                      "Peça uma amostra da rotina (pode ser o arquivo real), devolva o que entendeu dela pelo **[F1]**"],
    "spec-make-define/SKILL.md": ["Liste no começo os alertas aceitos das etapas anteriores ([A2]).",
                                  "Sem o BRAINSTORM, siga o [A3].",
                                  "Preencha o template, confira-o pelo **[F2]** e feche com [E1].",
                                  "Se a amostra diz `origem: real`, diga a linha de continuidade do **[F1]**."],
    # SPEC_MAKE_S6 AT-002 (contrato C2 #5): os 4 pré-requisitos, cada um com passos (test_contrato conta os passos)
    "spec-make-brainstorm/references/PROTOCOLO.md": ["### Conector ausente", "### Conector só de leitura",
                                                     "### Conexão faltando", "### Sem amostra",
                                                     "Comece pela linha de versão e pelo mapa da regra [E1].",
                                                     # SPEC_MAKE_S7 AT-006 / UX SHOULD-3: o aviso e os estados do anexo
                                                     "Sobre o seu arquivo: pode anexar o real.",
                                                     "### Anexo que a skill não consegue ler",
                                                     "Arquivo com senha: a senha é segredo ([X1]); não peça nem use;",
                                                     "nunca invente o conteúdo."],
    # SPEC_MAKE_S6 AT-003: o termo e a pergunta remetem ao CONDUCAO.md; o EARS é ensinado 1 vez, com o fluxo da pessoa
    "spec-make-brainstorm/references/COPY.md": ["a lista e a frase de cada termo estão em [CONDUCAO.md](CONDUCAO.md) [K2]."],
    "spec-make-define/references/EARS.md": ["## Como ensinar (1 vez por conversa)",
                                            "com um critério do fluxo da própria pessoa (nunca o do CNPJ"],
    # avaliador fresco do s3, ciclo 2 (B9): o passo 9 da build entrega o handoff com os ids lidos agora e a sessão
    "spec-make-build/SKILL.md": [
        # SPEC_MAKE_S6 AT-006 (contrato C2 #4): o build repete os alertas aceitos no recibo e na ficha
        "Liste no começo os alertas aceitos das etapas anteriores ([A2]).",
        # rodada 1b (R5@opus): o resumo do Quick start não pode dizer que só o [B8] para
        "O que para o build está em **[B8]** e nos bloqueios [X1] ([B2], [B4], [B6]); o resto vira alerta.",
        "Recibo com operações gastas e os alertas aceitos que ficaram pendentes ([A2])",
        # SPEC_MAKE_S7 AT-003/AT-007: o recibo passa pelo [F2]; com origem real, o teste fica na origem de teste, confidencial
        "confira-o pelo **[F2]** e faça a pergunta **[B2]**.",
        'com `origem: real` no DEFINE, o teste só na origem de teste, com 1 item e o fluxo confidencial, e a linha "teste com '
        'dado real da rotina" ([F1])',
        "a ficha os repete na seção `Alertas aceitos` ([A2]).",
        "Sem algum dos três documentos, siga o [A3].",
        # rodada 1b (A2@fable): DEFINE sem teste aceito no Define — o build monta o mínimo; sem amostra, alerta
        "DEFINE sem teste de aceite (alerta do [D1] aceito na etapa 2): monte um teste mínimo com a amostra do BRAINSTORM",
        "sem amostra nenhuma: alerta [A1] — o fluxo nunca rodou com dado de verdade",
        "além do que o [B3] corrige: alerta [A1] — corrigir aqui deixa o DESIGN desatualizado",
        "alerta [A1] — o Make interrompe a execução quando a cota acaba.",
        "9. **Fichas.** Preencha a ficha do fluxo e o handoff — `HANDOFF_<FLUXO>.md` pela skill `spec-make-handoff`, "
        "com os ids lidos agora e esta sessão no histórico — e feche com [E1]."],
    "spec-make-design/references/GOVERNANCA_DO_FLUXO.md": [
        "**Sem a chave:** alerta [A1]; peça a chave.",
        "**Sem o passo:** alerta [A1]; diga o que falta e ofereça o desenho com o passo.",
        "**Sem o registro:** alerta [A1]."],
    "spec-make-design/references/PROMPTS_E_SKILLS.md": [
        "| nome |", "| tipo | prompt (módulo de IA) ou skill (fluxo acionado pelo assistente) |", "| módulo |",
        "| versão | v1 |", "| provedor e modelo |", "| entrada |", "| saída e consumidor |", "| repetição |", "| completude |",
        "| se faltar dado |", "| autônomo ou com aceite | com aceite sempre que grava ([G1]) |",
        "| teste mínimo | 1 entrada de exemplo (mascarada, [F1]) e a saída esperada |",
        "| ferramenta MCP |", "| campos da interface |", "| limite | a skill só chama o cenário; não grava nada fora dele |",
        "| prompt | a skill `prompt-builder-by-rdd` | antes de criar o fluxo",
        "| skill | a skill `skill-builder-by-rdd` | depois do teste aprovado"],
    "spec-make-define/references/VERIFY_GATE_EXECUCAO.md": [
        "amostra: <estrutura; exemplo mascarado> (origem: real, mascarada aqui | inventada | pública)",
        '"O blueprint foi validado" como teste: alerta [A1]; peça amostra e resultado esperado.',
        "Fluxo que grava sem a segunda execução: alerta [A1] — sem ela, um fluxo que repete o mesmo item duplica registros "
        "sem ninguém perceber",
        "Amostra com dado real no documento: mascare pela tabela do [F1] e confira pelo [F2]; o teste roda na origem de teste, "
        "com o fluxo confidencial."],
    "spec-make-build/references/PROTOCOLO.md": [
        "a contagem não pode mudar e a 2ª execução tem de ter processado o item",
        "Execução que não processou nada também gasta 1 operação: com fila, confira que a linha nova voltou como "
        "`processado = true`.",
        "use a chave natural `TESTE-1` e acrescente ao filtro do `searchRows`",
        "o destino segue com 1 linha com essa chave, as operações são maiores que zero **e** a linha nova voltou como "
        "`processado = true`",
        "acrescente ao filtro do `searchRows` a condição `chave_natural` igual a `TESTE-1` (as duas condições juntas), para "
        "o teste nunca ler nem marcar um pendente real",
        # SPEC_MAKE_S6 (R2@opus): o verificador roda em todo fluxo; a parada mora só no [B8]
        "o verificador roda em todo fluxo; o que fazer com cada saída (0, 1, 2 e 3) está no [B8] do SKILL.md.",
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


# SPEC_MAKE_S6 AT-004 (contrato C2 #3): cada item da lista do AT-004 tem frase de alerta prendida — conjunto NOMEADO, nunca
# "o que por acaso já está em REGRAS" (guard que itera sobre o que aparece é default-PASS para ausência)
D, DF, B, H = "spec-make-design/SKILL.md", "spec-make-define/SKILL.md", "spec-make-build/SKILL.md", "spec-make-handoff/SKILL.md"
ITENS_AT004: dict[str, tuple[str, str]] = {
    "G1": (D, "Sem esse passo: alerta [A1]"), "G2": (D, "Sem esse registro: alerta [A1]"), "G3": (D, "Sem a chave: alerta [A1]"),
    "S1": (D, "Sem o alcance: alerta [A1]"), "S3": (D, "Filtro por coluna vazia: alerta [A1]"),
    "S4": (D, "Se o total passar do orçamento do DEFINE: alerta [A1]"),
    "S5": (D, "auditoria sem o gatilho ou sem a view: alerta [A1]"), "W1": (D, "e faça o alerta [A1]"),
    "P1-design": (D, "Fluxo com módulo de IA e sem esse inventário: alerta [A1]"),
    "P1-build": (B, "alerta [A1] antes do `scenarios_create`"),
    "B3": ("spec-make-build/references/DIAGNOSTICO.md", "ainda falhar: alerta [A1]"),
    "B6": (B, "e faça o alerta [A1]: a mudança pode apagar"), "B7": (B, "Faltando algum: alerta [A1]"),
    "D1": (DF, '"blueprint validado" como teste de aceite: alerta [A1]'), "D2": (DF, "na entrega: alerta [A1]"),
    "N1-brainstorm": ("spec-make-brainstorm/SKILL.md", "ou com módulo oficial disponível: alerta [A1]"),
    "N1-design": (D, "ou com módulo oficial disponível: alerta [A1]"),
    "N1-build": (B, "ou com módulo oficial disponível: alerta [A1]"),
    "H4": (H, "alerta [A1] para cada aviso"),
    "A3-define": (DF, "Sem o BRAINSTORM, siga o [A3]."), "A3-design": (D, "Sem o DEFINE, siga o [A3]."),
    "A3-build": (B, "Sem algum dos três documentos, siga o [A3]."),
    "validacao-3x": (D, "Depois de 3 tentativas no mesmo módulo: alerta [A1]"),
    "ia-grava-direto": (D, "**A pessoa quer a IA gravando direto:** alerta [A1]"),
    "desenho-errado": (B, "além do que o [B3] corrige: alerta [A1]"),
    "plano-sem-operacoes": (B, "alerta [A1] — o Make interrompe a execução quando a cota acaba."),
    "define-sem-teste": (B, "sem amostra nenhuma: alerta [A1] — o fluxo nunca rodou com dado de verdade"),
}


def itens_sem_frase(regras: list[Regra], frases: dict[str, list[str]]) -> list[str]:
    """Itens do AT-004 cujo trecho de alerta não está prendido (contem de uma Regra do mesmo arquivo ou FRASES)."""
    faltam = []
    for nome, (arq, trecho) in ITENS_AT004.items():
        alvo = _junto(trecho)
        prendidos = [_junto(s) for r in regras if r.arquivo == arq for s in r.contem] + [_junto(s) for s in frases.get(arq, [])]
        if not ("alerta [A1]" in alvo or "[A3]" in alvo) or not any(alvo in s for s in prendidos):
            faltam.append(nome)
    return faltam

