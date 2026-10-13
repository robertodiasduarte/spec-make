#!/usr/bin/env python3
"""Version gate: every skill carries its own version, and a changed skill must bump it.

Quem baixa o .zip não dá git pull: a versão e a data dentro do SKILL.md são a única forma de a
pessoa saber que a cópia envelheceu. Este gate impede que essa informação minta.

Checks, for each skills/<name>/SKILL.md:
  1. metadata.version is X.Y.Z and metadata.updated is YYYY-MM;
  2. the body has the identification line
     `<name> vX.Y.Z · <mês>/<ano> · versão atual: <URL>` matching the metadata;
  3. manifest.json and evals/cases.json, when present, carry the same "version";
  4. with --base REF: a skill whose folder changed since REF has a version greater than the one
     in REF (a new skill, or one without version in REF, passes), and updated is not older.

Usage:
  python3 scripts/check-versions.py                    # structural checks only
  python3 scripts/check-versions.py --base origin/main # plus the bump check
Exit 0 = PASS, 1 = FAIL. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = "https://github.com/robertodiasduarte/spec-make/releases/latest"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
UPDATED = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")


def meta(text: str, key: str) -> str | None:
    fm = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not fm:
        return None
    m = re.search(rf"^  {key}:\s*\"?([^\"\n]*)\"?\s*$", fm.group(1), re.M)
    return m.group(1).strip() if m else None


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def semver(v: str) -> tuple[int, int, int]:
    return tuple(int(x) for x in SEMVER.match(v).groups())  # type: ignore[union-attr]


def check_skill(d: Path, base: str | None) -> list[str]:
    name = d.name
    erros: list[str] = []
    text = (d / "SKILL.md").read_text(encoding="utf-8")
    v, u = meta(text, "version"), meta(text, "updated")
    if not v or not SEMVER.match(v):
        return [f"{name}: metadata.version ausente ou fora de X.Y.Z ({v!r})"]
    if not u or not UPDATED.match(u):
        return [f"{name}: metadata.updated ausente ou fora de AAAA-MM ({u!r})"]
    ano, mes = u.split("-")
    linha = f"`{name} v{v} · {MESES[int(mes) - 1]}/{ano} · versão atual: {URL}`"
    if linha not in text:
        erros.append(f"{name}: linha de identificação ausente ou diferente do metadata; esperado {linha}")
    for extra in ("manifest.json", "evals/cases.json"):
        p = d / extra
        if p.exists():
            got = json.loads(p.read_text(encoding="utf-8")).get("version")
            if got is not None and got != v:
                erros.append(f"{name}: {extra} tem version {got!r}, SKILL.md tem {v!r}")

    if base:
        changed = git("diff", "--name-only", base, "--", f"skills/{name}/").stdout.strip()
        if changed:
            old = git("show", f"{base}:skills/{name}/SKILL.md")
            if old.returncode == 0:
                ov, ou = meta(old.stdout, "version"), meta(old.stdout, "updated")
                if ov and SEMVER.match(ov) and semver(v) <= semver(ov):
                    erros.append(f"{name}: a skill mudou desde {base} e a versão não subiu ({ov} -> {v})")
                if ou and UPDATED.match(ou) and u < ou:
                    erros.append(f"{name}: metadata.updated voltou no tempo ({ou} -> {u})")
    return erros


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="git ref to compare against (e.g. origin/main)")
    a = ap.parse_args()
    base = a.base
    if base and git("rev-parse", "--verify", "--quiet", f"{base}^{{commit}}").returncode != 0:
        print(f"check-versions: base {base!r} indisponível; só as checagens estruturais.")
        base = None
    erros: list[str] = []
    skills = sorted(p.parent for p in (ROOT / "skills").glob("*/SKILL.md"))
    for d in skills:
        erros += check_skill(d, base)
    if erros:
        print("\n".join(f"FAIL: {e}" for e in erros))
        print("check-versions: FAIL — suba metadata.version (e a linha de identificação) da skill alterada.")
        return 1
    print(f"PASS: check-versions — {len(skills)} skills com versão coerente" + (f", comparadas a {base}." if base else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
