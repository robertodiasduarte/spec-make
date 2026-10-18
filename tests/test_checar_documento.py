"""SPEC_MAKE_S7 AT-003/AT-007: o verificador de documento reprova webhook, credencial, CPF, CNPJ e 11+ dígitos inteiros e
aprova o documento com a máscara do [F1] — e cada asserção morde um mutante em memória, nunca em disco (LM-146).

CPF, CNPJ, número longo, credencial e webhook são MONTADOS em tempo de execução: um literal de 11 dígitos, um token ou um
endereço de webhook reprovaria o publish-check (LM-058, LM-312). O oráculo da classificação recebe a implementação como
argumento (LM-360): o mutante "credencial rebaixada" roda a mesma conferência contra uma cópia que move o ERRO para AVISO."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FONTE = RAIZ / "compartilhado" / "checar_documento.py"
_spec = importlib.util.spec_from_file_location("checar_documento", FONTE)
cd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cd)  # type: ignore[union-attr]

SKILLS = ["spec-make-brainstorm", "spec-make-define", "spec-make-design", "spec-make-build", "spec-make-handoff"]


def cpf() -> str:
    return "123." + "456." + "789-" + "01"


def cpf_sem_pontos() -> str:
    return "123456789" + "-01"


def cnpj() -> str:
    return "12." + "345." + "678/" + "0001-" + "90"


def cnpj_sem_pontos() -> str:
    return "12345678" + "/0001-90"


def corrido() -> str:
    return "1" * 11


def bearer() -> str:
    return "Bearer " + "a" * 24


def webhook() -> str:
    return "https://hook.us2.make.com/" + "a" * 32


def json_password() -> str:
    return '{"password":"' + "abcd" + 'efgh"}'


def senha_solta() -> str:
    return "senha: " + "Abc" + "12345"


LIMPO = """# BRAINSTORM_BOLETOS
## Amostra
| Amostra (estrutura, com exemplo mascarado) | Origem |
|---|---|
| coluna `cpf`: `***.123.456-**` · coluna `cnpj`: `12.345.***/****-90` | real, mascarada aqui |
Cenário 6600102 · execução 3f9a1c0e-7b2d4e6f-a8c0e2f4-b6d8fa1c · sha 3f9a1c0e-7b2d4e6f-a8c0e2f4-b6d8fa1c-c3e5a7b9-d1f3b5c7-e9a1c3e5-f7b9d1a3
Companhia aberta: 33.000.167/0001-01 (CNPJ público)
API key: autorizada por link, dentro do Make
token: {{1.token}} · senha: "{{1.senha}}"
chave natural: data + documento + valor
O token expira em 1 hora.
"""
RECIBO_LIMPO = """# Recibo do teste — Boletos
| Item | Valor |
|---|---|
| Dado real no teste | teste com dado real da rotina · confidencial · origem de teste: Boletos-teste |
| Execução do teste | 6600102 · sucesso · 4 operações |
"""

# (nome, mutante(texto) -> texto, exit esperado, trecho da mensagem)
CASOS = [
    ("limpo", lambda t: t, 0, ""),
    ("cpf", lambda t: t + f"\nCPF {cpf()}\n", 1, "CPF inteiro"),
    ("cpf-meio-formatado", lambda t: t + f"\nCPF {cpf_sem_pontos()}\n", 1, "CPF inteiro"),
    ("cnpj-cliente", lambda t: t + f"\nCliente {cnpj()}\n", 1, "CNPJ inteiro"),
    ("cnpj-meio-formatado", lambda t: t + f"\nCNPJ {cnpj_sem_pontos()}\n", 1, "CNPJ inteiro"),
    ("corrido", lambda t: t + f"\nconta {corrido()}\n", 1, "11+ dígitos"),
    ("credencial-bearer", lambda t: t + f"\n{bearer()}\n", 1, "credencial escrita"),
    ("credencial-json", lambda t: t + f"\n{json_password()}\n", 1, "credencial escrita"),
    ("credencial-solta", lambda t: t + f"\n{senha_solta()}\n", 1, "credencial escrita"),
    ("webhook", lambda t: t + f"\n{webhook()}\n", 1, "URL de webhook"),
    ("publico-com-cpf", lambda t: t + f"\n{cnpj()} (CNPJ público) e CPF {cpf()}\n", 1, "CPF inteiro"),
    ("publico-so-cnpj", lambda t: t + f"\n{cnpj()} (CNPJ público)\n", 0, ""),
    ("publico-14-digitos", lambda t: t + "\n" + "9" * 14 + " (CNPJ público)\n", 0, ""),
    ("publico-com-corrido", lambda t: t + f"\n{cnpj()} (CNPJ público) e conta {corrido()}\n", 1, "11+ dígitos"),
    ("email-pessoal", lambda t: t + "\nmaria@" + "gmail.com\n", 3, "e-mail pessoal"),
    ("email-corporativo", lambda t: t + "\nfinanceiro@escritorio.example\n", 0, ""),
    ("recibo-limpo", lambda t: RECIBO_LIMPO, 0, ""),
]


def sem_erro(classificar, texto: str) -> list[str]:
    """Os ERROS que a implementação dá ao texto: o oráculo roda contra o real e contra cada mutante (LM-360)."""
    return classificar(texto)[0]


def rodar_cli(conteudo: str | None) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as d:
        arq = Path(d) / "doc.md"
        if conteudo is not None:
            arq.write_text(conteudo, encoding="utf-8")
        r = subprocess.run([sys.executable, "-I", str(FONTE), str(arq)], capture_output=True, text=True,
                           env={"PYTHONDONTWRITEBYTECODE": "1"})
        return r.returncode, r.stdout


class ChecarDocumento(unittest.TestCase):
    def test_cada_caso_tem_o_exit_e_a_mensagem(self):
        for nome, mut, esperado, trecho in CASOS:
            with self.subTest(caso=nome):
                rc, saida = rodar_cli(mut(LIMPO))
                self.assertEqual(rc, esperado, saida)
                if trecho:
                    self.assertIn(trecho, saida)

    def test_arquivo_ilegivel_sai_2(self):
        rc, saida = rodar_cli(None)
        self.assertEqual(rc, 2)
        self.assertIn("não consegui ler", saida)

    def test_mensagem_de_cpf_e_cnpj_diz_mascare(self):
        _, saida = rodar_cli(LIMPO + f"\nCPF {cpf()} e {cnpj()}\n")
        self.assertIn("mascare como ***.123.456-**", saida)
        _, saida = rodar_cli(LIMPO + f"\nCNPJ {cnpj()}\n")
        self.assertIn("mascare como 12.345.***/****-90", saida)

    def test_o_que_o_xis_um_manda_escrever_nao_vira_erro(self):
        """A1@fable: 'API key: autorizada por link' e o placeholder do Make não são credencial."""
        for linha in ("API key: autorizada por link, dentro do Make", "token: {{1.token}}", 'senha: "{{1.senha}}"',
                      "chave natural: data + documento + valor", "o token expira em 1 hora"):
            with self.subTest(linha=linha):
                self.assertEqual(cd.classificar(linha), ([], []))

    def test_credencial_rebaixada_a_aviso_reprova(self):
        """LM-360: a conferência é uma função que recebe a implementação; o mutante move o ERRO de credencial para AVISO."""
        texto = LIMPO + f"\n{bearer()}\n{json_password()}\n"
        self.assertTrue(sem_erro(cd.classificar, texto))

        def rebaixada(t: str):
            erros, avisos = cd.classificar(t)
            mover = [e for e in erros if "credencial" in e]
            return [e for e in erros if e not in mover], avisos + mover

        self.assertEqual(sem_erro(rebaixada, texto), [], "o mutante não rebaixou nada: o teste não tem dentes")

    def test_marcador_de_cnpj_publico_nao_isenta_o_resto_da_linha(self):
        erros, _ = cd.classificar(f"{cnpj()} (CNPJ público) CPF {cpf()} {bearer()}\n")
        self.assertEqual(len(erros), 2)

    def test_templates_e_exemplo_do_kit_passam(self):
        """O documento-modelo do próprio kit não pode carregar dado inteiro (nem placeholder confundido com credencial)."""
        arquivos = sorted((RAIZ / "skills").glob("*/assets/*.md"))
        self.assertGreaterEqual(len(arquivos), 7)
        for arq in arquivos:
            with self.subTest(arquivo=arq.relative_to(RAIZ).as_posix()):
                self.assertEqual(cd.classificar(arq.read_text(encoding="utf-8"))[0], [])

    def test_as_cinco_skills_levam_o_verificador(self):
        for s in SKILLS:
            with self.subTest(skill=s):
                copia = RAIZ / "skills" / s / "scripts" / "checar_documento.py"
                self.assertTrue(copia.is_file())
                self.assertEqual(copia.read_bytes(), FONTE.read_bytes())

    def test_a_fonte_nao_traz_dado_nem_credencial_literal(self):
        """O próprio arquivo é publicável: nada que o publish-check reprovaria (11+ dígitos, token, e-mail pessoal)."""
        import re
        texto = FONTE.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"[0-9]{11}", texto))
        self.assertIsNone(re.search(r"[A-Za-z0-9._%+-]+@(gmail|hotmail|outlook|yahoo|uol|terra)\.", texto))


if __name__ == "__main__":
    unittest.main()
