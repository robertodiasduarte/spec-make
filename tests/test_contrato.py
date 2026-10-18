"""AT-002…AT-008, AT-011 e MUSTs da UX Review: cada âncora tem o conteúdo exigido e cada asserção morde um mutante."""
from __future__ import annotations

import re
import unittest

import json

import contrato
from contrato import FRASES, RAIZ, REGRAS, bloco, checar, checar_frases, checar_texto, itens_sem_frase, jargao, mutantes


def trocar(texto: str, de: str, para: str) -> tuple[int, str]:
    """(quantas vezes `de` aparece, texto com a troca). A busca ignora a diferença entre espaço e quebra de linha: o
    mutante não depende de onde o Markdown quebrou a linha (SPEC_MAKE_S5)."""
    padrao = re.compile(r"\s+".join(re.escape(x) for x in de.split()))
    return len(padrao.findall(texto)), padrao.sub(lambda _m: para, texto, count=1)


def x1_problemas(texto: str) -> list[str]:
    """SPEC_MAKE_S7: o [X1] tem exatamente 3 itens numerados e nenhuma menção a dado pessoal dentro do bloco."""
    b = bloco(texto, "X1")
    if b is None:
        return ["âncora [X1] ausente"]
    p = []
    itens = re.findall(r"^\d\. ", b, re.M)
    if len(itens) != 3:
        p.append(f"[X1] com {len(itens)} itens (esperado 3)")
    if re.search(r"pessoal|CPF|salário|dado de cliente|nome de pessoa", b, re.I):
        p.append("[X1] menciona dado pessoal")
    return p


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
            # SPEC_MAKE_S6: o teto do [B3] vira "até 4 vezes antes do alerta"; sem "Seguir assim", não corrige
            (d, 'Sem a escolha de\n"Seguir assim", não corrija nem rode de novo', 'Sem a escolha de\n"Seguir assim", corrija e rode de novo'),
            (d, "o teste roda até 4 vezes antes do alerta", "o teste roda até 9 vezes antes do alerta"),
            (p, "7. `scenarios_activate` — necessário para rodar; sob demanda, ele só roda quando alguém pede.\n", ""),
            (p, "Nunca peça chave no chat.", "Peça a chave no chat."),
            (b, "O fluxo é criado com `metadata.scenario.confidential: true`.",
             "O fluxo é criado com `metadata.scenario.confidential: false` (não `confidential: true`)."),
            # SPEC_MAKE_S6: a polaridade nova — "alerta [A1]" trocado por seguir sem alerta reprova
            (ds, "Sem a chave: alerta [A1]", "Sem a chave: siga sem alerta"),
            (ds, "Sem esse passo: alerta\n[A1]", "Sem esse passo: siga sem alerta"),
            (df, "alerta [A1] — os validadores do Make", "siga — os validadores do Make"),
            (b, "alerta [A1] antes do `scenarios_create` — sem o contrato", "siga para o `scenarios_create` — sem o contrato"),
            # rodada 6 (R2/R3@opus): G2, P1 do design e M1 das etapas de papel
            (ds, "Sem esse registro: alerta [A1]", "Sem esse registro: siga sem alerta"),
            (ds, "sem esse inventário: alerta [A1]", "sem esse inventário: siga sem alerta"),
            (ds, "e não declare o blueprint validado", "e declare o blueprint validado"),
            (df, 'ficam "a confirmar na conta" se', 'ficam "a confirmar na conta" mesmo se'),
            ("spec-make-brainstorm/SKILL.md", "Não afirme\nque um app existe", "Afirme\nque um app existe"),
            (b, "Não afirme que criou, rodou ou ligou nada.",
             "Diga que criou e rodou. (Não afirme que criou, rodou ou ligou nada só se pedirem.)"),
            # SPEC_MAKE_S5: a polaridade de cada regra nova, com 1 edição (a busca ignora onde a linha quebra)
            (ds, "e `supabase-management` ficam fora do alcance do kit ([X2]). Sem o alcance",
             "e `supabase-management` podem entrar no fluxo. Sem o alcance"),
            (ds, "ficam fora do alcance do kit ([X2]): diga isso e proponha o caminho só com o banco, sem perguntar.",
             "entram como alerta [A1]: diga isso e proponha o caminho só com o banco, se a pessoa quiser."),
            (ds, "e a pessoa não faz, antes do 1º fluxo rodar, mais que 1 colagem",
             "e a pessoa faz, antes do 1º fluxo rodar, mais que 1 colagem"),
            (ds, "webhook de qualquer tipo, Database Webhook", "webhook com chave de API, Database Webhook"),
            (ds, "Gatilho que não seja a agenda do Make nem a execução sob demanda fica fora do alcance",
             "Gatilho que não seja a agenda do Make nem a execução sob demanda vira alerta, não fica fora do alcance"),
            (ds, "nem a execução sob demanda fica fora", "ou a execução sob demanda fica fora"),
            (ds, "que regrava a linha inteira", "que grava só o que mudou"),
            (ds, "Se o total passar do orçamento do DEFINE: alerta [A1]", "Se o total passar do orçamento do DEFINE: siga"),
            (ds, "o DESIGN declara no bloco `Relógio` como o fluxo dispara", "o DESIGN não declara como o fluxo dispara"),
            (ds, "Chave natural que não é a `primary key` da tabela de destino do `upsertARecord`",
             "Chave natural que é a `primary key` da tabela de destino do `upsertARecord`"),
            (ds, "coluna de valor em `real`, `float4`, `float8` ou `double precision`, rateio sem",
             "coluna de valor em `numeric`, rateio sem"),
            (ds, "auditoria sem o gatilho ou sem a view: alerta [A1]", "auditoria sem o gatilho ou sem a view: siga"),
            (ds, "auditoria sem o gatilho ou sem a view", "auditoria com o gatilho e com a view"),
            (ds, "gravados antes do \"processa\" e nunca recalculados", "gravados depois do \"processa\" e recalculados"),
            (ds, "nunca afirme uma consulta que não fez —", "afirme a consulta mesmo sem ter feito —"),
            # avaliador fresco (W1): consultar a documentação é obrigatório, para cada app
            (ds, "consulte a documentação pública do Make", "pode consultar a documentação pública do Make"),
            (ds, "Para cada app do fluxo, consulte", "Se quiser, consulte"),
            (ds, "consulte a documentação pública do Make", "dispense a documentação pública do Make"),
            (ds, "divergir de `app-modules_list`, vale a conta", "divergir de `app-modules_list`, não vale a conta"),
            (ds, "e o DESIGN anota a divergência", "e o DESIGN não anota a divergência"),
            (ds, "e o DESIGN preenche a coluna", "e o DESIGN não preenche a coluna"),
            # SPEC_MAKE_S6: [B8] para sem alerta; [B7] alerta
            (b, "Pare antes de qualquer `scenarios_create`, sem alerta nem pergunta", "Faça o alerta [A1] antes de qualquer `scenarios_create`"),
            (b, "do app `supabase` algo além de `searchRows`", "do app `supabase` qualquer módulo, inclusive `searchRows`"),
            (b, "gatilho que não seja a agenda do\nMake nem sob demanda: fica fora do alcance do kit", "gatilho por webhook: entra como alerta"),
            (b, "ou módulo `postgres` ou `supabase-management`, ou HTTP para o projeto,",
             "ou HTTP para o projeto (o `postgres` e o `supabase-management` são aceitos),"),
            (b, "Faltando algum: alerta [A1]\nantes de qualquer `scenarios_create`", "Faltando algum: siga sem alerta e crie"),
            # SPEC_MAKE_HANDOFF (s3): H2, B6 (as 2 polaridades) e M1 do handoff
            (h, "Nunca chame `scenarios_create`", "Pode chamar `scenarios_create`"),
            (b, 'siga só depois de a\npessoa escolher "Seguir assim e registrar o alerta"', 'siga mesmo sem a escolha "Seguir assim e registrar o alerta"'),
            (b, "Depois releia `data-stores_list` e `hooks_list` e recalcule a custódia",
             "Não precisa reler `data-stores_list` e `hooks_list` nem recalcular a custódia"),
            (h, "Não afirme `lastEdit`", "Afirme `lastEdit`"),
            # avaliador fresco do s3, ciclo 1 — AT-005 (H2): ler o registro do data store; guardar a URL do webhook
            (h, "`data-stores_delete` nem `data-store-records_list` — o\nregistro de um data store pode guardar senha ou chave.",
             "`data-stores_delete`. Leia `data-store-records_list` para conferir o registro."),
            (h, "do webhook, guarde só o id e o nome", "do webhook, guarde só o id e o nome e também a URL completa"),
            # AT-003 (B6): lastEdit diferente segue sem o "sim"; compartilhado liberado a pedido
            (b, 'se for diferente, diga em 1 frase os dois horários ("editado no Make depois\nda ficha") e faça o alerta [A1]',
             'se for diferente, siga e no fim diga os dois horários ("editado no Make depois da ficha")'),
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
            ("spec-make-build/SKILL.md", "ou 2 (não leu o arquivo: nada foi conferido): não crie o\nfluxo",
             "ou 2 (não leu o arquivo: nada foi conferido): crie o fluxo"),
            # rodada 1b: o [N1] com motivo do módulo não alerta; confidencial e interface se corrigem; o Quick start cita o [X1]
            ("spec-make-build/SKILL.md", "linha de motivo do\n[N1] com o número dele não vira alerta",
             "linha de motivo do [N1] com o número dele vira alerta"),
            ("spec-make-build/SKILL.md", "confidencial desligado e chave `interface` no blueprint você corrige sozinho e avisa",
             "confidencial desligado e chave `interface` no blueprint viram alerta [A1]"),
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
        g, pr = "spec-make-design/references/GOVERNANCA_DO_FLUXO.md", "spec-make-design/references/PROMPTS_E_SKILLS.md"
        v = "spec-make-define/references/VERIFY_GATE_EXECUCAO.md"
        casos = [(g, "**Sem o passo:** alerta [A1]", "**Sem o passo:** aceite o DESIGN"),
                 (g, "**Sem a chave:** alerta [A1]; peça a chave.", "**Sem a chave:** aceite o DESIGN como pronto."),
                 (pr, "| versão | v1 |\n", ""),
                 (v, '"O blueprint foi validado" como teste: alerta [A1]', '"O blueprint foi validado" como teste: aceite'),
                 (v, "Fluxo que grava sem a segunda execução: alerta [A1]", "Fluxo que grava sem a segunda execução: aceite"),
                 (v, "(origem: real, mascarada aqui | inventada | pública)", "(origem: pública | inventada)"),
                 (v, "mascare pela tabela do [F1] e confira pelo [F2]", "use como veio no arquivo"),
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
                 ("spec-make-build/references/PROTOCOLO.md", "o verificador roda em todo fluxo; o que fazer com cada saída",
                  "o verificador roda se der tempo; o que fazer com cada saída"),
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
                 # rodada 1b (R5@opus): o Quick start do build cita os bloqueios [X1]
                 ("spec-make-build/SKILL.md", "está em **[B8]** e nos bloqueios [X1] ([B2], [B4], [B6]); o resto vira alerta.",
                  "está em **[B8]**; o resto vira alerta."),
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

    # ── SPEC_MAKE_S6 ─────────────────────────────────────────────────────────────────────────────────────────────────
    def test_s6_conducao_polaridade(self):
        """Pattern 6: inverter com 1 edição cada regra de CONDUCAO.md reprova (o "sim" solto, um por mensagem, bloqueio)."""
        c = "spec-make-brainstorm/references/CONDUCAO.md"
        casos = [
            (c, "a etapa continua: escreva o alerta", "a etapa termina: escreva o alerta"),
            (c, 'valem "Corrigir agora"', 'valem "Seguir assim e registrar o alerta"'),
            (c, 'Só a escolha de "Seguir assim e registrar o alerta"', "Qualquer resposta"),
            (c, "um por mensagem, o de maior risco primeiro", "todos de uma vez, em qualquer ordem"),
            (c, "A opção recomendada vem primeiro.", "A opção recomendada vem por último."),
            (c, "Cada alerta aceito vira uma linha", "Nenhum alerta aceito vira linha"),
            (c, "nenhuma confirmação os libera", "uma confirmação os libera"),
            (c, "não viram alerta nem pergunta", "viram alerta"),
            (c, "Toda resposta, inclusive a primeira, abre", "Só a primeira resposta abre"),
            (c, "Não pergunte o que o MCP do Make responde", "Pergunte tudo, inclusive o que o MCP do Make responde"),
            (c, "Rollback quando toda gravação do fluxo é idempotente pela chave\nnatural", "Rollback sempre"),
            (c, "e que a ficha não marca como `desta família`", "mesmo que a ficha marque como `desta família`"),
            (c, "a linha tem até 80 caracteres.", "a linha pode ter qualquer tamanho."),
        ]
        for arq, de, para in casos:
            with self.subTest(arquivo=arq, de=de[:40]):
                texto = (RAIZ / "skills" / arq).read_text(encoding="utf-8")
                n, mut = trocar(texto, de, para)
                self.assertEqual(n, 1, "trecho do mutante não achado (ou achado mais de uma vez) no texto real")
                self.assertTrue([e for r in REGRAS if r.arquivo == arq for e in checar_texto(r, mut)], "regra invertida passou")

    def test_s6_cada_alerta_reprova_sem_alerta(self):
        """R7@opus: para TODA frase prendida com "alerta [A1]" (REGRAS e FRASES), trocar a 1ª por "siga sem alerta"
        reprova — sem lista manual, cobre as regras convertidas que existirem."""
        total = 0
        for r in REGRAS:
            for s in r.contem:
                if "alerta [A1]" not in s:
                    continue
                texto = (RAIZ / "skills" / r.arquivo).read_text(encoding="utf-8")
                n, mut = trocar(texto, s, s.replace("alerta [A1]", "siga sem alerta", 1))
                with self.subTest(ancora=r.ancora, arquivo=r.arquivo, frase=s[:50]):
                    self.assertGreaterEqual(n, 1, "frase prendida não achada no texto real")
                    self.assertNotEqual(checar_texto(r, mut), [], "frase de alerta trocada passou")
                    total += 1
        for arq, frases in FRASES.items():
            texto = (RAIZ / "skills" / arq).read_text(encoding="utf-8")
            for s in frases:
                if "alerta [A1]" not in s and "[A3]" not in s:
                    continue
                novo = s.replace("alerta [A1]", "siga sem alerta", 1) if "alerta [A1]" in s else s.replace("[A3]", "nada", 1)
                n, mut = trocar(texto, s, novo)
                with self.subTest(arquivo=arq, frase=s[:50]):
                    self.assertGreaterEqual(n, 1)
                    self.assertTrue(checar_frases(arq, mut), "frase de alerta trocada passou")
                    total += 1
        self.assertGreaterEqual(total, 22)

    def test_s6_itens_do_at004_tem_frase(self):
        """Contrato C2 #3: o conjunto NOMEADO do AT-004, cada um com frase de alerta prendida; tirar uma reprova."""
        self.assertEqual(itens_sem_frase(REGRAS, FRASES), [])
        sem = {k: [s for s in v if "Depois de 3 tentativas" not in s] for k, v in FRASES.items()}
        self.assertEqual(itens_sem_frase(REGRAS, sem), ["validacao-3x"])
        sem_g1 = [r if not (r.ancora == "G1") else contrato.Regra("G1", r.arquivo, contem=r.contem[:-1]) for r in REGRAS]
        self.assertIn("G1", itens_sem_frase(sem_g1, FRASES))

    def test_s6_passos_do_mapa(self):
        """Decision 2 + R9@opus: K = número de passos, passo ≤ 30 caracteres, as 5 skills, e TODA linha composta ≤ 80."""
        texto = (RAIZ / "skills/spec-make-brainstorm/references/CONDUCAO.md").read_text(encoding="utf-8")
        etapas = {"spec-make-brainstorm": "📍 Etapa 1 de 4 · Brainstorm — passo {k} de {K}: {p} · depois: Define",
                  "spec-make-define": "📍 Etapa 2 de 4 · Define — passo {k} de {K}: {p} · depois: Design",
                  "spec-make-design": "📍 Etapa 3 de 4 · Design — passo {k} de {K}: {p} · depois: Build",
                  "spec-make-build": "📍 Etapa 4 de 4 · Build — passo {k} de {K}: {p} · depois: fim",
                  # rodada 1c (A1@fable): o destino do handoff varia; mede com o mais longo (Brainstorm)
                  "spec-make-handoff": "📍 Handoff (fora das etapas) — passo {k} de {K}: {p} · depois: Brainstorm"}
        linhas = {}
        for l in texto.splitlines():
            cel = [x.strip() for x in l.strip().strip("|").split("|")]
            if len(cel) == 3 and cel[0] in etapas:
                linhas[cel[0]] = (int(cel[1]), [x.strip() for x in cel[2].split(" · ")])
        self.assertEqual(set(linhas), set(etapas))
        for s, (k, passos) in linhas.items():
            with self.subTest(skill=s):
                self.assertEqual(k, len(passos))
                for p in passos:
                    self.assertLessEqual(len(p), 30, p)
                    linha = etapas[s].format(k=k, K=k, p=p)
                    self.assertLessEqual(len(linha), 80, linha)
        self.assertGreater(len(etapas["spec-make-brainstorm"].format(k=3, K=8, p="viabilidade na conta")), 80,
                           "o teste não mede a linha composta (o nome antigo dava 81)")

    def test_s6_prerequisitos_com_passos(self):
        """Contrato C2 #5: os 4 pré-requisitos do brainstorm, cada um com ≥2 passos numerados e "A conversa segue"."""
        def problemas(texto: str) -> list[str]:
            erros = []
            for titulo in ("### Conector ausente", "### Conector só de leitura", "### Conexão faltando", "### Sem amostra"):
                if titulo not in texto:
                    erros.append(f"{titulo}: ausente")
                    continue
                corpo = texto.split(titulo, 1)[1]
                corpo = re.split(r"\n#{2,3} ", corpo, maxsplit=1)[0]
                if len(re.findall(r"^\d+\. ", corpo, re.M)) < 2:
                    erros.append(f"{titulo}: menos de 2 passos")
                if "A conversa segue" not in corpo:
                    erros.append(f"{titulo}: sem 'A conversa segue'")
            return erros
        texto = (RAIZ / "skills/spec-make-brainstorm/references/PROTOCOLO.md").read_text(encoding="utf-8")
        self.assertEqual(problemas(texto), [])
        sem = re.sub(r"### Conector só de leitura.*?(?=### Conexão faltando)", "", texto, flags=re.S)
        self.assertTrue(problemas(sem))
        um_passo = texto.replace("2. Confira com a mesma pergunta do caso acima.", "")
        self.assertTrue(problemas(um_passo))

    def test_s7_versao_readme_manifest(self):
        """SPEC_MAKE_S7 AT-008: 1.5.0 exato nas 5; README com as 3 garantias (a primeira agora só de segredo), o arquivo real
        e o "resto a skill avisa"; manifests com a linha dos 3 casos rodados em agente fresco."""
        linha = "1.5.0: só 3 casos do brainstorm (amostra-pessoal, chave-no-chat, extrato-real) foram rodados em agente fresco"
        for s in ("spec-make-brainstorm", "spec-make-define", "spec-make-design", "spec-make-build", "spec-make-handoff"):
            with self.subTest(skill=s):
                sk = (RAIZ / "skills" / s / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn('  version: "1.5.0"', sk)
                man = json.loads((RAIZ / "skills" / s / "manifest.json").read_text(encoding="utf-8"))
                self.assertTrue(any(x.startswith(linha) for x in man["o_que_ainda_nao_prova"]))
        readme = " ".join((RAIZ / "README.md").read_text(encoding="utf-8").split())
        for frase in ("Três coisas a skill nunca faz, nem com a sua confirmação:",
                      "Usar segredo, chave ou endereço de webhook no fluxo, na amostra ou nos documentos",
                      "O seu arquivo real é bem-vindo: anexe o extrato, a nota, a folha ou o CSV da rotina.",
                      "os documentos que ela entrega guardam só a estrutura, com exemplo mascarado",
                      'Ligar o gatilho sem você responder "Ligar agora"',
                      "Apagar ou alterar o que esta conversa não criou, ou o que outro fluxo também usa",
                      "O resto a skill avisa e você decide",
                      '"Corrigir agora" e "Seguir assim e registrar o alerta"'):
            self.assertIn(frase, readme)

    def test_s7_x1_tem_3_itens_e_nenhum_dado_pessoal(self):
        """Contrato C2 #3 (AT-004): dentro de bloco(texto, "X1") há exatamente 3 itens e nenhuma menção a dado pessoal. Os
        mutantes ADITIVOS (um 4º item de dado pessoal; uma frase de dado pessoal no fim do item 1) deixam a âncora do webhook
        intacta: só esta asserção os pega, e sem ela os dois sobrevivem."""
        c = "spec-make-brainstorm/references/CONDUCAO.md"
        texto = (RAIZ / "skills" / c).read_text(encoding="utf-8")
        self.assertEqual(x1_problemas(texto), [])
        aditivos = [
            ("No lugar: criar um novo, só para este fluxo.",
             "No lugar: criar um novo, só para este fluxo.\n4. Dado pessoal real (CPF, nome de pessoa, salário, dado de cliente)."),
            ("conexão autorizada por link, ou só o id.", "conexão autorizada por link, ou só o id. Vale também para CPF e salário."),
        ]
        for de, para in aditivos:
            with self.subTest(de=de[:40]):
                n, mut = trocar(texto, de, para)
                self.assertEqual(n, 1)
                self.assertEqual([e for r in REGRAS if r.arquivo == c and r.ancora == "X1" for e in checar_texto(r, mut)], [],
                                 "o mutante aditivo mexeu na âncora: não prova a asserção negativa")
                self.assertTrue(x1_problemas(mut), "mutante aditivo de dado pessoal passou")

    def test_s7_x1_e_f1_polaridade_nos_dois_sentidos(self):
        """Decision 8 do DESIGN: reinstalar o ⛔ de dado pessoal e afrouxar o ⛔ de segredo reprovam; o [F1] não vira exigência
        de dado limpo nem alerta [A1]. Cada mutante é achado exatamente 1 vez e a regra do arquivo reprova (LM-361)."""
        c = "spec-make-brainstorm/references/CONDUCAO.md"
        casos = [
            # reinstalar o ⛔ de dado pessoal
            ("Segredo, credencial ou endereço de webhook",
             "Segredo, credencial ou dado pessoal real (CPF, nome de pessoa, salário, dado de cliente)"),
            # afrouxar o ⛔ de segredo (some "credencial")
            ("Segredo, credencial ou endereço de webhook", "Dado pessoal ou endereço de webhook"),
            ("nenhuma confirmação os libera", "uma confirmação os libera"),
            ("Nunca peça dado inventado ou público no lugar dele.", "Peça dado inventado ou público no lugar dele."),
            ("Nunca copie linha do arquivo.", "Copie a linha do arquivo."),
            ("Isto é aviso, não alerta [A1].", "Isto é alerta [A1]."),
            ("CNPJ de companhia aberta é público", "CNPJ de cliente é público"),
            ("Dado real só na origem de teste", "Dado real em qualquer fluxo"),
            ("Se o documento anterior diz `origem: real`", "Mesmo sem `origem: real`"),
            ("Saiu 1 (ERRO): não entregue.", "Saiu 1 (ERRO): entregue."),
            ("Saiu 0: entregue.", "Saiu 0: não entregue."),
        ]
        texto = (RAIZ / "skills" / c).read_text(encoding="utf-8")
        for de, para in casos:
            with self.subTest(de=de[:40], para=para[:30]):
                n, mut = trocar(texto, de, para)
                self.assertEqual(n, 1, "trecho do mutante não achado (ou achado mais de uma vez) no texto real")
                self.assertTrue([e for r in REGRAS if r.arquivo == c for e in checar_texto(r, mut)], "regra invertida passou")
        # o [F1] não tem ícone de alerta nem as opções do [A1] (UX MUST-3); a tabela de máscara tem a linha do CPF (UX MUST-6)
        f1 = bloco(texto, "F1")
        self.assertIsNotNone(f1)
        self.assertEqual((f1.count("⚠️"), f1.count("Seguir assim")), (0, 0))
        n, mut = trocar(texto, "Isto é aviso, não alerta [A1].", "⚠️ Isto é aviso, não alerta [A1].")
        self.assertEqual(n, 1)
        self.assertTrue(bloco(mut, "F1").count("⚠️"), "o mutante com o ícone de alerta não foi visto")
        mut = texto.replace("  | CPF | `***.123.456-**` |\n", "", 1)
        self.assertNotEqual(mut, texto)
        self.assertTrue([e for r in REGRAS if r.arquivo == c and r.ancora == "F1" for e in checar_texto(r, mut)])

    def test_ancora_ausente_reprova(self):
        r = REGRAS[0]
        texto = (RAIZ / "skills" / r.arquivo).read_text(encoding="utf-8").replace(f"**[{r.ancora}] ", "**[Z9] ")
        self.assertNotEqual(checar_texto(r, texto), [])


if __name__ == "__main__":
    unittest.main()
