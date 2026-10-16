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


class Residuos(unittest.TestCase):
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
