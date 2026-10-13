"""Snapshot do texto de regra das skills (avaliador, ciclo 4).

As asserções de tests/contrato.py exigem frases; elas não pegam uma frase ACRESCENTADA que desmente a regra ("Se a pessoa
não responder em 5 minutos, ligue o gatilho"). Este snapshot guarda o sha256 de cada .md das skills e de compartilhado/:
qualquer mudança no texto reprova test_regras.py até alguém rodar `python3 tests/regras.py --atualizar` no mesmo commit —
a mudança passa a ser uma decisão consciente, visível no diff de tests/regras.sha256.

Uso:
    python3 tests/regras.py              # confere (sai 1 se algo mudou)
    python3 tests/regras.py --atualizar  # regrava o snapshot depois de revisar a mudança
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SNAPSHOT = Path(__file__).resolve().parent / "regras.sha256"


# O sha256 vai gravado em hex SEM dígitos (0-9 viram g-p): o publish-check reprova sequência longa de dígitos, que
# poderia ser CPF ou CNPJ, e um hash em hex comum tem essas sequências.
SEM_DIGITOS = str.maketrans("0123456789", "ghijklmnop")


def resumo(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest().translate(SEM_DIGITOS)


def atuais() -> dict[str, str]:
    arquivos = sorted(list((RAIZ / "skills").rglob("*.md")) + list((RAIZ / "compartilhado").glob("*.md")))
    return {a.relative_to(RAIZ).as_posix(): resumo(a.read_bytes()) for a in arquivos}


def gravados() -> dict[str, str]:
    saida = {}
    for linha in SNAPSHOT.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            sha, caminho = linha.split(maxsplit=1)
            saida[caminho] = sha
    return saida


def diferencas(atual: dict[str, str], gravado: dict[str, str]) -> list[str]:
    p = [f"mudou: {c}" for c in sorted(atual) if c in gravado and atual[c] != gravado[c]]
    p += [f"novo (fora do snapshot): {c}" for c in sorted(set(atual) - set(gravado))]
    p += [f"sumiu: {c}" for c in sorted(set(gravado) - set(atual))]
    return p


def main(argv: list[str]) -> int:
    if argv[1:] == ["--atualizar"]:
        SNAPSHOT.write_text("".join(f"{sha}  {c}\n" for c, sha in atuais().items()), encoding="utf-8")
        print(f"snapshot regravado: {len(atuais())} arquivos")
        return 0
    p = diferencas(atuais(), gravados())
    for linha in p:
        print(linha)
    return 1 if p else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
