"""SPEC_MAKE_S5 AT-010 (Decision 10 do DESIGN): o kit congelado (edge, webhook com chave, Database Webhook, pg_cron,
makeAnApiCall, watchEvents, RPC de auditoria, chave nomeada) não vaza para o texto publicado.

Varre `skills/**/*.md`, `compartilhado/*.md`, `README.md`, cada `manifest.json` e os casos `positive` de cada
`evals/cases.json` (os negativos nomeiam o que a skill recusa; o oráculo ESPERADO de tests/evals.py já barra negativo
órfão). A permissão é por bloco, só duas: a recusa `[S2]` do design e a lista "nunca chame" do `[H2]` do handoff (existe
desde a v1.1.0). A versão reservada ao congelado não aparece em nenhum arquivo publicável nem no CHANGELOG.
"""
from __future__ import annotations

import json
import re
import unittest

from contrato import RAIZ, bloco

TERMOS = ("x-make-apikey", "hooks_create", "keys_list", "Database Webhook", "/functions/v1/", "/rest/v1/",
          "makeAnApiCall", "watchEvents", "pg_cron", "pg_net", "ActionSendDataAPIKeyAuth", "withSupabase",
          "security definer", "New secret key", "Webhook API Key Auth")
# palavras soltas do kit congelado (R3@codex/R4@opus 1b): "tabelas, cron ou edges" na prosa passava pela lista de termos exatos
PADROES = (re.compile(r"\bedges?\b", re.I), re.compile(r"\bcron\b", re.I),
           re.compile(r"\bchaves?\s+nomeadas?\b", re.I))      # R4@opus (rodada 2): a docstring a prometia e nada a pegava
RESERVADA = "1.2" + ".0"      # montada em pedaços: este arquivo não pode ser o resíduo que ele procura
PERMITIDOS = {"spec-make-design/SKILL.md": "S2", "spec-make-handoff/SKILL.md": "H2"}


def sem_bloco(texto: str, ancora: str) -> str:
    """Tira da âncora `**[XN] ` até a próxima âncora ou título."""
    b = bloco(texto, ancora)
    if b is None:
        return texto
    i = texto.find(f"**[{ancora}] ")
    return texto[:i] + texto[i + len(f"**[{ancora}] ") + len(b):]


def textos_publicados(raiz=RAIZ) -> dict[str, str]:
    """caminho relativo → texto a varrer (já sem os blocos permitidos e só com os casos positivos dos evals)."""
    saida: dict[str, str] = {}
    arquivos = sorted((raiz / "skills").rglob("*.md")) + sorted((raiz / "compartilhado").glob("*.md"))
    for extra in ("README.md", "CHANGELOG.md"):      # R4@opus (rodada 2): o CHANGELOG também é texto publicado
        if (raiz / extra).is_file():
            arquivos.append(raiz / extra)
    for f in arquivos:
        rel = f.relative_to(raiz).as_posix()
        texto = f.read_text(encoding="utf-8")
        ancora = PERMITIDOS.get(rel.removeprefix("skills/"))
        saida[rel] = sem_bloco(texto, ancora) if ancora else texto
    for f in sorted((raiz / "skills").glob("*/manifest.json")):
        saida[f.relative_to(raiz).as_posix()] = f.read_text(encoding="utf-8")
    for f in sorted((raiz / "skills").glob("*/evals/cases.json")):
        casos = json.loads(f.read_text(encoding="utf-8")).get("cases", [])
        saida[f.relative_to(raiz).as_posix() + "#positivos"] = json.dumps(
            [c for c in casos if c.get("type") == "positive"], ensure_ascii=False)
    return saida


def residuos(textos: dict[str, str]) -> list[str]:
    achados = [f"{rel}: {t!r}" for rel, txt in textos.items() for t in TERMOS if t in txt]
    return achados + [f"{rel}: /{p.pattern}/" for rel, txt in textos.items() for p in PADROES if p.search(txt)]


def versao_reservada(raiz=RAIZ) -> list[str]:
    """A versão reservada em qualquer arquivo publicável: .md, .json (inclusive os negativos) e o CHANGELOG."""
    achados = []
    for f in sorted(raiz.rglob("*")):
        rel = f.relative_to(raiz).as_posix()
        # .claude/: a pasta que a review plantou no repo público (LM-236) nunca é publicada; ela mora no worktree
        if not f.is_file() or f.suffix not in (".md", ".json") or rel.startswith((".git/", ".claude/", "dist/", "tests/")):
            continue
        if RESERVADA in f.read_text(encoding="utf-8"):
            achados.append(rel)
    return achados


