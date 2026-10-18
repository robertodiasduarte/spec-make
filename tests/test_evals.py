"""Casos de eval: formato, regras citadas existentes, os negativos exigidos pelo DEFINE (AT-006, AT-007, AT-008, AT-011)
e a ligação de cada negativo à âncora que o recusa, com mutantes (SPEC_MAKE s2, AT-004/AT-005)."""
from __future__ import annotations

import copy
import json
import unittest
from unittest import mock
from pathlib import Path

from contrato import REGRAS
import evals
import subprocess

from evals import ESPERADO, POSITIVOS, problemas, problemas_expected, problemas_positivos

RAIZ = Path(__file__).resolve().parents[1]
EXIGIDOS = {
    "spec-make-brainstorm": {"sem-mcp"},
    "spec-make-define": {"gate-uma-execucao", "gate-blueprint-validado", "sem-mcp"},
    "spec-make-design": {"sem-chave-natural", "ia-grava-direto", "aceite-sem-registro", "ia-sem-inventario", "sem-mcp"},
    "spec-make-build": {"sem-sim-gatilho", "falha-3x", "fluxo-alheio", "sem-mcp", "ia-sem-inventario",
                        "apaga-compartilhado", "lastedit-mudou", "uso-novo-externo"},
    "spec-make-handoff": {"placeholder-sobrando", "webhook-na-ficha", "sem-mcp", "arquivo-por-slice",
                          "primeira-ficha-sem-partes"},
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


    def test_mapa_caso_ancora(self):
        """Cada negativo exigido aponta EXATAMENTE a âncora que o recusa, e ela tem regra na mesma skill."""
        self.assertEqual(set(ESPERADO), set(EXIGIDOS))
        for skill, ids in EXIGIDOS.items():
            with self.subTest(skill=skill):
                self.assertEqual(ids - set(ESPERADO[skill]), set(), "negativo exigido fora do mapa")
        self.assertEqual(problemas(_reais()), [])

    def test_mapa_reprova_mutantes(self):
        """Avaliador ciclo 7 (5 mutantes) + vazia + âncora acrescida: cada mutante derruba o SEU caso, em memória."""
        real = _reais()
        mutantes = [("spec-make-design", "aceite-sem-registro", ["G3"]),        # outra âncora válida (INV-049)
                    ("spec-make-design", "aceite-sem-registro", None),
                    ("spec-make-design", "sem-chave-natural", None),
                    ("spec-make-define", "gate-uma-execucao", None),
                    ("spec-make-build", "sem-mcp", None),
                    ("spec-make-design", "ia-grava-direto", []),
                    ("spec-make-design", "aceite-sem-registro", ["G2", "G3"]),
                    # SPEC_MAKE_HANDOFF (s3): outra âncora válida da mesma skill · negativo da build removido ·
                    # âncora de OUTRA skill (B6 vive na build, não no handoff)
                    ("spec-make-handoff", "placeholder-sobrando", ["H3"]),
                    ("spec-make-build", "apaga-compartilhado", None),
                    ("spec-make-handoff", "webhook-na-ficha", ["B6"])]
        for skill, cid, regras in mutantes:
            with self.subTest(skill=skill, caso=cid, regras=regras):
                ev = copy.deepcopy(real)
                caso = next(c for c in ev[skill]["cases"] if c["id"] == cid)
                if regras is None:
                    del caso["regras"]
                else:
                    caso["regras"] = regras
                erros = problemas(ev)
                self.assertTrue(any(e.startswith(f"{skill}/{cid}:") for e in erros), f"mutante passou: {erros}")
        self.assertEqual(problemas(real), [], "o mutante vazou para o real")
        ev = copy.deepcopy(real)
        caso = next(c for c in ev["spec-make-design"]["cases"] if c["id"] == "aceite-sem-registro")
        ev["spec-make-design"]["cases"].insert(0, dict(caso, regras=["G3"]))   # 1º com âncora errada, 2º certo
        self.assertIn("spec-make-design/aceite-sem-registro: id repetido em cases.json", problemas(ev))

    def test_ancora_da_mesma_skill_reprova_mutantes(self):
        """Contrato C2 #4: mutantes que SÓ a regra "âncora com regra na mesma skill" pega (oráculo e caso mudam juntos)."""
        real = _reais()
        ev = copy.deepcopy(real)
        next(c for c in ev["spec-make-design"]["cases"] if c["id"] == "aceite-sem-registro")["regras"] = ["B2"]
        with mock.patch.dict(evals.ESPERADO["spec-make-design"], {"aceite-sem-registro": {"B2"}}):
            erros = problemas(ev)
        self.assertIn("spec-make-design/aceite-sem-registro: âncora B2 sem regra em spec-make-design", erros)
        ler = Path.read_text
        sem_frase = lambda self, *a, **k: (ler(self, *a, **k).replace("Frases proibidas:", "Frases:")
                                           if self.name == "COPY.md" and "spec-make-brainstorm" in self.parts else ler(self, *a, **k))
        with mock.patch.object(Path, "read_text", sem_frase):
            problemas(real)      # o ramo COPY de ancora_da_skill segue vivo (S7: nenhum caso o usa mais)
        ev = copy.deepcopy(real)
        next(c for c in ev["spec-make-brainstorm"]["cases"] if c["id"] == "chave-no-chat")["regras"] = ["B2"]
        with mock.patch.dict(evals.ESPERADO["spec-make-brainstorm"], {"chave-no-chat": {"B2"}}):
            erros = problemas(ev)
        self.assertIn("spec-make-brainstorm/chave-no-chat: âncora B2 sem regra em spec-make-brainstorm", erros)
        self.assertEqual(problemas(real), [])

    def test_positivo_do_handoff(self):
        """AT-010: o positivo `handoff-boletos` cita H1, H2 e H3 — oráculo separado do mapa dos negativos. SPEC_MAKE_S5:
        + o positivo `design-supabase` (S1–S5, W1) e 14 negativos (12 do design, 2 do build) ⇒ 37."""
        self.assertEqual(POSITIVOS, {"spec-make-handoff": {"handoff-boletos": {"H1", "H2", "H3"}},
                                     "spec-make-design": {"design-supabase": {"S1", "S2", "S3", "S4", "S5", "W1"}},
                                     "spec-make-brainstorm": {"amostra-pessoal": {"F1"}, "extrato-real": {"F1", "F2"}}})
        self.assertEqual(sum(len(v) for v in ESPERADO.values()), 38)   # S6: + http-com-nativo (N1); S7: amostra-pessoal sai, chave-no-chat entra
        self.assertEqual(problemas_positivos(_reais()), [])

    def test_positivo_reprova_mutantes(self):
        """Avaliador fresco do s3, ciclo 2 (EV4): `regras` do positivo sem H2, trocada, acrescida, repetida, vazia ou
        removida; o caso virando negativo; o caso removido; o caso duplicado — cada um derruba `handoff-boletos`."""
        real = _reais()
        cid, sk = "handoff-boletos", "spec-make-handoff"

        def com(fn):
            ev = copy.deepcopy(real)
            fn(ev[sk]["cases"], next(c for c in ev[sk]["cases"] if c["id"] == cid))
            return problemas_positivos(ev)

        mutantes = {
            "EV4 sem H2": lambda cs, c: c.__setitem__("regras", ["H1", "H3"]),
            "H2 trocada por H4": lambda cs, c: c.__setitem__("regras", ["H1", "H4", "H3"]),
            "M1 acrescida": lambda cs, c: c.__setitem__("regras", ["H1", "H2", "H3", "M1"]),
            "H2 repetida": lambda cs, c: c.__setitem__("regras", ["H1", "H2", "H2", "H3"]),
            "regras vazia": lambda cs, c: c.__setitem__("regras", []),
            "regras removida": lambda cs, c: c.pop("regras"),
            "virou negativo": lambda cs, c: c.__setitem__("type", "negative_control"),
            "caso removido": lambda cs, c: cs.remove(c),
            "caso duplicado com H1 só": lambda cs, c: cs.insert(0, dict(c, regras=["H1"])),
            "item que não é texto": lambda cs, c: c.__setitem__("regras", ["H1", {}, "H3"]),   # A1@codex r3b: era TypeError
        }
        for nome, fn in mutantes.items():
            with self.subTest(mutante=nome):
                erros = com(fn)
                self.assertTrue(any(e.startswith(f"{sk}/{cid}:") for e in erros), f"mutante passou: {erros}")
        self.assertEqual(problemas_positivos(real), [], "o mutante vazou para o real")
        # âncora de OUTRA skill: só a regra "âncora com regra na mesma skill" pega (oráculo e caso mudam juntos)
        ev = copy.deepcopy(real)
        next(c for c in ev[sk]["cases"] if c["id"] == cid)["regras"] = ["H1", "B6", "H3"]
        with mock.patch.dict(evals.POSITIVOS[sk], {cid: {"H1", "B6", "H3"}}):
            erros = problemas_positivos(ev)
        self.assertIn(f"{sk}/{cid}: âncora B6 sem regra em {sk}", erros)


    def test_s6_expected_dos_negativos(self):
        """Contrato C2 #1: convertidos esperam o alerta com "Seguir assim"; os de parada mantêm o expected da v1.4.0;
        `sem-mcp` do brainstorm cita os passos. Cada condição morde 1 mutante em memória."""
        real, base = _reais(), None      # o oráculo é a fotografia PARADA_V140 (release.yml: checkout raso, sem tags)
        self.assertEqual(problemas_expected(real, base), [])
        mut = copy.deepcopy(real)
        caso = next(c for c in mut["spec-make-design"]["cases"] if c["id"] == "sem-chave-natural")
        caso["expected"] = ["Recusa o DESIGN como pronto e pede a chave natural (ex.: chave de acesso da nota)"]   # o da v1.3.3
        self.assertTrue(any(e.startswith("spec-make-design/sem-chave-natural:") for e in problemas_expected(mut, base)))
        mut = copy.deepcopy(real)
        next(c for c in mut["spec-make-build"]["cases"] if c["id"] == "fluxo-alheio")["expected"] = ["Altera o fluxo com alerta"]
        self.assertTrue(any(e.startswith("spec-make-build/fluxo-alheio:") for e in problemas_expected(mut, base)))
        mut = copy.deepcopy(real)
        next(c for c in mut["spec-make-brainstorm"]["cases"] if c["id"] == "sem-mcp")["expected"] = ["Avisa"]
        self.assertTrue(any(e.startswith("spec-make-brainstorm/sem-mcp:") for e in problemas_expected(mut, base)))
        # rodada 1c: fonte-sem-consulta (W1) de volta a recusar; gatilho-webhook-no-design virando alerta
        mut = copy.deepcopy(real)
        next(c for c in mut["spec-make-design"]["cases"] if c["id"] == "fonte-sem-consulta")["expected"] = ["Recusa o DESIGN"]
        self.assertTrue(any(e.startswith("spec-make-design/fonte-sem-consulta:") for e in problemas_expected(mut, base)))
        mut = copy.deepcopy(real)
        next(c for c in mut["spec-make-build"]["cases"] if c["id"] == "gatilho-webhook-no-design")["expected"] = [
            "Alerta [A1]; segue com Seguir assim"]
        self.assertTrue(any(e.startswith("spec-make-build/gatilho-webhook-no-design:") for e in problemas_expected(mut, base)))


    def test_s6_fotografia_da_v133_bate_com_a_tag(self):
        """A fotografia PARADA_V140 é a cópia fiel da tag v1.4.0; sem a tag (checkout raso do release.yml), pula."""
        try:
            base = _base("v1.4.0")
        except AssertionError as e:
            self.skipTest(str(e))
        for chave, esperado in evals.PARADA_V140.items():
            skill, cid = chave.split("/", 1)
            with self.subTest(caso=chave):
                c = next(c for c in base[skill]["cases"] if c["id"] == cid)
                self.assertEqual(c["expected"], esperado)


def _base(tag: str) -> dict:
    """cases.json de cada skill na tag (git show): o oráculo dos negativos de parada."""
    saida = {}
    for s in ESPERADO:
        r = subprocess.run(["git", "-C", str(RAIZ), "show", f"{tag}:skills/{s}/evals/cases.json"], capture_output=True, text=True)
        if r.returncode != 0:
            raise AssertionError(f"tag {tag} ausente no repo (git fetch --tags): {r.stderr.strip()}")
        saida[s] = json.loads(r.stdout)
    return saida


def _reais() -> dict:
    return {s: json.loads((RAIZ / "skills" / s / "evals/cases.json").read_text(encoding="utf-8")) for s in ESPERADO}


if __name__ == "__main__":
    unittest.main()
