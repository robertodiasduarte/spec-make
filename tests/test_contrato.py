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

    def test_regra_invertida_reprova(self):
        """Avaliador ciclo 3 (achado 2): inverter a regra com 1 edição (o "nunca", o "não", o "pare", o número do teto)
        tem de reprovar — Decision 2: grep de palavra solta passa com a regra invertida."""
        b, p, d = "spec-make-build/SKILL.md", "spec-make-build/references/PROTOCOLO.md", \
            "spec-make-build/references/DIAGNOSTICO.md"
        ds, df = "spec-make-design/SKILL.md", "spec-make-define/SKILL.md"
        casos = [
            (b, "Nunca chame `scenarios_update`", "Pode chamar `scenarios_update`"),
            (b, 'ou ligue o gatilho real depois de a pessoa responder "Ligar agora" ou "sim"',
             'ou ligue o gatilho real; depois de a pessoa responder "Ligar agora" ou "sim"'),
            (d, "pare: não corrija nem rode de novo", "continue: corrija e rode de novo"),
            (d, "o teste roda no máximo 4 vezes", "o teste roda no máximo 9 vezes"),
            (p, "7. `scenarios_activate` — necessário para rodar; sob demanda, ele só roda quando alguém pede.\n", ""),
            (p, "Nunca peça chave no chat.", "Peça a chave no chat."),
            (b, "O fluxo é criado com `metadata.scenario.confidential: true`.",
             "O fluxo é criado com `metadata.scenario.confidential: false` (não `confidential: true`)."),
            (ds, "Sem a chave, recuse o\nDESIGN como pronto e peça a chave.",
             "Sem a chave, não recuse o\nDESIGN como pronto e não peça a chave."),
            (ds, "Sem esse passo,\nrecuse o DESIGN como pronto", "Sem esse passo,\nnão recuse o DESIGN como pronto"),
            (df, "Recuse como incompleto o teste", "Não Recuse como incompleto o teste"),
            (b, "pare antes do `scenarios_create`, diga", "não pare antes do `scenarios_create`, diga"),
            # rodada 6 (R2/R3@opus): G2, P1 do design e M1 das etapas de papel
            (ds, "Sem esse registro, recuse o DESIGN", "Sem esse registro, não recuse o DESIGN"),
            (ds, "sem esse inventário: recuse o DESIGN", "sem esse inventário: não recuse o DESIGN"),
            (ds, "e não declare o blueprint validado", "e declare o blueprint validado"),
            (df, 'ficam "a confirmar na conta" se', 'ficam "a confirmar na conta" mesmo se'),
            ("spec-make-brainstorm/SKILL.md", "Não afirme\nque um app existe", "Afirme\nque um app existe"),
            (b, "Não afirme que criou, rodou ou ligou nada.",
             "Diga que criou e rodou. (Não afirme que criou, rodou ou ligou nada só se pedirem.)"),
        ]
        for arq, de, para in casos:
            with self.subTest(arquivo=arq, de=de[:40]):
                texto = (RAIZ / "skills" / arq).read_text(encoding="utf-8")
                self.assertEqual(texto.count(de), 1, "trecho do mutante não achado no texto real")
                mut = texto.replace(de, para)
                erros = [e for r in REGRAS if r.arquivo == arq for e in checar_texto(r, mut)]
                self.assertTrue(erros, "regra invertida passou")

    def test_ancora_ausente_reprova(self):
        r = REGRAS[0]
        texto = (RAIZ / "skills" / r.arquivo).read_text(encoding="utf-8").replace(f"**[{r.ancora}] ", "**[Z9] ")
        self.assertNotEqual(checar_texto(r, texto), [])


if __name__ == "__main__":
    unittest.main()
