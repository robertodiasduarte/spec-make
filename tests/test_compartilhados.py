"""Decision 1: as cópias de compartilhado/ nas skills são idênticas à fonte.

SPEC_MAKE_HANDOFF (s3, proposta #4 do contrato C2): o conjunto de cópias é DERIVADO de sync.MAPA × skills — nunca uma
contagem fixa (o `len == 14` antigo não mudava sozinho com a 5ª skill, LM-088/LM-250) — e cada fonte diz que é igual
"em todas as skills", nunca "nas quatro".

Avaliador fresco do s3, ciclo 1 (AT-001): derivar o esperado de sync.SKILLS deixava a skill tirada de lá sem conferência
(cópia velha + "14 cópia(s) conferidas" + unittest OK). As skills vêm das PASTAS de skills/: cada .md de compartilhado/
tem de estar idêntico em references/ de toda pasta, e sync.SKILLS/MAPA têm de cobrir todas elas.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("sync", RAIZ / "scripts" / "sync-compartilhados.py")
sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sync)  # type: ignore[union-attr]

FRASE = "Este arquivo é igual em todas as skills do spec-make."
PROIBIDA = "quatro skills"


def pastas() -> list[str]:
    """As skills pelo disco, nunca pelo próprio sync."""
    return sorted(p.name for p in (RAIZ / "skills").iterdir() if p.is_dir())


def esperados() -> set[tuple[Path, Path]]:
    """Todo .md de compartilhado/ em references/ de TODA pasta de skills/; o resto (checar_blueprint.py) pelo MAPA."""
    md = {(arq, RAIZ / "skills" / s / "references" / arq.name)
          for arq in sync.FONTE.glob("*.md") for s in pastas()}
    outros = {(sync.FONTE / arq, RAIZ / "skills" / s / pasta / arq)
              for arq, (pasta, skills) in sync.MAPA.items() if not arq.endswith(".md") for s in skills}
    return md | outros


def problemas_cobertura() -> list[str]:
    """sync.SKILLS e cada .md do MAPA cobrem exatamente as pastas de skills/; todo .md de compartilhado/ está no MAPA."""
    p = []
    if sorted(sync.SKILLS) != pastas():
        p.append(f"sync.SKILLS {sorted(sync.SKILLS)} != pastas de skills/ {pastas()}")
    for arq in sorted(a.name for a in sync.FONTE.glob("*.md")):
        if arq not in sync.MAPA:
            p.append(f"{arq}: fora do MAPA")
        elif sorted(sync.MAPA[arq][1]) != pastas():
            p.append(f"{arq}: MAPA cobre {sorted(sync.MAPA[arq][1])}, não {pastas()}")
    return p


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
        self.assertEqual(problemas_cobertura(), [])
        self.assertEqual(set(pares), esperados())
        self.assertEqual(len(pares), len(set(pares)), "par repetido")
        self.assertEqual({d.parent.parent.name for _, d in pares}, set(pastas()), "skill sem cópia")
        # confere pelo esperado (derivado das pastas), não pelos pares do sync: skill fora do sync não escapa
        for origem, destino in sorted(esperados()):
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

    def test_sync_sem_uma_skill_reprova(self):
        """Mutante em memória do AT-001: tirar uma skill de sync.SKILLS (e, com ela, do MAPA) tem de reprovar."""
        self.assertEqual(problemas_cobertura(), [])
        for fora in pastas():
            menos = [s for s in sync.SKILLS if s != fora]
            mapa = {a: (pasta, [s for s in skills if s != fora]) for a, (pasta, skills) in sync.MAPA.items()}
            with self.subTest(fora=fora), mock.patch.object(sync, "SKILLS", menos), \
                    mock.patch.object(sync, "MAPA", mapa):
                self.assertTrue(problemas_cobertura(), "sync sem a skill passou")
                self.assertNotEqual(set(sync.pares()), esperados())
        # só o MAPA de um .md perde a skill (SKILLS intacto): também reprova
        mapa = dict(sync.MAPA, **{"COPY.md": ("references", sync.SKILLS[:-1])})
        with mock.patch.object(sync, "MAPA", mapa):
            self.assertTrue(problemas_cobertura())


if __name__ == "__main__":
    unittest.main()
