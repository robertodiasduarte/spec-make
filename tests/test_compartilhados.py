"""Decision 1: as cópias de compartilhado/ nas skills são idênticas à fonte."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("sync", RAIZ / "scripts" / "sync-compartilhados.py")
sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sync)  # type: ignore[union-attr]


class Compartilhados(unittest.TestCase):
    def test_copias_identicas(self):
        pares = sync.pares()
        self.assertEqual(len(pares), 14)
        for origem, destino in pares:
            with self.subTest(destino=str(destino.relative_to(RAIZ))):
                self.assertTrue(destino.is_file())
                self.assertEqual(destino.read_bytes(), origem.read_bytes())


if __name__ == "__main__":
    unittest.main()
