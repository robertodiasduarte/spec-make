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


SEGREDO = "abcd1234efgh5678ijkl"
APP_KEY = "1234567" + "890123"  # 13 dígitos montados em pedaços (publish-check reprova 11+ seguidos)


def _com_http(mapper: dict) -> dict:
    """blueprint_valido.json com 1 módulo http:ActionSendData a mais, com a credencial no mapper (achado AT-005)."""
    bp = _ler("blueprint_valido.json")
    bp["flow"].insert(2, {"id": 4, "module": "http:ActionSendData", "version": 3, "parameters": {},
                          "mapper": {"method": "post", "url": "https://api.exemplo.com/v1", **mapper},
                          "metadata": {"designer": {"x": 450, "y": 0}}})
    return bp


def _com_datastore(chave: str) -> dict:
    bp = _ler("blueprint_valido.json")
    bp["flow"].insert(2, {"id": 5, "module": "datastore:AddRecord", "version": 1, "parameters": {"datastore": 12345},
                          "mapper": {"key": chave, "data": {"cnpj": "{{2.cnpj}}"}, "overwrite": True},
                          "metadata": {"designer": {"x": 450, "y": 0}}})
    return bp


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

    def test_credencial_em_corpo_objeto(self):
        """Avaliador ciclo 1 (AT-005): app_key/app_secret no corpo (data como objeto)."""
        corpo = {"call": "ListarClientes", "app_key": APP_KEY, "app_secret": SEGREDO}
        self.assertTrue(any("credencial" in p for p in cb.checar(_com_http({"bodyType": "raw", "data": corpo}))))

    def test_credencial_em_corpo_texto_json(self):
        """O mesmo corpo escrito como texto JSON (bodyType raw)."""
        corpo = json.dumps({"call": "ListarClientes", "app_key": APP_KEY, "app_secret": SEGREDO})
        self.assertTrue(any("credencial" in p for p in cb.checar(_com_http({"bodyType": "raw", "data": corpo}))))

    def test_access_key_na_url(self):
        bp = _com_http({"url": "https://api.exemplo.com/v1?access_key=" + SEGREDO})
        self.assertTrue(any("credencial" in p for p in cb.checar(bp)))

    def test_client_secret_na_url(self):
        bp = _com_http({"url": "https://api.exemplo.com/v1?client_secret=" + SEGREDO})
        self.assertTrue(any("credencial" in p for p in cb.checar(bp)))

    def test_usuario_e_senha_na_url(self):
        bp = _com_http({"url": "https://usuario:" + SEGREDO + "@api.exemplo.com/v1"})
        self.assertTrue(any("credencial" in p for p in cb.checar(bp)))

    def test_cabecalho_subscription_key(self):
        bp = _com_http({"headers": [{"name": "Ocp-Apim-Subscription-Key", "value": SEGREDO}]})
        self.assertTrue(any("credencial" in p for p in cb.checar(bp)))

    def test_key_do_data_store_nao_e_credencial(self):
        """O nome exato "key" é a chave do registro no data store, mapeada ou fixa: não é credencial."""
        for chave in ["{{2.cnpj}}", "clientes"]:
            with self.subTest(chave=chave):
                self.assertEqual(cb.checar(_com_datastore(chave)), [])

    def test_rodada_3b(self):
        """A1/A2 do auditor e R2/R3 do opus (rodada 3b)."""
        casos = {
            "A1: 2 objetos com password no corpo texto": {"body": '{"a":{"password":"Segredo123"},"b":{"password":""},"n":{{1.n}}}'},
            "A2: password com valor https": {"password": "https://segredo.exemplo/abc123"},
            "R2: authPass literal": {"authUser": "escritorio", "authPass": "S3nhaFixa2026"},
            "R3: qs name=key": {"qs": [{"name": "key", "value": "AIzaSyD" + "x" * 20}]},
            "R3: cabeçalho name=key": {"headers": [{"name": "key", "value": "abcd1234efgh5678"}]},
        }
        for nome, campo in casos.items():
            with self.subTest(caso=nome):
                bp = _ler("blueprint_valido.json")
                bp["flow"][1]["mapper"].update(campo)
                self.assertTrue(any("credencial" in p for p in cb.checar(bp)), nome)
        for nome, campo in {"token_url com https": {"token_url": "https://auth.exemplo/oauth/token"},
                            "token_type Bearer": {"token_type": "Bearer"},
                            "Authorization Bearer mapeado": {"headers": [{"name": "Authorization", "value": "Bearer {{1.access_token}}"}]},
                            "qs name=key mapeado": {"qs": [{"name": "key", "value": "{{3.chave}}"}]}}.items():
            with self.subTest(caso=nome):
                bp = _ler("blueprint_valido.json")
                bp["flow"][1]["mapper"].update(campo)
                self.assertEqual(cb.checar(bp), [], nome)

    def test_rodada_4(self):
        """R4/R5@opus (rodada 4): 'key' no corpo texto vale igual lido ou não como JSON; endereço por palavra."""
        chave = "AIzaSyD" + "x" * 20
        for nome, campo in {"corpo JSON legível com key": {"body": '{"key":"' + chave + '"}'},
                            "corpo com mapeamento e key": {"body": '{"key":"' + chave + '","n":{{1.n}}}'},
                            "security_password https": {"security_password": "https://segredo.exemplo/abc123"},
                            "securityToken https": {"securityToken": "https://segredo.exemplo/abc123"}}.items():
            with self.subTest(caso=nome):
                bp = _ler("blueprint_valido.json")
                bp["flow"][1]["mapper"].update(campo)
                self.assertTrue(any("credencial" in p for p in cb.checar(bp)), nome)
        for nome, campo in {"token_url https": {"token_url": "https://auth.exemplo/oauth/token"},
                            "authorizationEndpoint https": {"authorizationEndpoint": "https://auth.exemplo/authorize"},
                            "corpo com key mapeado": {"body": '{"key":"{{2.cnpj}}"}'}}.items():
            with self.subTest(caso=nome):
                bp = _ler("blueprint_valido.json")
                bp["flow"][1]["mapper"].update(campo)
                self.assertEqual(cb.checar(bp), [], nome)

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