# SPEC_MAKE_S6 AT-004 (contrato C2 #2): o que antes parava a etapa vira alerta. A forma da recusa varia ("recuse",
# "A skill recusa", "pare e", "volte à") — regex, nunca lista fechada de frases (LM-359). Permitido só nos blocos que
# param de verdade e numa lista NOMEADA de exceções, cada uma com motivo.
RECUSA = re.compile(r"recus\w*|\bpare\b|\bvolte\b|não crie", re.I)
BLOCOS_QUE_PARAM = {"spec-make-build/SKILL.md": ("B8", "B2", "B4", "B6"), "spec-make-handoff/SKILL.md": ("H4", "H2")}
BLOCOS_CONDUCAO = ("X1",)
EXCECOES: list[tuple[str, str, str]] = [
    ("MCP_MAKE.md", "`validate_blueprint_schema` a recusa", "fato medido do Make: o validador recusa a chave interface"),
    ("MCP_MAKE.md", "`scenarios_run` recusa fluxo inativo", "fato medido do Make: rodar exige o fluxo ativo"),
    ("DIAGNOSTICO.md", "o validador recusa", "fato medido do Make (mesmo do MCP_MAKE.md)"),
    ("spec-make-design/references/PROTOCOLO.md", "o validador do Make a recusa", "fato medido do Make"),
    ("spec-make-design/SKILL.md", "gatilho que recusa alterar", "descreve o gatilho SQL da auditoria, não a skill"),
    ("spec-make-handoff/SKILL.md", "testar a recusa do fluxo de boletos", "fala da pessoa no exemplo: o fluxo de boletos tem a recusa"),
    # rodada 1c (A2@fable): trechos exatos do exemplo dos boletos, nunca "recusa" solto no arquivo inteiro
    ("HANDOFF_EXEMPLO.md", "Testar a recusa pelo link (parte 2/2)", "exemplo: o fluxo de boletos tem o passo de recusa"),
    ("HANDOFF_EXEMPLO.md", "testar a recusa pelo link.", "exemplo: o fluxo de boletos tem o passo de recusa"),
    ("HANDOFF_EXEMPLO.md", "rodar o teste de recusa na parte 6600102", "exemplo: o fluxo de boletos tem o passo de recusa"),
]


def recusas_fora_de_bloco(raiz=RAIZ) -> list[str]:
    """Ocorrências da regex fora dos blocos que param e das exceções nomeadas, em skills/**/*.md e compartilhado/*.md
    (menos SUPABASE.md, onde "recusa" descreve o gatilho do banco)."""
    achados = []
    arquivos = sorted((raiz / "skills").rglob("*.md")) + sorted((raiz / "compartilhado").glob("*.md"))
    for f in arquivos:
        if f.name == "SUPABASE.md":
            continue
        rel = f.relative_to(raiz).as_posix()
        texto = f.read_text(encoding="utf-8")
        ancoras = BLOCOS_QUE_PARAM.get(rel.removeprefix("skills/"), ()) + (BLOCOS_CONDUCAO if f.name == "CONDUCAO.md" else ())
        for a in ancoras:
            texto = sem_bloco(texto, a)
        for n, linha in enumerate(texto.splitlines(), 1):
            if not RECUSA.search(linha):
                continue
            if any(rel.endswith(arq) and trecho in linha for arq, trecho, _ in EXCECOES):
                continue
            achados.append(f"{rel}:{n}: {linha.strip()[:100]}")
    return achados


PROMPT_BUILDER_ANTIGO = "sdd-" + "prompt-builder"   # montado em pedaços: este arquivo não pode ser o resíduo que procura

# SPEC_MAKE_S7 AT-001/AT-006 (DESIGN Decision 8): a 1.5.0 aceita o arquivo real da rotina. O texto que EXIGIA amostra limpa
# ("sem dado pessoal real", "dado inventado ou público", "origem: pública | inventada") não volta. A regra nova escreve a
# negação e a alternativa ("Nunca peça dado inventado ou público", "real | inventada | pública"): por isso as exceções são
# NOMEADAS por trecho exato, com a caixa — nunca por arquivo inteiro (R2@codex, R2@fable).
EXIGENCIA = re.compile(r"dado pessoal real|sem dado pessoal|inventad[oa]s? ou públic[oa]|inventada\s*\|?\s*pública"
                       r"|públic[oa]\s*\|\s*inventad", re.I)
