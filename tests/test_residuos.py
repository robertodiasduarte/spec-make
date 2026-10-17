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
    ("HANDOFF_EXEMPLO.md", "recusa", "exemplo: o fluxo de boletos tem o passo de recusa do boleto"),
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
                 ("compartilhado/CONDUCAO.md", "\nSem o documento, não crie nada.\n")]
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
