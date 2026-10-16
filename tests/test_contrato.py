"""AT-002…AT-008, AT-011 e MUSTs da UX Review: cada âncora tem o conteúdo exigido e cada asserção morde um mutante."""
from __future__ import annotations

import re
import unittest

from contrato import FRASES, RAIZ, REGRAS, checar, checar_frases, checar_texto, jargao, mutantes


def trocar(texto: str, de: str, para: str) -> tuple[int, str]:
    """(quantas vezes `de` aparece, texto com a troca). A busca ignora a diferença entre espaço e quebra de linha: o
    mutante não depende de onde o Markdown quebrou a linha (SPEC_MAKE_S5)."""
    padrao = re.compile(r"\s+".join(re.escape(x) for x in de.split()))
    return len(padrao.findall(texto)), padrao.sub(lambda _m: para, texto, count=1)


class Contrato(unittest.TestCase):
    def test_regras_no_texto_real(self):
        for r in REGRAS:
            with self.subTest(ancora=r.ancora, arquivo=r.arquivo):
                self.assertEqual(checar(r), [])

    def test_cada_regra_reprova_seus_mutantes(self):
        total = 0
        for r in REGRAS:
            texto = (RAIZ / "skills" / r.arquivo).read_text(encoding="utf-8")
            ms = mutantes(r, texto)
            self.assertTrue(ms, f"[{r.ancora}] {r.arquivo}: nenhum mutante gerado")
            for desc, mut in ms:
                total += 1
                with self.subTest(ancora=r.ancora, arquivo=r.arquivo, mutante=desc):
                    self.assertNotEqual(checar_texto(r, mut), [], "mutante passou: a asserção não morde")
        self.assertGreater(total, 40)

    def test_b1_criar_antes_de_validar_reprova(self):
        """Avaliador ciclo 1 (AT-002): o item 3 de [B1] passa a mandar criar antes de validar; a ordem estrita das
        primeiras menções tem de reprovar, mesmo com a sequência antiga ainda achável mais adiante."""
        r = next(r for r in REGRAS if r.ancora == "B1")
        texto = (RAIZ / "skills" / r.arquivo).read_text(encoding="utf-8")
        velho = "3. `validate_module_configuration`"
        self.assertEqual(texto.count(velho), 1)
        mut = texto.replace(velho, "3. `scenarios_create` e depois `validate_module_configuration`")
        self.assertEqual(checar_texto(r, texto), [])
        erros = checar_texto(r, mut)
        self.assertTrue(any("scenarios_create" in e for e in erros), erros)

    def test_b2_sem_sim_ligar_o_gatilho_reprova(self):
        """Avaliador ciclo 2 (AT-003, M8): trocar a consequência da falta do "sim" por ligar o gatilho tem de reprovar."""
        r = next(r for r in REGRAS if r.ancora == "B2")
        texto = (RAIZ / "skills" / r.arquivo).read_text(encoding="utf-8")
        velho = "mantém o fluxo sob demanda, sem agenda nem webhook ligados"
        self.assertEqual(texto.count(velho), 1)
        self.assertEqual(checar_texto(r, texto), [])
        self.assertNotEqual(checar_texto(r, texto.replace(velho, "liga o gatilho do DESIGN mesmo assim")), [])

    def test_regra_invertida_reprova(self):
        """Avaliador ciclo 3 (achado 2): inverter a regra com 1 edição (o "nunca", o "não", o "pare", o número do teto)
        tem de reprovar — Decision 2: grep de palavra solta passa com a regra invertida."""
        b, p, d = "spec-make-build/SKILL.md", "spec-make-build/references/PROTOCOLO.md", \
            "spec-make-build/references/DIAGNOSTICO.md"
        ds, df = "spec-make-design/SKILL.md", "spec-make-define/SKILL.md"
        h = "spec-make-handoff/SKILL.md"
        casos = [
            (b, "Nunca chame `scenarios_update`", "Pode chamar `scenarios_update`"),
            (b, 'ou ligue o gatilho real depois de a pessoa responder "Ligar agora" ou "sim"',
             'ou ligue o gatilho real; depois de a pessoa responder "Ligar agora" ou "sim"'),
            (d, "pare: não corrija nem rode de novo", "continue: corrija e rode de novo"),
            (d, "o teste roda no máximo 4 vezes", "o teste roda no máximo 9 vezes"),
            (p, "7. `scenarios_activate` — necessário para rodar; sob demanda, ele só roda quando alguém pede.\n", ""),
            (p, "Nunca peça chave no chat.", "Peça a chave no chat."),
            (b, "O fluxo é criado com `metadata.scenario.confidential: true`.",
             "O fluxo é criado com `metadata.scenario.confidential: false` (não `confidential: true`)."),
            (ds, "Sem a chave, recuse o\nDESIGN como pronto e peça a chave.",
             "Sem a chave, não recuse o\nDESIGN como pronto e não peça a chave."),
            (ds, "Sem esse passo,\nrecuse o DESIGN como pronto", "Sem esse passo,\nnão recuse o DESIGN como pronto"),
            (df, "Recuse como incompleto o teste", "Não Recuse como incompleto o teste"),
            (b, "pare antes do `scenarios_create`, diga", "não pare antes do `scenarios_create`, diga"),
            # rodada 6 (R2/R3@opus): G2, P1 do design e M1 das etapas de papel
            (ds, "Sem esse registro, recuse o DESIGN", "Sem esse registro, não recuse o DESIGN"),
            (ds, "sem esse inventário: recuse o DESIGN", "sem esse inventário: não recuse o DESIGN"),
            (ds, "e não declare o blueprint validado", "e declare o blueprint validado"),
            (df, 'ficam "a confirmar na conta" se', 'ficam "a confirmar na conta" mesmo se'),
            ("spec-make-brainstorm/SKILL.md", "Não afirme\nque um app existe", "Afirme\nque um app existe"),
            (b, "Não afirme que criou, rodou ou ligou nada.",
             "Diga que criou e rodou. (Não afirme que criou, rodou ou ligou nada só se pedirem.)"),
            # SPEC_MAKE_S5: a polaridade de cada regra nova, com 1 edição (a busca ignora onde a linha quebra)
            (ds, "nunca entram no fluxo. Sem isso, recuse o DESIGN", "podem entrar no fluxo. Sem isso, recuse o DESIGN"),
            (ds, "ficam fora: recuse o DESIGN como pronto e proponha o caminho só com o banco",
             "ficam fora: aceite o DESIGN como pronto e proponha o caminho só com o banco"),
            (ds, "e a pessoa não faz, antes do 1º fluxo rodar, mais que 1 colagem",
             "e a pessoa faz, antes do 1º fluxo rodar, mais que 1 colagem"),
            (ds, "webhook de qualquer tipo, Database Webhook", "webhook com chave de API, Database Webhook"),
            (ds, "gatilho que não seja a agenda do Make nem a execução sob demanda: recuse",
             "gatilho que não seja a agenda do Make nem a execução sob demanda: aceite"),
            (ds, "nem a execução sob demanda: recuse", "ou a execução sob demanda: recuse"),
            (ds, "que regrava a linha inteira", "que grava só o que mudou"),
            (ds, "Se o total passar do orçamento do DEFINE, recuse", "Se o total passar do orçamento do DEFINE, aceite"),
            (ds, "o DESIGN declara no bloco `Relógio` como o fluxo dispara", "o DESIGN não declara como o fluxo dispara"),
            (ds, "Chave natural que não é a `primary key` da tabela de destino do `upsertARecord`",
             "Chave natural que é a `primary key` da tabela de destino do `upsertARecord`"),
            (ds, "coluna de valor em `real`, `float4`, `float8` ou `double precision`, rateio sem",
             "coluna de valor em `numeric`, rateio sem"),
            (ds, "campo da auditoria anulável, auditoria sem o gatilho ou sem a view: recuse",
             "campo da auditoria anulável, auditoria sem o gatilho ou sem a view: aceite"),
            (ds, "auditoria sem o gatilho ou sem a view", "auditoria com o gatilho e com a view"),
            (ds, "gravados antes do \"processa\" e nunca recalculados", "gravados depois do \"processa\" e recalculados"),
            (ds, "nunca afirme uma consulta que não fez.", "afirme a consulta mesmo sem ter feito."),
            # avaliador fresco (W1): consultar a documentação é obrigatório, para cada app
            (ds, "consulte a documentação pública do Make", "pode consultar a documentação pública do Make"),
            (ds, "Para cada app do fluxo, consulte", "Se quiser, consulte"),
            (ds, "consulte a documentação pública do Make", "dispense a documentação pública do Make"),
            (ds, "divergir de `app-modules_list`, vale a conta", "divergir de `app-modules_list`, não vale a conta"),
            (ds, "e o DESIGN anota a divergência", "e o DESIGN não anota a divergência"),
            (ds, "e o DESIGN preenche a coluna", "e o DESIGN não preenche a coluna"),
            (b, "não crie o fluxo: diga o que falta", "crie o fluxo e diga depois o que falta"),
            (b, "do app `supabase` só `searchRows`", "do app `supabase` também `watchEvents` e `searchRows`"),
            (b, "gatilho só pela agenda do Make ou sob demanda", "gatilho por webhook ou pela agenda do Make"),
            (b, "nenhum módulo `postgres` ou `supabase-management`, nenhum HTTP para o projeto",
             "o módulo `postgres` ou `supabase-management` e o HTTP para o projeto são aceitos"),
            # SPEC_MAKE_HANDOFF (s3): H2, B6 (as 2 polaridades) e M1 do handoff
            (h, "Nunca chame `scenarios_create`", "Pode chamar `scenarios_create`"),
            (b, 'siga só depois do "sim" da pessoa', 'siga mesmo sem o "sim" da pessoa'),
            (b, "Depois releia `data-stores_list` e `hooks_list` e recalcule a custódia",
             "Não precisa reler `data-stores_list` e `hooks_list` nem recalcular a custódia"),
            (h, "Não afirme `lastEdit`", "Afirme `lastEdit`"),
            # avaliador fresco do s3, ciclo 1 — AT-005 (H2): ler o registro do data store; guardar a URL do webhook
            (h, "`data-stores_delete` nem `data-store-records_list` — o\nregistro de um data store pode guardar senha ou chave.",
             "`data-stores_delete`. Leia `data-store-records_list` para conferir o registro."),
            (h, "do webhook, guarde só o id e o nome", "do webhook, guarde só o id e o nome e também a URL completa"),
            # AT-003 (B6): lastEdit diferente segue sem o "sim"; compartilhado liberado a pedido
            (b, 'se for diferente, diga em 1 frase os dois horários ("editado no Make depois\nda ficha") e siga só depois '
                'do "sim" da pessoa',
             'se for diferente, siga e no fim diga os dois horários ("editado no Make depois da ficha"); se for igual, '
             'siga só depois do "sim" da pessoa'),
            (b, "Recurso `compartilhado com N cenários`: só ler e acrescentar registro — nunca\nchame",
             "Recurso `compartilhado com N cenários` se a pessoa pedir: tudo liberado. Em outro caso — nunca chame"),
            # AT-002 (H1): classe `compartilhado` redefinida; `scenarios_list` liberado para achar as partes
            ("spec-make-handoff/references/PROTOCOLO.md",
             "- `compartilhado com N cenários — só ler e acrescentar` — data store usado também fora da família; N é o "
             "total de\n  cenários em `scenarioUsages`.",
             "- `compartilhado com N cenários` — nunca usado; data store usado fora da família também é `desta família`."),
            ("spec-make-handoff/references/PROTOCOLO.md", "Use `scenarios_list` só quando a pessoa der o nome sem o id",
             "Use `scenarios_list` para achar as partes; `scenarios_list` só quando a pessoa der o nome sem o id não é "
             "regra"),
            # avaliador fresco do s3, ciclo 2 — os mutantes que sobreviveram com o snapshot regravado
            # AT-003 (B6e, B6e2, B6h): uso novo fora da família continua `desta família` / sem avisar / segue a ficha
            (b, "recurso que ganhou uso fora da família passa a `compartilhado com N\ncenários`, e você diz isso à pessoa",
             "recurso que ganhou uso fora da família continua `desta família`, sem avisar a pessoa"),
            (b, "passa a `compartilhado com N\ncenários`, e você diz isso à pessoa", "passa a `compartilhado com N\ncenários`"),
            (b, "recurso que ganhou uso fora da família passa a `compartilhado com N\ncenários`, e você diz isso à pessoa",
             "recurso que ganhou uso fora da família segue com a custódia da ficha"),
            # AT-003 (B6f): recurso fora da ficha alterado em vez de [B4]
            (b, "Recurso ausente da ficha ou `fora do spec-make`: [B4] como sempre.",
             "Recurso ausente da ficha ou `fora do spec-make`: altere também, com o aviso [B5]."),
            # AT-006 (E1i, E1h): fecho normal sem o "Pronto: …"; sem pedir para salvar os dois
            (b, 'diz: "Pronto: o fluxo\nestá na sua conta. A ficha diz o que fazer quando ele falhar; o handoff',
             'diz: "Feito. A ficha diz o que fazer quando ele falhar; o handoff'),
            (b, "pede para salvar os dois e diz", "e diz"),
            # AT-006 (H3d): design e build trocados no mapeamento do prompt de retomada
            (h, '("Use a skill spec-make-design." quando o desenho muda; "Use a skill spec-make-build." quando só\nimplementa',
             '("Use a skill spec-make-build." quando o desenho muda; "Use a skill spec-make-design." quando só\nimplementa'),
            # AT-009 (M1b, M1c): sem o aviso em 1 frase; sem o "sem o conector" na linha "Gerada"
            (h, "Se a conversa não tiver o MCP do Make, avise em uma frase, escreva",
             "Se a conversa não tiver o MCP do Make, escreva"),
            (h, 'avise em uma frase, escreva "sem o conector" na\nlinha "Gerada" da ficha e preencha', "preencha"),
            # 1.3.3 (avaliador, ciclo 2): B7 manda parar quando o verificador reprova; S5 manda o DESIGN dizer onde se lê a view
            ("spec-make-build/SKILL.md", "se ele reprovar, não crie o fluxo; diga o problema e indique a",
             "se ele reprovar, crie o fluxo mesmo assim; diga o problema e indique a"),
            ("spec-make-design/SKILL.md", "O DESIGN diz que a pessoa lê a view da taxa de correção no\nSQL Editor do Supabase",
             "O DESIGN não diz onde a pessoa lê a view da taxa de correção no\nSQL Editor do Supabase"),
            # 1.3.1 (S3): valor do filtro em texto e filtro "existe" depois da busca, na âncora do design
            ("spec-make-design/SKILL.md", 'vai em texto (`"false"`, nunca o booleano `false`:',
             'vai em booleano (`false`, nunca o texto `"false"`:'),
            ("spec-make-design/SKILL.md", "Sem pendente, a busca devolve 1 pacote vazio:", "Sem pendente, a busca devolve nada:"),
        ]
        for arq, de, para in casos:
            with self.subTest(arquivo=arq, de=de[:40]):
                texto = (RAIZ / "skills" / arq).read_text(encoding="utf-8")
                n, mut = trocar(texto, de, para)
                self.assertEqual(n, 1, "trecho do mutante não achado (ou achado mais de uma vez) no texto real")
                erros = [e for r in REGRAS if r.arquivo == arq for e in checar_texto(r, mut)]
                self.assertTrue(erros, "regra invertida passou")

    def test_handoff_sem_jargao(self):
        """AT-007 (R5 da review do DESIGN do s3): "transversal" e "Etapa 5" fora do frontmatter de todo .md do handoff
        reprovam; o frontmatter (metadata.fase) não conta."""
        pasta = RAIZ / "skills" / "spec-make-handoff"
        for arq in sorted(pasta.rglob("*.md")):
            with self.subTest(arquivo=arq.relative_to(pasta).as_posix()):
                self.assertEqual(jargao(arq.read_text(encoding="utf-8")), [])
        sk = (pasta / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn('fase: "transversal"', sk)
        self.assertTrue(jargao(sk.replace("## Quick start", "## Quick start\n\nEsta skill é transversal.", 1)))
        self.assertTrue(jargao(sk + "\nspec-make · Etapa 5 de 5 — Handoff\n"))

    def test_frases_dos_arquivos_de_referencia(self):
        for arq in FRASES:
            with self.subTest(arquivo=arq):
                self.assertEqual(checar_frases(arq, (RAIZ / "skills" / arq).read_text(encoding="utf-8")), [])

    def test_regra_invertida_nos_arquivos_de_referencia_reprova(self):
        """Avaliador ciclo 4 (achado 2): as 8 inversões de 1 edição nos arquivos de referência; avaliador fresco do s3,
        ciclo 2 (B9): o passo 9 da build, fora das âncoras."""
        g, pr = "spec-make-design/references/GOVERNANCA_DO_FLUXO.md", "spec-make-design/references/PROMPTS_DE_IA.md"
        v = "spec-make-define/references/VERIFY_GATE_EXECUCAO.md"
        casos = [(g, "**Sem o passo:** recuse o DESIGN", "**Sem o passo:** aceite o DESIGN"),
                 (g, "**Sem a chave:** recuse o DESIGN como pronto e peça a chave.", "**Sem a chave:** aceite o DESIGN como pronto."),
                 (pr, "| versão | v1 |\n", ""),
                 (v, '"O blueprint foi validado" como teste: recuse', '"O blueprint foi validado" como teste: aceite'),
                 (v, "Fluxo que grava sem a segunda execução: recuse como incompleto.",
                  "Fluxo que grava sem a segunda execução: aceite como completo."),
                 (v, "sem dado pessoal real; origem", "pode usar dado real de cliente; origem"),
                 ("spec-make-build/references/PROTOCOLO.md", "a contagem não pode mudar", "a contagem pode mudar"),
                 # R2@opus (1b): a linha "Gatilho real" também aceita a 2ª execução mais barata; R1@codex (1b): o teste da fila é isolado
                 ("spec-make-build/references/PROTOCOLO.md", "(operações maiores que zero; ela pode gastar menos que a 1ª): execução que não processou nada",
                  "(operações maiores que zero, iguais às da 1ª): execução que não processou nada"),
                 ("spec-make-build/references/PROTOCOLO.md",
                  "a condição `chave_natural` igual a `TESTE-1` (as duas condições juntas), para o teste nunca ler nem marcar",
                  "a condição `chave_natural` igual a `TESTE-1` (ou nenhuma), para o teste ler e marcar"),
                 # R2@opus (rodada 2): o mutante do passo 10 (não da linha "Gatilho real") também reprova
                 ("spec-make-build/references/PROTOCOLO.md",
                  "(operações maiores que zero; ela pode gastar menos que a 1ª). Execução que não processou nada também gasta 1",
                  "(operações maiores que zero, iguais às da 1ª). Execução que não processou nada também gasta 1"),
                 # R1@opus (rodada 2): ligar de verdade sem tirar o filtro de teste
                 ("spec-make-build/references/PROTOCOLO.md", "no mesmo `scenarios_update` tire a condição `TESTE-1` do `searchRows`",
                  "no mesmo `scenarios_update` troque a agenda"),
                 ("spec-make-build/references/PROTOCOLO.md", "o destino segue com 1 linha com essa chave",
                  "o destino pode ter qualquer contagem"),
                 ("spec-make-design/references/SUPABASE.md", "and format_type(a.atttypid, a.atttypmod) <> 'numeric(18,2)'))) then",
                  "and format_type(a.atttypid, a.atttypmod) <> 'numeric(18,0)'))) then"),
                 # R2@codex (rodada 2): a conferência da fila preexistente sem a coluna do marcador
                 ("spec-make-design/references/SUPABASE.md", "where a.attrelid = 'public.<fila>'::regclass and a.attname = 'processado_em'",
                  "where a.attrelid = 'public.<fila>'::regclass and a.attname = 'processado'"),
                 # 1.3.3: verificador obrigatório no build e leitura da view no SQL Editor
                 ("spec-make-build/references/PROTOCOLO.md", "o verificador é obrigatório; se ele reprovar, não crie o fluxo:",
                  "o verificador é opcional; se ele reprovar, crie o fluxo:"),
                 ("spec-make-design/references/SUPABASE.md", "A pessoa lê essa view no SQL Editor do Supabase",
                  "A pessoa não lê essa view no SQL Editor do Supabase"),
                 # 1.3.1: o teste de ponta a ponta achou o filtro booleano e o pacote vazio
                 ("spec-make-build/references/PROTOCOLO.md",
                  "Faça ainda a **3ª execução com a fila vazia**: ela termina em sucesso e gasta exatamente 1 operação",
                  "Faça ainda a **3ª execução com a fila cheia**: ela termina em sucesso e gasta exatamente 1 operação"),
                 ("spec-make-build/references/PROTOCOLO.md",
                  "Com fila, rode também uma 3ª execução com a fila vazia: ela termina em sucesso e gasta exatamente 1 operação.",
                  "Com fila, não precisa de 3ª execução."),
                 ("spec-make-design/references/SUPABASE.md", "com o booleano `false` o Make ignora a condição",
                  "com o booleano `false` o Make aplica a condição"),
                 ("spec-make-design/references/SUPABASE.md", "devolve **1 pacote vazio** (não zero)",
                  "devolve **nenhum pacote** (zero)"),
                 # R1@codex (rodada 2): o filtro de teste é a chave exata, não "contém"
                 ("spec-make-design/references/SUPABASE.md", "a condição `chave_natural` *Equals* `TESTE-1`",
                  "a condição `chave_natural` contém `TESTE-`"),
                 ("spec-make-build/references/DIAGNOSTICO.md", "Correções só no fluxo que esta conversa criou ([B4]).",
                  "Correções em qualquer fluxo da conta."),
                 ("spec-make-handoff/references/PROTOCOLO.md", "Nunca troque o `lastEdit` da ficha",
                  "Troque o `lastEdit` da ficha"),
                 ("spec-make-handoff/references/PROTOCOLO.md", "a ficha mantém o `lastEdit` antigo",
                  "a ficha passa a ter o `lastEdit` da conta"),
                 # avaliador fresco do s3, ciclo 2 (B9): o passo 9 da build sem os ids lidos agora e a sessão
                 ("spec-make-build/SKILL.md", "com os ids\n   lidos agora e esta sessão no histórico ", ""),
                 ("spec-make-build/SKILL.md",
                  "9. **Fichas.** Preencha a ficha do fluxo e o handoff — `HANDOFF_<FLUXO>.md` pela skill "
                  "`spec-make-handoff`, com os ids\n   lidos agora e esta sessão no histórico — e feche",
                  "9. **Fichas.** Preencha a ficha do fluxo e feche")]
        for arq, de, para in casos:
            with self.subTest(arquivo=arq, de=de[:40]):
                texto = (RAIZ / "skills" / arq).read_text(encoding="utf-8")
                n, mut = trocar(texto, de, para)
                self.assertEqual(n, 1, "trecho do mutante não achado (ou achado mais de uma vez) no texto real")
                self.assertTrue(checar_frases(arq, mut), "regra invertida passou")

    def test_ancora_ausente_reprova(self):
        r = REGRAS[0]
        texto = (RAIZ / "skills" / r.arquivo).read_text(encoding="utf-8").replace(f"**[{r.ancora}] ", "**[Z9] ")
        self.assertNotEqual(checar_texto(r, texto), [])


if __name__ == "__main__":
    unittest.main()