EXCECOES_EXIGENCIA: list[tuple[str, str, str]] = [
    ("CONDUCAO.md", "Nunca peça dado inventado ou público no lugar dele.", "negação do [F1] (fonte e as 5 cópias)"),
    ("skills/spec-make-define/assets/DEFINE_TEMPLATE.md", "(origem: {real, mascarada aqui | inventada | pública})",
     "o campo novo lista `real` primeiro"),
    ("skills/spec-make-define/references/VERIFY_GATE_EXECUCAO.md", "(origem: real, mascarada aqui | inventada | pública)",
     "o campo novo lista `real` primeiro"),
    ("skills/spec-make-brainstorm/evals/cases.json", "Não pede amostra inventada ou pública",
     "expected do positivo amostra-pessoal: diz o que a skill NÃO faz"),
    ("CHANGELOG.md", "dado pessoal real, ligar o gatilho", "histórico da v1.4.0 (a v1.5.0 tirou o dado pessoal do bloqueio)"),
]
ALERTA_DADO_REAL = re.compile(r"alerta \[A1\][^.]{0,200}?(arquivo real|dado real|dado pessoal|anexo)", re.I)


def arquivos_da_exigencia(raiz=RAIZ) -> list[Path]:
    """Texto publicado inteiro: .md das skills e do compartilhado, README, CHANGELOG, manifests e TODOS os casos dos evals."""
    achados = sorted((raiz / "skills").rglob("*.md")) + sorted((raiz / "compartilhado").glob("*.md"))
    achados += [raiz / n for n in ("README.md", "CHANGELOG.md") if (raiz / n).is_file()]
    achados += sorted((raiz / "skills").glob("*/manifest.json")) + sorted((raiz / "skills").glob("*/evals/cases.json"))
    return achados


def exigencias(raiz=RAIZ, textos: dict[str, str] | None = None) -> list[str]:
    """Linhas do texto publicado que exigem amostra limpa, menos as exceções nomeadas (trecho exato dentro da linha)."""
    if textos is None:
        textos = {f.relative_to(raiz).as_posix(): f.read_text(encoding="utf-8") for f in arquivos_da_exigencia(raiz)}
    saida = []
    for rel, txt in textos.items():
        for n, linha in enumerate(txt.splitlines(), 1):
            if not EXIGENCIA.search(linha):
                continue
            if any(rel.endswith(arq) and trecho in linha for arq, trecho, _ in EXCECOES_EXIGENCIA):
                continue
            saida.append(f"{rel}:{n}: {linha.strip()[:100]}")
    return saida


def alertas_de_dado_real(textos: dict[str, str]) -> list[str]:
    """`alerta [A1]` cuja frase cita arquivo real, dado real, dado pessoal ou anexo: dado real não vira alerta (AT-006)."""
    saida = []
    for rel, txt in textos.items():
        for par in re.split(r"\n\s*\n", txt):
            if ALERTA_DADO_REAL.search(" ".join(par.split())):
                saida.append(rel)
                break
    return saida


