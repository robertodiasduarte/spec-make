"""AT-004/AT-009 (SPEC_MAKE_HANDOFF): o verificador da ficha aprova o exemplo e a mesma ficha gerada sem o conector, e
reprova cada problema — 13 mutantes em memória, nunca em disco (LM-146). Os dígitos longos são montados em tempo de
execução: um literal de 11 dígitos reprovaria o publish-check (LM-058)."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SCRIPT = RAIZ / "skills" / "spec-make-handoff" / "scripts" / "checar_handoff.py"
_spec = importlib.util.spec_from_file_location("checar_handoff", SCRIPT)
ch = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ch)  # type: ignore[union-attr]
EXEMPLO = (RAIZ / "skills" / "spec-make-handoff" / "assets" / "HANDOFF_EXEMPLO.md").read_text(encoding="utf-8")


def sem_conector(texto: str) -> str:
    """A mesma ficha gerada sem o conector: linha Gerada dizendo isso e id/estado/custódia a confirmar na conta."""
    saida = []
    for linha in texto.splitlines():
        if linha.startswith("| Gerada |"):
            linha = "| Gerada | sem o conector do Make: os estados abaixo estão a confirmar na conta |"
        elif ch.LINHA_INV.match(linha):
            celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
            linha = f"| {celulas[0]} | {ch.A_CONFIRMAR} | {celulas[2]} | {ch.A_CONFIRMAR} | {ch.A_CONFIRMAR} |"
        saida.append(linha)
    return "\n".join(saida) + "\n"


MUTANTES = [
    ("placeholder", lambda t: t.replace("## Feito\n", "## Feito\n\n- {o que foi feito}\n", 1), "placeholder sobrando"),
    ("webhook", lambda t: t + "\nURL: https://hook.us2.make.com/" + "a" * 32 + "\n", "URL de webhook"),
    ("digitos", lambda t: t + "\nCNPJ " + "1" * 11 + "\n", "11+ dígitos"),
    ("sem-id", lambda t: t.replace("| Webhook | 2900101 |", "| Webhook | — |", 1), "sem id numérico"),
    ("secao", lambda t: t.replace("## Prompt de retomada", "## Prompt", 1), "seção ausente"),
    ("sem-conector-afirma", lambda t: sem_conector(t).replace(f"| {ch.A_CONFIRMAR} |\n", "| desta família |\n", 1),
     "sem o conector afirma"),
    ("com-conector-a-confirmar", lambda t: t.replace("| Webhook | 2900101 |", f"| Webhook | {ch.A_CONFIRMAR} |", 1),
     "sem id numérico"),
    # review pós-build, rodada 1b (R1/R4@opus, A1@codex)
    ("placeholder-digito", lambda t: t.replace("Onde paramos:", "Onde paramos: {2 ou 3 linhas}.", 1), "placeholder sobrando"),
    ("placeholder-reticencias", lambda t: t.replace("## Feito\n", "## Feito\n\n- {…}\n", 1), "placeholder sobrando"),
    ("rotulo-outra-caixa", lambda t: t.replace("| Data store | 170101 |", "| Data Store | — |", 1), "sem id numérico"),
    ("inventario-vazio", lambda t: "\n".join(l for l in t.splitlines() if not ch.LINHA_INV.match(l)) + "\n",
     "nenhum recurso listado"),
    ("sem-conector-contagem", lambda t: sem_conector(t).replace(
        '"Boletos – aprovação ERP" | a confirmar na conta', '"Boletos – aprovação ERP" | 5 registros', 1),
     "sem o conector afirma"),
    ("conexao-da-familia", lambda t: t.replace("ok · Gmail expira em 2027-04-13 | fora do spec-make |",
                                               "ok · Gmail expira em 2027-04-13 | desta família |", 1),
     "tem de ser 'fora do spec-make'"),
]


class ChecarHandoff(unittest.TestCase):
    def test_fichas_validas(self):
        self.assertEqual(ch.problemas(EXEMPLO), [])
        self.assertNotEqual(sem_conector(EXEMPLO), EXEMPLO)
        self.assertEqual(ch.problemas(sem_conector(EXEMPLO)), [])

    def test_cada_mutante_reprova_pela_sua_causa(self):
        for nome, mutar, causa in MUTANTES:
            with self.subTest(mutante=nome):
                texto = mutar(EXEMPLO)
                self.assertNotEqual(texto, EXEMPLO, "o mutante não mudou nada: o trecho-alvo sumiu do exemplo")
                erros = ch.problemas(texto)
                self.assertTrue(any(causa in e for e in erros), f"{nome}: esperado {causa!r}, veio {erros}")
        self.assertEqual(ch.problemas(EXEMPLO), [], "o mutante vazou para o real")

    def test_formula_do_make_nao_e_placeholder(self):
        self.assertEqual(ch.problemas(EXEMPLO.replace("## Feito\n", "## Feito\n\n- campo {{1.id}} mapeado\n", 1)), [])

    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok, ruim = Path(tmp) / "HANDOFF_OK.md", Path(tmp) / "HANDOFF_RUIM.md"
            ok.write_text(EXEMPLO, encoding="utf-8")
            ruim.write_text(MUTANTES[1][1](EXEMPLO), encoding="utf-8")
            roda = lambda *a: subprocess.run([sys.executable, "-I", str(SCRIPT), *a], capture_output=True, text=True)
            self.assertEqual(roda(str(ok)).returncode, 0)
            r = roda(str(ruim))
            self.assertEqual(r.returncode, 1)
            self.assertIn("URL de webhook", r.stdout)
            self.assertEqual(roda(str(Path(tmp) / "nao-existe.md")).returncode, 2)
            self.assertEqual(roda().returncode, 2)


    def test_s6_severidade_de_cada_mutante(self):
        """SPEC_MAKE_S6 AT-007: webhook e 11+ dígitos são ERRO (exit 1); o resto é AVISO (exit 3); a seção
        `## Alertas aceitos` é aceita. Severidade conferida pelo classificar e pela linha de comando."""
        erro = {"webhook", "digitos"}
        with tempfile.TemporaryDirectory() as tmp:
            for nome, mutar, _causa in MUTANTES:
                with self.subTest(mutante=nome):
                    erros, avisos = ch.classificar(mutar(EXEMPLO))
                    if nome in erro:
                        self.assertNotEqual(erros, [], f"{nome}: devia ser ERRO")
                    else:
                        self.assertEqual(erros, [], f"{nome}: virou ERRO")
                        self.assertNotEqual(avisos, [], f"{nome}: sem AVISO")
                    arq = Path(tmp) / f"HANDOFF_{nome}.md"
                    arq.write_text(mutar(EXEMPLO), encoding="utf-8")
                    r = subprocess.run([sys.executable, "-I", str(SCRIPT), str(arq)], capture_output=True, text=True)
                    self.assertEqual(r.returncode, 1 if nome in erro else 3, r.stdout)
        self.assertIn("## Alertas aceitos", EXEMPLO)
        self.assertEqual(ch.problemas(EXEMPLO), [])

if __name__ == "__main__":
    unittest.main()
