"""AT-001: as 4 skills no padrão ouro; copy sem qualificar a pessoa pela falta."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from padrao_ouro import RAIZ, SKILLS, checar_copy, checar_skill


class PadraoOuro(unittest.TestCase):
    def test_quatro_skills(self):
        self.assertEqual(sorted(p.name for p in (RAIZ / "skills").iterdir() if p.is_dir()), sorted(SKILLS))

    def test_cada_skill(self):
        for s in SKILLS:
            with self.subTest(skill=s):
                self.assertEqual(checar_skill(RAIZ / "skills" / s), [])

    def test_copy(self):
        for s in SKILLS:
            with self.subTest(skill=s):
                self.assertEqual(checar_copy(RAIZ / "skills" / s), [])

    def test_mutantes_reprovam(self):
        """Cada checagem morde: emoji, seção fora de ordem, autoria ausente, frase proibida, arquivo não citado."""
        with tempfile.TemporaryDirectory() as tmp:
            for nome, mutar, checagem in [
                ("emoji", lambda t: t.replace("## Quick start", "## Quick start \U0001F680", 1), checar_skill),
                ("ordem", lambda t: t.replace("## Examples", "## ExamplesX", 1).replace(
                    "## Quick start", "## Examples\n\n## Quick start", 1), checar_skill),
                ("autoria", lambda t: t.replace("Esta skill foi construída", "Skill feita", 1), checar_skill),
                ("proibida", lambda t: t + "\nVocê não precisa saber programar.\n", checar_copy),
            ]:
                with self.subTest(mutante=nome):
                    d = Path(tmp) / nome / "spec-make-define"
                    shutil.copytree(RAIZ / "skills" / "spec-make-define", d)
                    sk = d / "SKILL.md"
                    sk.write_text(mutar(sk.read_text(encoding="utf-8")), encoding="utf-8")
                    self.assertNotEqual(checagem(d), [], f"mutante {nome} passou")
            d = Path(tmp) / "orfao" / "spec-make-define"
            shutil.copytree(RAIZ / "skills" / "spec-make-define", d)
            (d / "references" / "SOBRA.md").write_text("x\n", encoding="utf-8")
            self.assertNotEqual(checar_skill(d), [], "arquivo não citado passou")


if __name__ == "__main__":
    unittest.main()
