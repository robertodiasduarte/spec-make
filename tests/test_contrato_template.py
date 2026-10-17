"""AT-001 (SPEC_MAKE_SUPABASE): o DESIGN_TEMPLATE traz a coluna `Alcance` na tabela dos módulos e as seções
`Fontes consultadas`, `Prepare o banco` e `Relógio`; num fluxo sem Supabase, a coluna e as 2 seções do banco dizem
"não se aplica: o fluxo não usa Supabase" (nas 2 seções, precedida da condição "Sem Supabase:"), e a seção `Custo` traz
a linha das operações paradas por mês do [S4] (AT-005). Avaliador fresco, ciclo 2: nenhum teste lia o template — apagar
as seções, a coluna ou a frase passava. Cada asserção morde um mutante em memória, nunca em disco (LM-146).

O template só existe em skills/spec-make-design/assets/ (não é compartilhado: sync-compartilhados.py não o copia);
a build lê o DESIGN entregue, não o template."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
TEMPLATE = RAIZ / "skills" / "spec-make-design" / "assets" / "DESIGN_TEMPLATE.md"

NAO_SE_APLICA = '"não se aplica: o fluxo não usa Supabase"'
SECOES = ["## O fluxo, módulo a módulo", "## Fontes consultadas", "## Prepare o banco", "## Relógio", "## Custo"]
# seções que, sem Supabase, dizem a frase inteira, COM a condição: "Com Supabase: …" (1 edição) inverte o sentido
# (review pós-build rodada 4b, R1@opus)
SECOES_SUPABASE = ["## Prepare o banco", "## Relógio"]
CONDICAO_SEM_SUPABASE = f"Sem Supabase: {NAO_SE_APLICA}"
# [S4] / AT-005: o lugar do custo ocioso da agenda do Make (R3@opus, rodada 4b)
CUSTO_OCIOSO = "Operações paradas por mês (agenda do Make): {disparos por mês} × {operações do disparo vazio}"
# [W1]: as colunas que a documentação consultada preenche
COLUNAS_FONTES = ["App", "URL", "Data", "Módulo e versão lidos", "Divergência com a conta"]


def secao(texto: str, titulo: str) -> str | None:
    """Corpo da seção `titulo` (linha exata) até o próximo título `## `; None se o título não existe."""
    linhas = texto.splitlines()
    if titulo not in linhas:
        return None
    i = linhas.index(titulo) + 1
    fim = next((k for k in range(i, len(linhas)) if linhas[k].startswith("## ")), len(linhas))
    return "\n".join(linhas[i:fim])


def _celulas(linha: str) -> list[str]:
    return [c.strip() for c in linha.strip().strip("|").split("|")]


def tabela(corpo: str) -> list[list[str]]:
    """Linhas da 1ª tabela Markdown do corpo, já em células (cabeçalho, separador e dados)."""
    return [_celulas(l) for l in corpo.splitlines() if l.lstrip().startswith("|")]


def checar_template(texto: str) -> list[str]:
    erros = []
    for t in SECOES:
        if secao(texto, t) is None:
            erros.append(f"falta a seção {t!r}")
    modulos = secao(texto, "## O fluxo, módulo a módulo")
    if modulos is not None:
        linhas = tabela(modulos)
        if len(linhas) < 3:
            erros.append("a tabela dos módulos precisa de cabeçalho, separador e 1 linha de exemplo")
        elif "Alcance" not in linhas[0]:
            erros.append("falta a coluna 'Alcance' na tabela dos módulos")
        else:
            k = linhas[0].index("Alcance")
            if any(len(l) != len(linhas[0]) for l in linhas[1:]):
                erros.append("a tabela dos módulos tem linha com número de colunas diferente do cabeçalho")
            elif not all(re.fullmatch(r":?-{3,}:?", c) for c in linhas[1]):
                erros.append("a 2ª linha da tabela dos módulos não é o separador")
            elif NAO_SE_APLICA not in linhas[2][k]:
                erros.append(f"a coluna 'Alcance' não diz {NAO_SE_APLICA} para fluxo sem Supabase")
            elif "[S1]" not in linhas[2][k]:
                erros.append("a coluna 'Alcance' não remete a [S1] (motivo · tabelas · operações)")
    fontes = secao(texto, "## Fontes consultadas")
    if fontes is not None:
        linhas = tabela(fontes)
        if not linhas or linhas[0] != COLUNAS_FONTES:
            erros.append(f"as colunas de 'Fontes consultadas' não são {COLUNAS_FONTES}")
        if '"não consultado"' not in fontes:
            erros.append("'Fontes consultadas' não prevê \"não consultado\" ([W1])")
    for t in SECOES_SUPABASE:
        corpo = secao(texto, t)
        if corpo is not None and CONDICAO_SEM_SUPABASE not in " ".join(corpo.split()):
            erros.append(f"{t!r} não diz {CONDICAO_SEM_SUPABASE!r} para fluxo sem Supabase")
    custo = secao(texto, "## Custo")
    if custo is not None and CUSTO_OCIOSO not in " ".join(custo.split()):
        erros.append("'Custo' sem a linha das operações paradas por mês da agenda do Make ([S4])")
    return erros


def _sem_secao(texto: str, titulo: str) -> str:
    corpo = secao(texto, titulo)
    assert corpo is not None, titulo
    return texto.replace(f"{titulo}\n{corpo}", "", 1)


def _sem_coluna_alcance(texto: str) -> str:
    """A tabela dos módulos sem a última coluna (Alcance) em todas as linhas."""
    corpo = secao(texto, "## O fluxo, módulo a módulo")
    novo = "\n".join(re.sub(r"\|[^|]*\|$", "|", l) if l.startswith("|") else l for l in corpo.splitlines())
    return _troca_corpo(texto, "## O fluxo, módulo a módulo", corpo, novo)


def _troca_corpo(texto: str, titulo: str, corpo: str, novo: str) -> str:
    """Troca o corpo DA SEÇÃO `titulo` (título + corpo juntos): corpos iguais em 2 seções não fazem o mutante de uma
    cair na outra (review pós-build rodada 4b, A1@fable)."""
    alvo = f"{titulo}\n{corpo}"
    assert texto.count(alvo) == 1, titulo
    return texto.replace(alvo, f"{titulo}\n{novo}", 1)


def _troca_na_secao(texto: str, titulo: str, de: str, para: str) -> str:
    corpo = secao(texto, titulo)
    assert corpo is not None and de in corpo, (titulo, de)
    return _troca_corpo(texto, titulo, corpo, corpo.replace(de, para))


def mutantes_template(t: str) -> dict[str, str]:
    """Textos alterados que checar_template TEM de reprovar: cada seção, a coluna e a frase removidas ou trocadas."""
    frase = NAO_SE_APLICA.strip('"')
    return {
        "sem 'Prepare o banco'": _sem_secao(t, "## Prepare o banco"),
        "sem 'Relógio'": _sem_secao(t, "## Relógio"),
        "sem 'Fontes consultadas'": _sem_secao(t, "## Fontes consultadas"),
        "sem 'Prepare o banco' e 'Relógio'": _sem_secao(_sem_secao(t, "## Prepare o banco"), "## Relógio"),
        "título 'Relógio' trocado": t.replace("## Relógio\n", "## Agenda\n", 1),
        "título 'Prepare o banco' trocado": t.replace("## Prepare o banco\n", "## Banco\n", 1),
        "sem a coluna Alcance": _sem_coluna_alcance(t),
        "cabeçalho sem 'Alcance'": t.replace("| Conexão | Alcance |", "| Conexão | |", 1),
        "Alcance sem o 'não se aplica'": _troca_na_secao(t, "## O fluxo, módulo a módulo",
                                                         f' · "{frase}"', ""),
        "Alcance sem [S1]": _troca_na_secao(t, "## O fluxo, módulo a módulo", " ([S1])", ""),
        "'Prepare o banco' sem o 'não se aplica'": _troca_na_secao(t, "## Prepare o banco",
                                                                   f'Sem Supabase: "{frase}".', ""),
        "'Relógio' sem o 'não se aplica'": _troca_na_secao(t, "## Relógio", f'Sem Supabase: "{frase}".', ""),
        "'Relógio' com a frase invertida": _troca_na_secao(t, "## Relógio", frase,
                                                           "se aplica: o fluxo usa Supabase"),
        "'Fontes consultadas' sem a coluna URL": _troca_na_secao(t, "## Fontes consultadas", "| URL ", ""),
        "'Fontes consultadas' sem \"não consultado\"": _troca_na_secao(t, "## Fontes consultadas",
                                                                      ' · "não consultado"', ""),
        # rodada 4b: a condição invertida com 1 edição (R1@opus) e o custo ocioso (R3@opus)
        "'Prepare o banco' com 'Com Supabase:'": _troca_na_secao(t, "## Prepare o banco", "Sem Supabase:", "Com Supabase:"),
        "'Relógio' com 'Com Supabase:'": _troca_na_secao(t, "## Relógio", "Sem Supabase:", "Com Supabase:"),
        "'Custo' sem as operações paradas": _troca_na_secao(t, "## Custo", "Operações paradas por mês", "Operações por mês"),
        "sem 'Custo'": _sem_secao(t, "## Custo"),
    }


class Template(unittest.TestCase):
    def setUp(self):
        self.texto = TEMPLATE.read_text(encoding="utf-8")

    def test_template_real_passa(self):
        self.assertEqual(checar_template(self.texto), [])

    def test_mutante_de_uma_secao_so_muda_ela(self):
        """A1@fable (rodada 4b): o mutante rotulado 'Relógio' muda o Relógio e deixa o 'Prepare o banco' igual."""
        mut = mutantes_template(self.texto)["'Relógio' com 'Com Supabase:'"]
        self.assertEqual(secao(mut, "## Prepare o banco"), secao(self.texto, "## Prepare o banco"))
        self.assertNotEqual(secao(mut, "## Relógio"), secao(self.texto, "## Relógio"))
        erros = checar_template(mut)
        self.assertTrue(erros and all("Relógio" in e for e in erros), erros)

    def test_template_e_unico(self):
        """Não há cópia do template em outra skill nem em compartilhado/: se surgir, este teste a aponta."""
        copias = sorted(p.relative_to(RAIZ).as_posix() for p in RAIZ.rglob("DESIGN_TEMPLATE*.md")
                        if ".git" not in p.parts)
        self.assertEqual(copias, ["skills/spec-make-design/assets/DESIGN_TEMPLATE.md"])

    def test_mutantes_reprovam(self):
        t = self.texto
        casos = mutantes_template(t)
        self.assertGreaterEqual(len(casos), 19)
        for nome, mut in casos.items():
            with self.subTest(mutante=nome):
                self.assertNotEqual(mut, t, "o mutante não mudou o texto")
                self.assertTrue(checar_template(mut), f"mutante passou: {nome}")



# SPEC_MAKE_S6 AT-006: a seção dos alertas aceitos (título sem emoji: o SKILL.md cita a mesma string) com "nenhum"
TEMPLATES_ALERTAS = ["spec-make-brainstorm/assets/BRAINSTORM_TEMPLATE.md", "spec-make-define/assets/DEFINE_TEMPLATE.md",
                     "spec-make-design/assets/DESIGN_TEMPLATE.md", "spec-make-build/assets/FICHA_DO_FLUXO_TEMPLATE.md",
                     "spec-make-handoff/assets/HANDOFF_TEMPLATE.md", "spec-make-handoff/assets/HANDOFF_EXEMPLO.md"]
TITULO_ALERTAS = "## Alertas aceitos"


def problemas_alertas(textos: dict[str, str]) -> list[str]:
    erros = []
    for arq in TEMPLATES_ALERTAS:
        corpo = secao(textos[arq], TITULO_ALERTAS)
        if corpo is None:
            erros.append(f"{arq}: falta a seção {TITULO_ALERTAS!r}")
        elif "nenhum" not in corpo:
            erros.append(f"{arq}: a seção {TITULO_ALERTAS!r} não prevê \"nenhum\"")
    recibo = textos["spec-make-build/assets/RECIBO_TEMPLATE.md"]
    linha = next((l for l in recibo.splitlines() if "Alertas aceitos" in l), "")
    if "nenhum" not in linha:
        erros.append("RECIBO_TEMPLATE.md: sem a linha 'Alertas aceitos' com \"nenhum\"")
    define = secao(textos["spec-make-define/assets/DEFINE_TEMPLATE.md"], "## Critérios de aceite") or ""
    linhas = tabela(define)
    if not linhas or linhas[0][-1] != "Em outras palavras" or any("Em outras palavras:" not in l[-1] for l in linhas[2:]):
        erros.append("DEFINE_TEMPLATE.md: critério sem a coluna 'Em outras palavras' preenchida em cada linha")
    return erros


def _textos_alertas() -> dict[str, str]:
    arqs = TEMPLATES_ALERTAS + ["spec-make-build/assets/RECIBO_TEMPLATE.md"]
    return {a: (RAIZ / "skills" / a).read_text(encoding="utf-8") for a in arqs}


class AlertasNosTemplates(unittest.TestCase):
    def test_s6_alertas_aceitos_e_em_outras_palavras(self):
        self.assertEqual(problemas_alertas(_textos_alertas()), [])

    def test_s6_mutantes_reprovam(self):
        real = _textos_alertas()
        mutantes = {
            "título com emoji": ("spec-make-design/assets/DESIGN_TEMPLATE.md", lambda t: t.replace(TITULO_ALERTAS + "\n", "## ⚠️ Alertas aceitos\n", 1)),
            "sem a seção no handoff": ("spec-make-handoff/assets/HANDOFF_TEMPLATE.md", lambda t: t.replace(TITULO_ALERTAS + "\n", "## Alertas\n", 1)),
            "exemplo sem nenhum": ("spec-make-handoff/assets/HANDOFF_EXEMPLO.md", lambda t: t.replace(TITULO_ALERTAS + "\n\nnenhum\n", TITULO_ALERTAS + "\n\n- algo\n", 1)),
            "recibo sem a linha": ("spec-make-build/assets/RECIBO_TEMPLATE.md", lambda t: "\n".join(l for l in t.splitlines() if "Alertas aceitos" not in l)),
            "define sem em outras palavras": ("spec-make-define/assets/DEFINE_TEMPLATE.md", lambda t: t.replace(" | Em outras palavras: {…} |", " | {…} |", 1)),
        }
        for nome, (arq, mutar) in mutantes.items():
            with self.subTest(mutante=nome):
                mut = dict(real)
                mut[arq] = mutar(real[arq])
                self.assertNotEqual(mut[arq], real[arq], "o mutante não mudou nada")
                self.assertTrue(problemas_alertas(mut), "mutante passou")

if __name__ == "__main__":
    unittest.main()
