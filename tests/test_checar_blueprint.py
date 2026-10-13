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

    def test_credencial_fixa_dentro_da_formula(self):
        """Avaliador ciclo 2 (AT-005): texto fixo DENTRO de {{…}} (entre aspas ou argumento sem aspas) é credencial
        escrita; referências, funções e palavras do Make continuam não sendo."""
        segredo = "abcd1234" + "efgh5678"
        for nome, campo in {
                "Basic base64 com aspas": {"headers": [{"name": "Authorization",
                                                        "value": 'Basic {{base64("contabil:MinhaSenha2026")}}'}]},
                "Basic base64 sem aspas": {"headers": [{"name": "Authorization",
                                                        "value": "Basic {{base64(contabil:MinhaSenha2026)}}"}]},
                "Bearer literal entre aspas": {"headers": [{"name": "Authorization",
                                                            "value": 'Bearer {{"' + segredo + '"}}'}]},
                "api_key literal entre aspas": {"data": {"api_key": '{{"' + segredo + '"}}'}},
                "api_key no ifempty": {"data": {"api_key": '{{ifempty(1.chave; "' + segredo + '")}}'}},
                "key na query por fórmula": {"url": 'https://api.exemplo.com/v1?key={{"' + segredo + '"}}'}}.items():
            with self.subTest(caso=nome):
                self.assertTrue(any("credencial" in p for p in cb.checar(_com_http(campo))), nome)
        for nome, campo in {
                "Bearer mapeado": {"headers": [{"name": "Authorization", "value": "Bearer {{4.token}}"}]},
                "Basic de campos mapeados": {"headers": [{"name": "Authorization",
                                                          "value": 'Basic {{base64(1.usuario + ":" + 1.senha)}}'}]},
                "ifempty com emptystring": {"data": {"api_key": "{{ifempty(1.chave; emptystring)}}"}},
                "variável do fluxo": {"data": {"token": "{{var.input.token}}"}},
                "campo com espaço": {"data": {"senha": "{{1.`Senha do portal`}}"}},
                "get com índice": {"data": {"apikey": "{{get(1.chaves; 1)}}"}},
                "key na query mapeada": {"url": "https://api.exemplo.com/v1?key={{1.chave}}"}}.items():
            with self.subTest(caso=nome):
                self.assertEqual(cb.checar(_com_http(campo)), [], nome)

    def test_rodada_5(self):
        """R1-R3@opus (rodada 5): referência só começa por número de módulo ou "var" e aceita acento; texto entre aspas
        comparado numa condição não é o valor do campo."""
        bp = _com_http({"headers": [{"name": "Authorization", "value": "Basic {{base64(joao:senha.2026)}}"}]})
        self.assertTrue(any("credencial" in p for p in cb.checar(bp)), "senha com ponto escrita à mão")
        for nome, campo in {
                "if com comparação": {"data": {"api_key": '{{if(1.ambiente = "producao"; 2.chave_producao; '
                                                          '2.chave_teste)}}'}},
                "comparação na query": {"url": 'https://api.exemplo.com/v1?key={{if(1.amb != "producao"; 2.k1; '
                                                '2.k2)}}'},
                "campo com acento": {"data": {"token": "{{3.códigoAcesso}}"}}}.items():
            with self.subTest(caso=nome):
                self.assertEqual(cb.checar(_com_http(campo)), [], nome)

    def test_avaliador_ciclo_3(self):
        """Avaliador ciclo 3 (AT-005): nomes de credencial em cabeçalho, query e corpo de formulário em texto."""
        v = "abcdef" + "123456"
        def hdr(nome):
            return {"headers": [{"name": nome, "value": v}]}
        for nome, campo in {"X-Auth-Key": hdr("X-Auth-Key"), "chave-api": hdr("chave-api"), "pwd": hdr("pwd"),
                            "chave": hdr("chave"), "pass": hdr("pass"),
                            "?pwd=": {"url": "https://api.x.com/v1?user=ana&pwd=" + v},
                            "?chave=": {"url": "https://api.x.com/v1?chave=" + v},
                            "form client_secret": {"data": "client_secret=" + v + "&grant_type=client_credentials"},
                            "form password no meio": {"data": "grant_type=password&username=ana&password=" + v},
                            "app_hash": {"data": {"app_hash": v}}}.items():
            with self.subTest(caso=nome):
                self.assertTrue(any("credencial" in p for p in cb.checar(_com_http(campo))), nome)
        for nome, campo in {"Content-Type": {"headers": [{"name": "Content-Type", "value": "application/json"}]},
                            "X-Tenant mapeado": {"headers": [{"name": "X-Auth-Key", "value": "{{1.chave}}"}]},
                            "form mapeado": {"data": "client_secret={{1.segredo}}&grant_type=client_credentials"},
                            "form sem credencial": {"data": "grant_type=client_credentials&scope=leitura"},
                            "?chave= mapeada": {"url": "https://api.x.com/v1?chave={{1.chave_nfe}}"},
                            # R4@opus/R2@kimi (rodada 6): nome que só termina em key ou começa por pass não é credencial
                            "?sort_key=": {"url": "https://api.x.com/v1/notas?sort_key=emissao"},
                            "?partitionKey=": {"url": "https://api.x.com/v1?partitionKey=clientes"},
                            "X-Pass-Through": {"headers": [{"name": "X-Pass-Through", "value": "enabled"}]}}.items():
            with self.subTest(caso=nome):
                self.assertEqual(cb.checar(_com_http(campo)), [], nome)

    def test_entrada_que_pede_credencial(self):
        """R1@opus (rodada 6): o campo de entrada com nome de credencial leva a chave pelo chat e pela execução."""
        bp = _ler("blueprint_valido.json")
        bp["flow"][0]["metadata"]["interface"].append({"name": "api_token", "type": "text"})
        self.assertTrue(any("credencial" in p and "entrada" in p for p in cb.checar(bp)))
        bp = _ler("blueprint_valido.json")
        bp["flow"][0]["metadata"]["interface"].append({"name": "chave_nfe", "type": "text"})
        self.assertEqual(cb.checar(bp), [])

    def test_avaliador_ciclo_4(self):
        """Avaliador ciclo 4 (AT-005): formatos conhecidos em qualquer lugar e nomes que faltavam. Os tokens são montados
        em pedaços: o texto do teste não pode parecer credencial para o publish-check."""
        v = "abcdef" + "123456" + "XYZ"
        formatos = {"Stripe": "sk_" + "live_" + "a1B2c3D4e5F6g7H8", "Slack": "xo" + "xb-" + "1234567890-abcdefABCDEF",
                    "GitHub": "gh" + "p_" + "A" * 36, "Google": "AI" + "za" + "SyD" + "x1" * 16,
                    "Telegram": "https://api.telegram.org/bot" + "123456789:" + "AAH" + "x" * 32 + "/sendMessage",
                    "Slack webhook": "https://hooks.slack.com/" + "services/T0000AAAA/B0000BBBB/" + "c" * 24}
        casos = {}
        for nome, tok in formatos.items():
            casos[nome + " em X-Custom"] = {"headers": [{"name": "X-Custom", "value": tok}]}
            casos[nome + " no corpo texto"] = {"data": "mensagem: " + tok}
        casos["Telegram no caminho"] = {"url": formatos["Telegram"]}
        casos.update({"Cookie": {"headers": [{"name": "Cookie", "value": "sessionid=" + v}]},
                      "X-Auth": {"headers": [{"name": "X-Auth", "value": v}]},
                      "Credential": {"headers": [{"name": "Credential", "value": v}]},
                      "?access_code=": {"url": "https://api.x.com/v1?access_code=" + v},
                      "SetVariable credencial": {"variables": [{"name": "credencial", "value": v}]}})
        for nome, campo in casos.items():
            with self.subTest(caso=nome):
                self.assertTrue(any("credencial" in p for p in cb.checar(_com_http(campo))), nome)
        for nome, campo in {"X-Request-Id": {"headers": [{"name": "X-Request-Id", "value": v}]},
                            "Cookie mapeado": {"headers": [{"name": "Cookie", "value": "sessionid={{1.sessao}}"}]},
                            "Telegram mapeado": {"url": "https://api.telegram.org/bot{{1.token}}/sendMessage"},
                            "texto com 'bot'": {"data": "o robô (bot) respondeu ao cliente"}}.items():
            with self.subTest(caso=nome):
                self.assertEqual(cb.checar(_com_http(campo)), [], nome)

    def test_rodada_7(self):
        """R2@codex, R1/R2@opus (rodada 7): Cookie com literal sem "=" ou em fórmula reprova; formato conhecido no meio de
        identificador e "cookie" dentro de outro nome não são credencial."""
        v = "abcdef" + "123456" + "XYZ"
        for nome, campo in {"Cookie sem =": {"headers": [{"name": "Cookie", "value": v}]},
                            "Cookie em fórmula": {"headers": [{"name": "Cookie",
                                                               "value": '{{"sid=' + v + '"}}'}]}}.items():
            with self.subTest(caso=nome):
                self.assertTrue(any("credencial" in p for p in cb.checar(_com_http(campo))), nome)
        for nome, campo in {"rk_test_ no meio": {"headers": [{"name": "X-Ambiente", "value": "network_test_homologacao"}]},
                            "sk- no meio": {"url": "https://api.exemplo.com.br/v1/helpdesk-chamados-abertos"},
                            "X-Cookie-Consent": {"headers": [{"name": "X-Cookie-Consent", "value": "aceito-todos"}]},
                            "accept_cookies": {"url": "https://api.exemplo.com/v1?accept_cookies=sempre-aceitar"},
                            "shareCookies": {"shareCookies": False}}.items():
            with self.subTest(caso=nome):
                self.assertEqual(cb.checar(_com_http(campo)), [], nome)

    def test_avaliador_ciclo_5(self):
        """Avaliador ciclo 5 (AT-005): valor numérico com nome de credencial reprova; nome que só CONTÉM um marcador
        ("secretaria", "resenha", "max_tokens") e frase que começa por "Token" não são credencial."""
        # números longos montados em tempo de execução: o publish-check reprova 11+ dígitos seguidos no texto
        n11, n15, n13 = int("123456" + "78901"), int("9876543" + "21012345"), int("123456" + "7890123")
        for nome, campo in {"password numérico": {"password": n11},
                            "senha numérica no data": {"data": {"senha": 98765432}},
                            "X-API-KEY numérico": {"headers": [{"name": "X-API-KEY", "value": n15}]},
                            "qs token numérico": {"qs": [{"name": "token", "value": n11}]},
                            "app_key/app_secret numéricos": {"data": {"call": "ListarClientes", "app_key": n13,
                                                                      "app_secret": n13 + 7}},
                            "corpo raw token numérico": {"data": '{"token": ' + str(n11) + ', "cnpj": "{{1.cnpj}}"}'},
                            "corpo raw senha numérica": {"data": '{"usuario": "contador", "senha": 98765432}'},
                            "corpo raw ilegível senha numérica": {"data": '{"senha": 98765432, "n": {{1.n}}}'}}.items():
            with self.subTest(caso=nome):
                self.assertTrue(any("credencial" in p for p in cb.checar(_com_http(campo))), nome)
        for nome, campo in {"secretaria": {"secretaria": "Secretaria da Fazenda SP"},
                            "resenha": {"resenha": "Cliente pediu revisão do balancete"},
                            "Token expirado": {"texto": "Token expirado: renove a conexão no Make"},
                            "max_tokens texto": {"model": "gpt-4.1-mini", "max_tokens": "100000"},
                            "max_tokens número": {"max_tokens": 100000},
                            "token_ttl curto": {"token_ttl": 3600},
                            "booleano": {"shareCookies": True, "password_required": False}}.items():
            with self.subTest(caso=nome):
                self.assertEqual(cb.checar(_com_http(campo)), [], nome)

    def test_rodada_8(self):
        """R1-R3@opus e A1 (rodada 8): marcador como pedaço da palavra, plural, cookie como última palavra; número em
        campo de duração ou limite não é credencial."""
        v = "abc123" + "def456"
        for nome in ("secretkey", "tokenacesso", "senhacertificado", "passwordhash", "credentials", "client_credentials",
                     "secrets", "dbpwd", "auth_cookie"):
            with self.subTest(caso=nome):
                self.assertTrue(any("credencial" in p for p in cb.checar(_com_http({"data": {nome: v}}))), nome)
        bp = _com_http({"headers": [{"name": "X-Session-Cookie", "value": v}]})
        self.assertTrue(any("credencial" in p for p in cb.checar(bp)), "X-Session-Cookie")
        for nome, campo in {"token_expires_in": {"token_expires_in": 2592000}, "token_limit": {"token_limit": 128000},
                            "password_max_age": {"password_max_age": 7776000},
                            "secretariaFazenda": {"secretariaFazenda": "Secretaria da Fazenda"},
                            "maxtokens": {"maxtokens": "100000"}}.items():
            with self.subTest(caso=nome):
                self.assertEqual(cb.checar(_com_http(campo)), [], nome)

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