class Residuos(unittest.TestCase):
    def test_s6_nenhuma_recusa_fora_dos_blocos_que_param(self):
        self.assertEqual(recusas_fora_de_bloco(), [])

    def test_s6_recusa_inserida_reprova(self):
        """Mutantes do contrato C2 #2: as formas que a lista fechada não pegava, cada uma num arquivo diferente."""
        import shutil
        import tempfile
        from pathlib import Path
        casos = [("skills/spec-make-define/SKILL.md", "\nA skill recusa o teste.\n"),
                 ("skills/spec-make-build/references/PROTOCOLO.md", "\nSe faltar, pare e diga o que falta.\n"),
                 ("skills/spec-make-design/references/PROTOCOLO.md", "\nSem a chave, volte à etapa 2.\n"),
                 ("compartilhado/CONDUCAO.md", "\nSem o documento, não crie nada.\n"),
                 ("skills/spec-make-handoff/assets/HANDOFF_EXEMPLO.md", "\nA skill recusa a ficha sem id.\n")]
        with tempfile.TemporaryDirectory() as d:
            r = Path(d)
            shutil.copytree(RAIZ / "skills", r / "skills")
            shutil.copytree(RAIZ / "compartilhado", r / "compartilhado")
            self.assertEqual(recusas_fora_de_bloco(r), [])
            for arq, extra in casos:
                with self.subTest(arquivo=arq):
                    alvo = r / arq
                    original = alvo.read_text(encoding="utf-8")
                    alvo.write_text(original + extra, encoding="utf-8")
                    self.assertTrue(any(a.startswith(arq) for a in recusas_fora_de_bloco(r)), "recusa inserida passou")
                    alvo.write_text(original, encoding="utf-8")

    def test_s7_nenhuma_exigencia_de_amostra_limpa(self):
        """AT-001: 0 exigência de dado inventado/público/sem dado pessoal no texto publicado, fora das exceções nomeadas."""
        self.assertEqual(exigencias(), [])

    def test_s7_exigencia_plantada_em_cada_tipo_de_arquivo_reprova(self):
        """Mutantes: a frase antiga, e a negação SEM o "Nunca" (que a exceção não cobre), em cada tipo de arquivo."""
        base = {f.relative_to(RAIZ).as_posix(): f.read_text(encoding="utf-8") for f in arquivos_da_exigencia()}
        tipos = ["skills/spec-make-brainstorm/SKILL.md", "skills/spec-make-define/assets/DEFINE_TEMPLATE.md",
                 "compartilhado/CONDUCAO.md", "compartilhado/COPY.md", "README.md", "CHANGELOG.md",
                 "skills/spec-make-build/manifest.json", "skills/spec-make-brainstorm/evals/cases.json"]
        for chave in tipos:
            for planta in ("Peça uma amostra sem dado pessoal real.", "Peça dado inventado ou público no lugar dele.",
                           "origem: pública | inventada"):
                with self.subTest(arquivo=chave, planta=planta[:30]):
                    mut = dict(base)
                    mut[chave] = mut[chave] + f"\n{planta}\n"
                    self.assertTrue(exigencias(textos=mut), "exigência plantada passou")

    def test_s7_cada_excecao_e_necessaria(self):
        """Prova de que a lista não é um passe livre: sem a exceção, o texto real reprova; e a exceção vale só na caixa certa."""
        base = {f.relative_to(RAIZ).as_posix(): f.read_text(encoding="utf-8") for f in arquivos_da_exigencia()}
        self.assertEqual(len(EXCECOES_EXIGENCIA), 5)
        for arq, trecho, motivo in EXCECOES_EXIGENCIA:
            with self.subTest(arquivo=arq):
                alvos = [k for k in base if k.endswith(arq) and trecho in base[k]]
                self.assertTrue(alvos, f"exceção sem uso: {motivo}")
                for alvo in alvos:
                    mut = dict(base)
                    mut[alvo] = mut[alvo].replace(trecho, trecho.lower() if trecho != trecho.lower() else trecho.upper(), 1)
                    self.assertTrue(any(a.startswith(alvo) for a in exigencias(textos=mut)),
                                    "a exceção cobriu uma linha mudada: o trecho exato não está mandando")

    def test_s7_dado_real_nao_vira_alerta(self):
        """AT-006: 0 `alerta [A1]` citando arquivo real/dado real/dado pessoal/anexo; o aviso do [F1] não é alerta."""
        base = {f.relative_to(RAIZ).as_posix(): f.read_text(encoding="utf-8")
                for f in sorted((RAIZ / "skills").rglob("*.md")) + sorted((RAIZ / "compartilhado").glob("*.md"))}
        self.assertEqual(alertas_de_dado_real(base), [])
        for chave in ("skills/spec-make-brainstorm/SKILL.md", "compartilhado/CONDUCAO.md"):
            with self.subTest(arquivo=chave):
                mut = dict(base)
                mut[chave] = mut[chave] + "\n\nArquivo com dado pessoal: alerta [A1] — o arquivo real tem dado pessoal.\n"
                self.assertEqual(alertas_de_dado_real(mut), [chave])

    def test_s7_aviso_sem_mcp_nao_inventa_zona(self):
        """AT-006 (while sem MCP): o ramo [M1] do aviso manda tirar a zona; mutante com "servidores na Europa" reprova."""
        texto = (RAIZ / "compartilhado/CONDUCAO.md").read_text(encoding="utf-8")
        self.assertIn("não invente uma zona", " ".join(texto.split()))
        proto = (RAIZ / "skills/spec-make-brainstorm/references/PROTOCOLO.md").read_text(encoding="utf-8")
        self.assertIn("sem o conector, tire o trecho da zona", " ".join(proto.split()))
        for arq in ("compartilhado/CONDUCAO.md", "skills/spec-make-brainstorm/references/PROTOCOLO.md",
                    "skills/spec-make-brainstorm/SKILL.md", "README.md"):
            conteudo = (RAIZ / arq).read_text(encoding="utf-8")
            self.assertNotRegex(conteudo, r"servidores (na|nos) (Europa|EUA)", f"{arq} afirma país de servidor")

    def test_s6_texto_publicado_sem_o_builder_antigo(self):
        """AT-009: o nome antigo do builder fora de todo texto publicado (skills, compartilhado, README, CHANGELOG,
        manifests e casos positivos); mutante em memória reprova."""
        t = textos_publicados()
        self.assertEqual([k for k, v in t.items() if PROMPT_BUILDER_ANTIGO in v], [])
        mut = dict(t)
        mut["README.md"] = mut["README.md"] + f"\nInstale a {PROMPT_BUILDER_ANTIGO}.\n"
        self.assertEqual([k for k, v in mut.items() if PROMPT_BUILDER_ANTIGO in v], ["README.md"])

    def test_texto_publicado_sem_resquicio_do_kit_congelado(self):
        self.assertEqual(residuos(textos_publicados()), [])

    def test_versao_reservada_fora_de_todo_arquivo_publicavel(self):
        self.assertEqual(versao_reservada(), [])

    def test_a_varredura_enxerga_cada_tipo_de_arquivo(self):
        """Contra o guard que itera sobre o que aparece: a varredura tem de ter lido md, manifest e casos positivos."""
        t = textos_publicados()
        self.assertGreater(len(t), 30)
        self.assertTrue(any(k.endswith("DESIGN_TEMPLATE.md") for k in t))
        self.assertTrue(any(k.endswith("references/MCP_MAKE.md") for k in t))
        self.assertEqual(sum(1 for k in t if k.endswith("manifest.json")), 5)
        self.assertEqual(sum(1 for k in t if k.endswith("#positivos")), 5)
        self.assertIn("design-supabase", t["skills/spec-make-design/evals/cases.json#positivos"])

    def test_mutante_termo_novo_em_cada_lugar_reprova(self):
        base = textos_publicados()
        for chave in ("skills/spec-make-design/SKILL.md", "skills/spec-make-design/assets/DESIGN_TEMPLATE.md",
                      "skills/spec-make-design/references/PROTOCOLO.md", "compartilhado/MCP_MAKE.md",
                      "compartilhado/SUPABASE.md", "CHANGELOG.md", "skills/spec-make-build/SKILL.md",
                      "skills/spec-make-build/references/PROTOCOLO.md", "skills/spec-make-build/manifest.json",
                      "skills/spec-make-design/evals/cases.json#positivos"):
            for termo in ("watchEvents", "Database Webhook", "pg_cron", "receitas de cron", "chame uma edge", "crie uma chave nomeada"):
                with self.subTest(arquivo=chave, termo=termo):
                    mut = dict(base)
                    mut[chave] = mut[chave] + f"\nUse {termo}.\n"
                    self.assertTrue(residuos(mut), "resíduo inserido passou")

    def test_termo_no_bloco_permitido_nao_reprova_e_fora_dele_reprova(self):
        for rel, ancora in PERMITIDOS.items():
            txt = (RAIZ / "skills" / rel).read_text(encoding="utf-8")
            self.assertIsNotNone(bloco(txt, ancora), f"bloco [{ancora}] ausente em {rel}")
            dentro = txt.replace(f"**[{ancora}] ", f"**[{ancora}] Use makeAnApiCall e hooks_create. ", 1)
            self.assertEqual(residuos({rel: sem_bloco(dentro, ancora)}), [])
            fora = txt.replace("## Quick start", "## Quick start\n\nUse makeAnApiCall.", 1)
            self.assertTrue(residuos({rel: sem_bloco(fora, ancora)}))

    def test_versao_reservada_num_manifest_ou_no_changelog_reprova(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            r = Path(d)
            (r / "skills/s").mkdir(parents=True)
            (r / "skills/s/manifest.json").write_text(json.dumps({"version": RESERVADA}), encoding="utf-8")
            (r / "CHANGELOG.md").write_text(f"## v{RESERVADA}\n", encoding="utf-8")
            (r / "skills/s/evals").mkdir()
            (r / "skills/s/evals/cases.json").write_text(json.dumps({"version": "1.3.0", "cases": [
                {"id": "x", "type": "negative_control", "input": f"v{RESERVADA}"}]}), encoding="utf-8")
            self.assertEqual(sorted(versao_reservada(r)),
                             ["CHANGELOG.md", "skills/s/evals/cases.json", "skills/s/manifest.json"])


if __name__ == "__main__":
    unittest.main()
