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

REGRAS: list[Regra] = [
    Regra("B1", _skill("spec-make-build", "references/PROTOCOLO.md"), at="AT-002",
          contem=['"on-demand"', "confidential: true", "credential-requests_create",
                  "esperar a pessoa autorizar e conferir de novo. Nunca peça chave no chat."],
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
    Regra("B6", _skill("spec-make-build"), at="AT-003",
          contem=["contam como criados por esta conversa para [B4] — e só eles",
                  "editado no Make depois da ficha", 'siga só depois do "sim" da pessoa',
                  "releia `data-stores_list` e `hooks_list` e recalcule a custódia",
                  "nunca chame `data-stores_delete`, `data-stores_update` de estrutura nem `hooks_delete` sobre ele"],
          em_ordem=["lastEdit", "scenarioUsages", "scenarios_update"]),
    Regra("E1", _skill("spec-make-build"), at="AT-006", contem=["`HANDOFF_<FLUXO>.md`", "o handoff, como continuar depois"]),
    # skill de handoff: fora de ETAPAS (não é etapa — a 1ª linha não diz "Etapa N de 4")
    Regra("H1", _skill("spec-make-handoff", "references/PROTOCOLO.md"), at="AT-002",
          contem=["desta família", "compartilhado com N cenários", "fora do spec-make", "scenarioUsages", "lastEdit",
                  "pergunte quais cenários fazem parte do fluxo", "`scenarios_list` só quando a pessoa der o nome sem o id",
                  "Cenário que a pessoa não confirmou nunca entra como `desta família`."],
          em_ordem=["environment_get", "scenarios_get", "hooks_list", "data-stores_list", "connections_list"]),
    Regra("H2", _skill("spec-make-handoff"), at="AT-005",
          contem=["Nunca chame `scenarios_create`, `scenarios_update`", "`data-store-records_list`",
                  "do webhook, guarde só o id e o nome", "quem altera é a etapa 3 ou 4, sob a custódia da ficha"]),
    Regra("H3", _skill("spec-make-handoff"), at="AT-006",
          contem=["nunca crie um arquivo novo para a mesma família", "Use a skill spec-make-", "sem nenhum trecho entre « »"],
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
          contem=["fora do histórico", "modelo", "versão do prompt", "sugestão original", "quem aceitou",
                  "(UTC)", "se editou", "Sem esse registro, recuse o DESIGN como pronto."]),
    Regra("G3", _skill("spec-make-design"), at="AT-011",
          contem=["chave natural", "já existe ⇒ não grava de novo",
                  "Sem a chave, recuse o DESIGN como pronto e peça a chave."]),
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
M1["spec-make-handoff"] = ['"a confirmar na conta" em cada estado. Não afirme `lastEdit`, custódia nem contagem de registros '
                           'sem ter lido a conta.']
REGRAS.append(Regra("M1", _skill("spec-make-handoff"), at="AT-009", contem=M1["spec-make-handoff"]))
for _nome, _n, _rot, _prox in ETAPAS:
    REGRAS.append(Regra("M1", _skill(_nome), at="AT-006", contem=M1[_nome]))
    REGRAS.append(Regra("E1", _skill(_nome), at="UX MUST 4",
                        contem=[f"spec-make · Etapa {_n} de 4 — {_rot}", _prox]))


# Regras que vivem nos arquivos de referência (fora das âncoras), com a polaridade inteira (avaliador, ciclo 4). Uma frase
# ACRESCENTADA que desmente a regra é pega pelo snapshot de tests/regras.py.
FRASES: dict[str, list[str]] = {
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
        "a contagem não pode mudar e a 2ª execução tem de ter processado o item"],
    "spec-make-build/references/DIAGNOSTICO.md": [
        "Correções só no fluxo que esta conversa criou ([B4])."],
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
