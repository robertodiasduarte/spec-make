"""AT-005: o verificador reprova blueprint sem confidential, com a chave interface (o Make recusa), com o módulo de
entrada sem campos ou com credencial; aprova o válido."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FIX = Path(__file__).resolve().parent / "fixtures"
SCRIPT = RAIZ / "compartilhado" / "checar_blueprint.py"

_spec = importlib.util.spec_from_file_location("checar_blueprint", SCRIPT)
cb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cb)  # type: ignore[union-attr]


def _ler(nome: str) -> dict:
    return json.loads((FIX / nome).read_text(encoding="utf-8"))


class ChecarBlueprint(unittest.TestCase):
    def test_valido_passa(self):
        self.assertEqual(cb.checar(_ler("blueprint_valido.json")), [])

    def test_exemplo_da_skill_passa(self):
        ex = json.loads((RAIZ / "skills/spec-make-design/assets/blueprint-minimo.json").read_text(encoding="utf-8"))
        self.assertEqual(cb.checar(ex), [])

    def test_negativos(self):
        for nome, trecho in [("blueprint_sem_confidencial.json", "confidential"),
                             ("blueprint_interface_no_blueprint.json", "interface"),
                             ("blueprint_entrada_sem_campos.json", "metadata.interface"),
                             ("blueprint_com_credencial.json", "credencial"),
                             ("blueprint_header_bearer.json", "credencial"),
                             ("blueprint_chave_na_url.json", "credencial")]:
            with self.subTest(fixture=nome):
                probs = cb.checar(_ler(nome))
                self.assertEqual(len(probs), 1, probs)
                self.assertIn(trecho.split(".")[0], probs[0])

    def test_token_montado_em_pedacos(self):
        """Chave no formato sk- é pega (montada em tempo de execução para não cair no publish-check, LM-312)."""
        bp = _ler("blueprint_valido.json")
        bp["flow"][1]["mapper"]["token"] = "sk-" + "ab12" * 6
        self.assertTrue(any("credencial" in p for p in cb.checar(bp)))

    def test_mapeamento_do_make_nao_e_segredo(self):
        bp = _ler("blueprint_valido.json")
        bp["flow"][1]["mapper"]["apikey"] = "{{3.chave}}"
        bp["flow"][1]["mapper"]["headers"] = [{"name": "Authorization", "value": "Bearer {{4.token}}"},
                                              {"name": "Accept", "value": "application/json"}]
        self.assertEqual(cb.checar(bp), [])

    def test_chave_fixa_com_mapeamento_grudado(self):
        """A2 da review: {{…}} grudado numa chave fixa não a torna dinâmica."""
        for valor in ["segredo-fixo{{emptystring}}", "Bearer abcdef0123456789{{emptystring}}"]:
            with self.subTest(valor=valor):
                bp = _ler("blueprint_valido.json")
                bp["flow"][1]["mapper"]["headers"] = [{"name": "Authorization", "value": valor}]
                bp["flow"][1]["mapper"]["apikey"] = valor
                self.assertTrue(any("credencial" in p for p in cb.checar(bp)))

    def test_credencial_dentro_da_expressao(self):
        """R1@opus (rodada 2): token conhecido ou chave na URL escritos DENTRO de {{…}} continuam credencial."""
        for valor in ["Bearer {{ifempty(1.token; sk-" + "proj" + "A" * 20 + ")}}",
                      "{{trim(eyJ" + "hbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" + ".xxx)}}",
                      "{{ifempty(1.url; https://x.exemplo/?token=abcdefgh)}}"]:
            with self.subTest(valor=valor[:30]):
                bp = _ler("blueprint_valido.json")
                bp["flow"][1]["mapper"]["campo"] = valor
                self.assertTrue(any("credencial" in p for p in cb.checar(bp)))

    def test_modulo_dentro_de_rota_conta(self):
        bp = _ler("blueprint_entrada_sem_campos.json")
        entrada = bp["flow"].pop(0)
        bp["flow"].insert(0, {"id": 99, "module": "builtin:BasicRouter", "version": 1, "routes": [{"flow": [entrada]}]})
        self.assertTrue(any("interface" in p for p in cb.checar(bp)))

    def test_cli_codigos_de_saida(self):
        ok = subprocess.run([sys.executable, "-I", str(SCRIPT), str(FIX / "blueprint_valido.json")], capture_output=True)
        ruim = subprocess.run([sys.executable, "-I", str(SCRIPT), str(FIX / "blueprint_sem_confidencial.json")], capture_output=True)
        self.assertEqual((ok.returncode, ruim.returncode), (0, 1))

    def test_copias_nas_skills_sao_identicas(self):
        for s in ("spec-make-design", "spec-make-build"):
            with self.subTest(skill=s):
                self.assertEqual((RAIZ / "skills" / s / "scripts/checar_blueprint.py").read_bytes(), SCRIPT.read_bytes())


if __name__ == "__main__":
    unittest.main()
