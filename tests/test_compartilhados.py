"""Decision 1: as cópias de compartilhado/ nas skills são idênticas à fonte.

SPEC_MAKE_HANDOFF (s3, proposta #4 do contrato C2): o conjunto de cópias é DERIVADO de sync.MAPA × skills — nunca uma
contagem fixa (o `len == 14` antigo não mudava sozinho com a 5ª skill, LM-088/LM-250) — e cada fonte diz que é igual
"em todas as skills", nunca "nas quatro".
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("sync", RAIZ / "scripts" / "sync-compartilhados.py")
sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sync)  # type: ignore[union-attr]

FRASE = "Este arquivo é igual em todas as skills do spec-make."
PROIBIDA = "quatro skills"


def esperados() -> set[tuple[Path, Path]]:
    return {(sync.FONTE / arq, RAIZ / "skills" / s / pasta / arq)
            for arq, (pasta, skills) in sync.MAPA.items() for s in skills}


def problemas_texto(nome: str, texto: str) -> list[str]:
    p = []
    if FRASE not in texto:
        p.append(f"{nome}: sem a frase {FRASE!r}")
    if PROIBIDA in texto:
        p.append(f"{nome}: ainda diz {PROIBIDA!r}")
    return p


class Compartilhados(unittest.TestCase):
    def test_copias_identicas(self):
        pares = sync.pares()
        self.assertEqual(set(pares), esperados())
        self.assertEqual(len(pares), len(set(pares)), "par repetido")
        self.assertEqual({d.parent.parent.name for _, d in pares}, set(sync.SKILLS), "skill sem cópia")
        for origem, destino in pares:
            with self.subTest(destino=str(destino.relative_to(RAIZ))):
                self.assertTrue(destino.is_file())
                self.assertEqual(destino.read_bytes(), origem.read_bytes())

    def test_texto_da_fonte(self):
        for arq in sorted(sync.FONTE.glob("*.md")):
            with self.subTest(fonte=arq.name):
                self.assertEqual(problemas_texto(arq.name, arq.read_text(encoding="utf-8")), [])
        texto = (sync.FONTE / "COPY.md").read_text(encoding="utf-8")
        self.assertTrue(problemas_texto("mutante", texto.replace(FRASE, "Este arquivo é igual nas quatro skills do spec-make.")))
        self.assertTrue(problemas_texto("mutante", texto + "\nVale para as quatro skills.\n"))


if __name__ == "__main__":
    unittest.main()
