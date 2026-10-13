"""Casos de eval: formato, regras citadas existentes e os negativos exigidos pelo DEFINE (AT-006, AT-007, AT-008, AT-011)."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from contrato import REGRAS

RAIZ = Path(__file__).resolve().parents[1]
EXIGIDOS = {
    "spec-make-brainstorm": {"sem-mcp"},
    "spec-make-define": {"gate-uma-execucao", "gate-blueprint-validado", "sem-mcp"},
    "spec-make-design": {"sem-chave-natural", "ia-grava-direto", "aceite-sem-registro", "ia-sem-inventario", "sem-mcp"},
    "spec-make-build": {"sem-sim-gatilho", "falha-3x", "fluxo-alheio", "sem-mcp", "ia-sem-inventario"},
}
ANCORAS = {r.ancora for r in REGRAS} | {"COPY"}


class Evals(unittest.TestCase):
    def test_casos(self):
        for skill, ids in EXIGIDOS.items():
            with self.subTest(skill=skill):
                ev = json.loads((RAIZ / "skills" / skill / "evals/cases.json").read_text(encoding="utf-8"))
                casos = {c["id"]: c for c in ev["cases"]}
                self.assertEqual(len(casos), len(ev["cases"]), "id repetido")
                faltam = ids - {i for i, c in casos.items() if c["type"] == "negative_control"}
                self.assertEqual(faltam, set(), f"negativos exigidos ausentes: {faltam}")
                for c in ev["cases"]:
                    self.assertTrue(c.get("input") and c.get("expected"), c["id"])
                    self.assertTrue(set(c.get("regras", [])) <= ANCORAS, f"{c['id']}: regra inexistente {c.get('regras')}")


if __name__ == "__main__":
    unittest.main()
