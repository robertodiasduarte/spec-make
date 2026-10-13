"""Checagens do padrão ouro de skill (estrutura) usadas por test_padrao_ouro.py.

Cada função recebe o caminho da pasta da skill e devolve uma lista de problemas (vazia = ok).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SKILLS = ["spec-make-brainstorm", "spec-make-define", "spec-make-design", "spec-make-build"]

SECOES = [
    "## Quick start",
    "## Quando usar / Quando não usar",
    "## Dados necessários",
    "## Procedimento passo a passo",
    "## Validações e checklist de qualidade",
    "## Tratamento de exceções",
    "## Examples",
    "## Inventário do bundle",
    "## Metodologia e autoria",
]
AUTORIA = "Esta skill foi construída com a metodologia de Roberto Dias Duarte."

# Faixas de emoji e pictogramas (o padrão ouro proíbe emoji no corpo da skill).
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\U00002B00-\U00002BFF]")

# Frases que qualificam a pessoa pelo que ela não sabe: lidas do compartilhado/COPY.md (fonte única), que por isso fica
# de fora da varredura.
def _proibidas() -> list[str]:
    texto = (RAIZ / "compartilhado" / "COPY.md").read_text(encoding="utf-8")
    m = re.search(r"Frases proibidas:(.*?)Descrever o produto", texto, re.S)
    frases = re.findall(r'"([^"]+)"', m.group(1)) if m else []
    assert len(frases) >= 5, "COPY.md sem a lista de frases proibidas"
    # a frase pode estar quebrada em linhas no Markdown: compara palavra a palavra, com qualquer espaço entre elas
    return [r"\s+".join(re.escape(w) for w in f.split()) for f in frases]


PROIBIDAS = _proibidas()


def frontmatter(texto: str) -> dict[str, str]:
    m = re.match(r"\A---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return {}
    campos: dict[str, str] = {}
    for linha in m.group(1).splitlines():
        mm = re.match(r"^(\s*)([a-z_]+):\s*\"?(.*?)\"?\s*$", linha)
        if mm and mm.group(3):
            chave = ("metadata." if mm.group(1) else "") + mm.group(2)
            campos[chave] = mm.group(3)
    return campos


def checar_skill(pasta: Path) -> list[str]:
    nome = pasta.name
    p: list[str] = []
    skill = pasta / "SKILL.md"
    if not skill.is_file():
        return [f"{nome}: SKILL.md ausente"]
    texto = skill.read_text(encoding="utf-8")

    fm = frontmatter(texto)
    if fm.get("name") != nome:
        p.append(f"{nome}: frontmatter name={fm.get('name')!r} diferente da pasta")
    if fm.get("license") != "MIT":
        p.append(f"{nome}: license precisa ser MIT")
    if fm.get("metadata.author") != "Roberto Dias Duarte":
        p.append(f"{nome}: metadata.author ausente")
    if fm.get("metadata.methodology") != "Metodologia de Roberto Dias Duarte":
        p.append(f"{nome}: metadata.methodology ausente")
    desc = fm.get("description", "")
    if not desc or len(desc) > 1024:
        p.append(f"{nome}: description ausente ou acima de 1024 caracteres ({len(desc)})")

    linhas = texto.splitlines()
    if len(linhas) >= 500:
        p.append(f"{nome}: SKILL.md com {len(linhas)} linhas (limite: menos de 500)")
    if EMOJI.search(texto):
        p.append(f"{nome}: SKILL.md tem emoji")

    posicoes = []
    for s in SECOES:
        idx = [i for i, l in enumerate(linhas) if l.strip() == s]
        if len(idx) != 1:
            p.append(f"{nome}: seção {s!r} ausente ou repetida")
        else:
            posicoes.append(idx[0])
    if len(posicoes) == len(SECOES) and posicoes != sorted(posicoes):
        p.append(f"{nome}: as seções estão fora da ordem do padrão ouro (8 + Inventário + Metodologia e autoria)")
    if not any(l.startswith("# ") for l in linhas[: posicoes[0] if posicoes else len(linhas)]):
        p.append(f"{nome}: título (# ) ausente antes do Quick start")
    m = re.search(r"^## Metodologia e autoria\n+(.+)$", texto, re.M)
    if not m or m.group(1).strip() != AUTORIA:
        p.append(f"{nome}: seção Metodologia e autoria sem a frase literal")

    # links relativos do SKILL.md apontam para arquivos presentes
    for alvo in re.findall(r"\]\(((?:references|assets|scripts|evals)/[^)#]+)\)", texto):
        if not (pasta / alvo).is_file():
            p.append(f"{nome}: link para arquivo ausente: {alvo}")
    # todo arquivo do bundle é citado no SKILL.md (inventário honesto)
    for arq in sorted(pasta.rglob("*")):
        if arq.is_file() and "__pycache__" not in arq.parts and arq.name != ".DS_Store":
            rel = arq.relative_to(pasta).as_posix()
            if rel != "SKILL.md" and rel not in texto and arq.name not in texto:
                p.append(f"{nome}: arquivo do bundle não citado no SKILL.md: {rel}")

    if not (pasta / "references" / "RUNTIME_COMPATIBILITY.md").is_file():
        p.append(f"{nome}: references/RUNTIME_COMPATIBILITY.md ausente")

    man_p = pasta / "manifest.json"
    if not man_p.is_file():
        p.append(f"{nome}: manifest.json ausente")
    else:
        man = json.loads(man_p.read_text(encoding="utf-8"))
        if not man.get("o_que_ainda_nao_prova"):
            p.append(f"{nome}: manifest.json sem o_que_ainda_nao_prova")
        if man.get("version") != fm.get("metadata.version"):
            p.append(f"{nome}: manifest.json version difere do SKILL.md")
        for item in man.get("nucleo", []):
            if not (pasta / item).is_file():
                p.append(f"{nome}: manifest.json cita arquivo ausente: {item}")

    ev_p = pasta / "evals" / "cases.json"
    if not ev_p.is_file():
        p.append(f"{nome}: evals/cases.json ausente")
    else:
        tipos = {c.get("type") for c in json.loads(ev_p.read_text(encoding="utf-8")).get("cases", [])}
        if "positive" not in tipos or "negative_control" not in tipos:
            p.append(f"{nome}: evals precisa de ao menos 1 caso positive e 1 negative_control")

    return p


def checar_copy(pasta: Path) -> list[str]:
    """Varre SKILL.md, references/ e assets/ (exceto COPY.md, que lista as frases) pela lista proibida."""
    p = []
    for arq in sorted(pasta.rglob("*.md")):
        if arq.name == "COPY.md":
            continue
        texto = arq.read_text(encoding="utf-8")
        for padrao in PROIBIDAS:
            if re.search(padrao, texto, re.I):
                p.append(f"{pasta.name}/{arq.relative_to(pasta)}: frase proibida ({padrao})")
    return p
