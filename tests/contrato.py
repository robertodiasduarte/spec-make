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
    Regra("P1", _skill("spec-make-design"), at="AT-007", contem=["inventário de prompts", "sdd-prompt-builder"]),
    Regra("P1", _skill("spec-make-build"), at="AT-007",
          contem=["sem inventário", "[G1]", "[G2]",
                  "sem inventário de prompts no DESIGN: pare antes do `scenarios_create`, diga o que falta"]),
    Regra("G1", _skill("spec-make-design"), at="AT-007",
          contem=["pessoa identificada antes da gravação",
                  "Sem esse passo, recuse o DESIGN como pronto e diga o que falta."]),
    Regra("G2", _skill("spec-make-design"), at="AT-007",
          contem=["fora do histórico", "modelo", "versão do prompt", "sugestão original", "quem aceitou",
                  "(UTC)", "se editou", "recuse o DESIGN"]),
    Regra("G3", _skill("spec-make-design"), at="AT-011",
          contem=["chave natural", "já existe ⇒ não grava de novo",
                  "Sem a chave, recuse o DESIGN como pronto e peça a chave."]),
    Regra("D1", _skill("spec-make-define"), at="AT-008",
          contem=["sem dado pessoal real", "resultado esperado", "segunda execução da mesma", "mesma contagem",
                  "no destino. Recuse como incompleto o teste que só confere uma execução",
                  ', e recuse "blueprint validado" como teste de aceite']),
]
for _nome, _n, _rot, _prox in ETAPAS:
    REGRAS.append(Regra("M1", _skill(_nome), at="AT-006", contem=["a confirmar na conta"] if _nome != "spec-make-build"
                        else ["a confirmar na conta", "e as operações. Não afirme que criou, rodou ou ligou nada.",
                              "Importar blueprint"]))
    REGRAS.append(Regra("E1", _skill(_nome), at="UX MUST 4",
                        contem=[f"spec-make · Etapa {_n} de 4 — {_rot}", _prox]))


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
