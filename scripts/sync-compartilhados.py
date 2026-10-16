#!/usr/bin/env python3
"""Copia os arquivos de compartilhado/ para as skills (fonte única; cada zip é autônomo).

Uso:
    python3 -I scripts/sync-compartilhados.py           # copia
    python3 -I scripts/sync-compartilhados.py --check   # só confere; sai 1 se alguma cópia divergir ou faltar

Biblioteca padrão; Python 3.9+.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FONTE = RAIZ / "compartilhado"
SKILLS = ["spec-make-brainstorm", "spec-make-define", "spec-make-design", "spec-make-build", "spec-make-handoff"]

# arquivo de compartilhado/ → (pasta de destino dentro da skill, skills que recebem)
MAPA = {
    "MCP_MAKE.md": ("references", SKILLS),
    "COPY.md": ("references", SKILLS),
    "RUNTIME_COMPATIBILITY.md": ("references", SKILLS),
    "SUPABASE.md": ("references", SKILLS),
    "checar_blueprint.py": ("scripts", ["spec-make-design", "spec-make-build"]),
}


def pares() -> list[tuple[Path, Path]]:
    saida = []
    for arquivo, (pasta, skills) in MAPA.items():
        for s in skills:
            saida.append((FONTE / arquivo, RAIZ / "skills" / s / pasta / arquivo))
    return saida


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    erros = []
    for origem, destino in pares():
        if not origem.is_file():
            erros.append(f"fonte ausente: {origem.relative_to(RAIZ)}")
            continue
        conteudo = origem.read_bytes()
        if a.check:
            if not destino.is_file():
                erros.append(f"cópia ausente: {destino.relative_to(RAIZ)}")
            elif destino.read_bytes() != conteudo:
                erros.append(f"cópia divergente: {destino.relative_to(RAIZ)} (rode scripts/sync-compartilhados.py)")
        else:
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(conteudo)
    if erros:
        print("\n".join(f"FAIL: {e}" for e in erros))
        return 1
    print(f"PASS: sync-compartilhados — {len(pares())} cópia(s) {'conferidas' if a.check else 'gravadas'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
