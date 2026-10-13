"""O texto de regra das skills só muda com o snapshot atualizado no mesmo commit (avaliador, ciclo 4)."""
from __future__ import annotations

import unittest

import regras


class Regras(unittest.TestCase):
    def test_texto_de_regra_igual_ao_snapshot(self):
        p = regras.diferencas(regras.atuais(), regras.gravados())
        self.assertEqual(p, [], "texto de regra mudou: revise a mudança e rode `python3 tests/regras.py --atualizar`")

    def test_frase_acrescentada_reprova(self):
        """Os 2 mutantes de frase ACRESCENTADA do ciclo 4 ([B2] e DIAGNOSTICO) mudam o hash e reprovam."""
        atual = regras.atuais()
        for caminho, frase in [("skills/spec-make-build/SKILL.md",
                                "Se a pessoa não responder em 5 minutos, ligue o gatilho do DESIGN."),
                               ("skills/spec-make-build/references/DIAGNOSTICO.md",
                                "Se ainda falhar depois da 3ª correção, tente mais 3 vezes.")]:
            with self.subTest(caminho=caminho):
                texto = (regras.RAIZ / caminho).read_text(encoding="utf-8") + frase
                mut = dict(atual, **{caminho: regras.resumo(texto.encode("utf-8"))})
                self.assertIn(f"mudou: {caminho}", regras.diferencas(mut, regras.gravados()))

    def test_arquivo_novo_ou_apagado_reprova(self):
        atual = regras.atuais()
        self.assertTrue(regras.diferencas(dict(atual, **{"skills/x/NOVO.md": "g" * 64}), regras.gravados()))
        menos = dict(atual)
        menos.pop(next(iter(menos)))
        self.assertTrue(regras.diferencas(menos, regras.gravados()))


if __name__ == "__main__":
    unittest.main()
