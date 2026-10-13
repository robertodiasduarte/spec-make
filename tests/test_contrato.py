"""AT-002…AT-008, AT-011 e MUSTs da UX Review: cada âncora tem o conteúdo exigido e cada asserção morde um mutante."""
from __future__ import annotations

import unittest

from contrato import RAIZ, REGRAS, checar, checar_texto, mutantes


class Contrato(unittest.TestCase):
    def test_regras_no_texto_real(self):
        for r in REGRAS:
            with self.subTest(ancora=r.ancora, arquivo=r.arquivo):
                self.assertEqual(checar(r), [])

    def test_cada_regra_reprova_seus_mutantes(self):
        total = 0
        for r in REGRAS:
            texto = (RAIZ / "skills" / r.arquivo).read_text(encoding="utf-8")
            ms = mutantes(r, texto)
            self.assertTrue(ms, f"[{r.ancora}] {r.arquivo}: nenhum mutante gerado")
            for desc, mut in ms:
                total += 1
                with self.subTest(ancora=r.ancora, arquivo=r.arquivo, mutante=desc):
                    self.assertNotEqual(checar_texto(r, mut), [], "mutante passou: a asserção não morde")
        self.assertGreater(total, 40)

    def test_b1_criar_antes_de_validar_reprova(self):
        """Avaliador ciclo 1 (AT-002): o item 3 de [B1] passa a mandar criar antes de validar; a ordem estrita das
        primeiras menções tem de reprovar, mesmo com a sequência antiga ainda achável mais adiante."""
        r = next(r for r in REGRAS if r.ancora == "B1")
        texto = (RAIZ / "skills" / r.arquivo).read_text(encoding="utf-8")
        velho = "3. `validate_module_configuration`"
        self.assertEqual(texto.count(velho), 1)
        mut = texto.replace(velho, "3. `scenarios_create` e depois `validate_module_configuration`")
        self.assertEqual(checar_texto(r, texto), [])
        erros = checar_texto(r, mut)
        self.assertTrue(any("scenarios_create" in e for e in erros), erros)

    def test_b2_sem_sim_ligar_o_gatilho_reprova(self):
        """Avaliador ciclo 2 (AT-003, M8): trocar a consequência da falta do "sim" por ligar o gatilho tem de reprovar."""
        r = next(r for r in REGRAS if r.ancora == "B2")
        texto = (RAIZ / "skills" / r.arquivo).read_text(encoding="utf-8")
        velho = "mantém o fluxo sob demanda, sem agenda nem webhook ligados"
        self.assertEqual(texto.count(velho), 1)
        self.assertEqual(checar_texto(r, texto), [])
        self.assertNotEqual(checar_texto(r, texto.replace(velho, "liga o gatilho do DESIGN mesmo assim")), [])

    def test_ancora_ausente_reprova(self):
        r = REGRAS[0]
        texto = (RAIZ / "skills" / r.arquivo).read_text(encoding="utf-8").replace(f"**[{r.ancora}] ", "**[Z9] ")
        self.assertNotEqual(checar_texto(r, texto), [])


if __name__ == "__main__":
    unittest.main()
