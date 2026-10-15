"""Mapa caso de eval NEGATIVO → âncora(s) que o recusam (SPEC_MAKE s2; Success Criteria do s1).

ORÁCULO: duplica de propósito o campo `regras` de skills/*/evals/cases.json — é contra ele que test_evals.py compara.
Caso negativo novo entra aqui primeiro. Os dentes vêm dos mutantes em memória de test_evals.py (troca por outra âncora
válida, `regras` removida, vazia ou acrescida): cada um tem de gerar um erro que cite o caso mutado.
"""
from __future__ import annotations

from contrato import RAIZ, REGRAS

ESPERADO: dict[str, dict[str, set[str]]] = {
    "spec-make-brainstorm": {"sem-mcp": {"M1"}, "amostra-pessoal": {"COPY"}},
    "spec-make-define": {"gate-uma-execucao": {"D1"}, "gate-blueprint-validado": {"D1"}, "sem-mcp": {"M1"}},
    "spec-make-design": {"sem-chave-natural": {"G3"}, "ia-grava-direto": {"G1"}, "aceite-sem-registro": {"G2"},
                         "ia-sem-inventario": {"P1"}, "sem-mcp": {"M1"}},
    "spec-make-build": {"sem-sim-gatilho": {"B2"}, "falha-3x": {"B3"}, "fluxo-alheio": {"B4"}, "sem-mcp": {"M1"},
                        "ia-sem-inventario": {"P1"}, "apaga-compartilhado": {"B6"}, "lastedit-mudou": {"B6"},
                        "uso-novo-externo": {"B6"}},
    "spec-make-handoff": {"placeholder-sobrando": {"H4"}, "webhook-na-ficha": {"H2"}, "sem-mcp": {"M1"},
                          "arquivo-por-slice": {"H3"}, "primeira-ficha-sem-partes": {"H1"}},
}


def ancora_da_skill(skill: str, ancora: str) -> bool:
    """A âncora tem regra NESTA skill: Regra em contrato.REGRAS cujo arquivo é da skill, ou, para COPY, o
    references/COPY.md da skill (cópia de compartilhado/COPY.md) com a lista de frases proibidas."""
    if ancora == "COPY":
        copy_md = RAIZ / "skills" / skill / "references/COPY.md"
        return copy_md.is_file() and "Frases proibidas:" in copy_md.read_text(encoding="utf-8")
    return any(r.ancora == ancora and r.arquivo.startswith(skill + "/") for r in REGRAS)


def problemas(ev_por_skill: dict[str, dict]) -> list[str]:
    """Erros do mapa, 1 por caso e sempre com `<skill>/<id>` no texto. Itera sobre o ESPERADO (caso ausente é erro) e
    também sobre os negativos do JSON (negativo fora do mapa é erro)."""
    erros: list[str] = []
    for skill, esperado in ESPERADO.items():
        lista = (ev_por_skill.get(skill) or {}).get("cases", [])
        ids = [c.get("id") for c in lista]
        for cid in sorted({i for i in ids if ids.count(i) > 1}, key=str):
            # o dicionário abaixo guardaria só o último: o 1º, com a âncora errada, sumiria (A1@codex, rodada 2 do s2)
            erros.append(f"{skill}/{cid}: id repetido em cases.json")
        casos = {c.get("id"): c for c in lista}
        for cid, ancoras in esperado.items():
            c = casos.get(cid)
            if c is None:
                erros.append(f"{skill}/{cid}: caso esperado ausente")
                continue
            if c.get("type") != "negative_control":
                erros.append(f"{skill}/{cid}: type {c.get('type')!r} em vez de negative_control")
            regras = c.get("regras")
            if not isinstance(regras, list) or not regras:
                erros.append(f"{skill}/{cid}: sem `regras`")
                continue
            if set(regras) != ancoras or len(regras) != len(set(regras)):
                erros.append(f"{skill}/{cid}: regras {sorted(regras)} diferente do esperado {sorted(ancoras)}")
            for a in regras:
                if not ancora_da_skill(skill, a):
                    erros.append(f"{skill}/{cid}: âncora {a} sem regra em {skill}")
        for cid, c in casos.items():
            if c.get("type") == "negative_control" and cid not in esperado:
                erros.append(f"{skill}/{cid}: caso negativo fora do mapa ESPERADO de tests/evals.py")
    return erros
