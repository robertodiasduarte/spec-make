"""AT-002…AT-008, AT-011 e MUSTs da UX Review: cada âncora tem o conteúdo exigido e cada asserção morde um mutante."""
from __future__ import annotations

import unittest

from contrato import FRASES, RAIZ, REGRAS, checar, checar_frases, checar_texto, jargao, mutantes


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
        h = "spec-make-handoff/SKILL.md"
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
            # SPEC_MAKE_HANDOFF (s3): H2, B6 (as 2 polaridades) e M1 do handoff
            (h, "Nunca chame `scenarios_create`", "Pode chamar `scenarios_create`"),
            (b, 'siga só depois do "sim" da pessoa', 'siga mesmo sem o "sim" da pessoa'),
            (b, "Depois releia `data-stores_list` e `hooks_list` e recalcule a custódia",
             "Não precisa reler `data-stores_list` e `hooks_list` nem recalcular a custódia"),
            (h, "Não afirme `lastEdit`", "Afirme `lastEdit`"),
        ]
        for arq, de, para in casos:
            with self.subTest(arquivo=arq, de=de[:40]):
                texto = (RAIZ / "skills" / arq).read_text(encoding="utf-8")
                self.assertEqual(texto.count(de), 1, "trecho do mutante não achado no texto real")
                mut = texto.replace(de, para)
                erros = [e for r in REGRAS if r.arquivo == arq for e in checar_texto(r, mut)]
                self.assertTrue(erros, "regra invertida passou")

    def test_handoff_sem_jargao(self):
        """AT-007 (R5 da review do DESIGN do s3): "transversal" e "Etapa 5" fora do frontmatter de todo .md do handoff
        reprovam; o frontmatter (metadata.fase) não conta."""
        pasta = RAIZ / "skills" / "spec-make-handoff"
        for arq in sorted(pasta.rglob("*.md")):
            with self.subTest(arquivo=arq.relative_to(pasta).as_posix()):
                self.assertEqual(jargao(arq.read_text(encoding="utf-8")), [])
        sk = (pasta / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn('fase: "transversal"', sk)
        self.assertTrue(jargao(sk.replace("## Quick start", "## Quick start\n\nEsta skill é transversal.", 1)))
        self.assertTrue(jargao(sk + "\nspec-make · Etapa 5 de 5 — Handoff\n"))

    def test_frases_dos_arquivos_de_referencia(self):
        for arq in FRASES:
            with self.subTest(arquivo=arq):
                self.assertEqual(checar_frases(arq, (RAIZ / "skills" / arq).read_text(encoding="utf-8")), [])

    def test_regra_invertida_nos_arquivos_de_referencia_reprova(self):
        """Avaliador ciclo 4 (achado 2): as 8 inversões de 1 edição nos arquivos de referência."""
        g, pr = "spec-make-design/references/GOVERNANCA_DO_FLUXO.md", "spec-make-design/references/PROMPTS_DE_IA.md"
        v = "spec-make-define/references/VERIFY_GATE_EXECUCAO.md"
        casos = [(g, "**Sem o passo:** recuse o DESIGN", "**Sem o passo:** aceite o DESIGN"),
                 (g, "**Sem a chave:** recuse o DESIGN como pronto e peça a chave.", "**Sem a chave:** aceite o DESIGN como pronto."),
                 (pr, "| versão | v1 |\n", ""),
                 (v, '"O blueprint foi validado" como teste: recuse', '"O blueprint foi validado" como teste: aceite'),
                 (v, "Fluxo que grava sem a segunda execução: recuse como incompleto.",
                  "Fluxo que grava sem a segunda execução: aceite como completo."),
                 (v, "sem dado pessoal real; origem", "pode usar dado real de cliente; origem"),
                 ("spec-make-build/references/PROTOCOLO.md", "a contagem não pode mudar", "a contagem pode mudar"),
                 ("spec-make-build/references/DIAGNOSTICO.md", "Correções só no fluxo que esta conversa criou ([B4]).",
                  "Correções em qualquer fluxo da conta."),
                 ("spec-make-handoff/references/PROTOCOLO.md", "Nunca troque o `lastEdit` da ficha",
                  "Troque o `lastEdit` da ficha"),
                 ("spec-make-handoff/references/PROTOCOLO.md", "a ficha mantém o `lastEdit` antigo",
                  "a ficha passa a ter o `lastEdit` da conta")]
        for arq, de, para in casos:
            with self.subTest(arquivo=arq, de=de[:40]):
                texto = (RAIZ / "skills" / arq).read_text(encoding="utf-8")
                self.assertEqual(texto.count(de), 1, "trecho do mutante não achado no texto real")
                self.assertTrue(checar_frases(arq, texto.replace(de, para)), "regra invertida passou")

    def test_ancora_ausente_reprova(self):
        r = REGRAS[0]
        texto = (RAIZ / "skills" / r.arquivo).read_text(encoding="utf-8").replace(f"**[{r.ancora}] ", "**[Z9] ")
        self.assertNotEqual(checar_texto(r, texto), [])


if __name__ == "__main__":
    unittest.main()
