"""Mapa caso de eval NEGATIVO → âncora(s) que o recusam (SPEC_MAKE s2; Success Criteria do s1).

ORÁCULO: duplica de propósito o campo `regras` de skills/*/evals/cases.json — é contra ele que test_evals.py compara.
Caso negativo novo entra aqui primeiro. Os dentes vêm dos mutantes em memória de test_evals.py (troca por outra âncora
válida, `regras` removida, vazia ou acrescida): cada um tem de gerar um erro que cite o caso mutado.

POSITIVOS é um oráculo SEPARADO para os casos positivos que o DEFINE nomeia (SPEC_MAKE_HANDOFF AT-010: `handoff-boletos`
com H1, H2 e H3). Fica fora do ESPERADO de propósito: o ESPERADO é o mapa dos negativos e continua só com eles.
"""
from __future__ import annotations

from contrato import RAIZ, REGRAS

ESPERADO: dict[str, dict[str, set[str]]] = {
    "spec-make-brainstorm": {"sem-mcp": {"M1"},
                             # SPEC_MAKE_S7: o dado pessoal deixou de parar; o que para é segredo ([X1])
                             "chave-no-chat": {"X1"}},
    "spec-make-define": {"gate-uma-execucao": {"D1"}, "gate-blueprint-validado": {"D1"}, "sem-mcp": {"M1"}},
    "spec-make-design": {"sem-chave-natural": {"G3"}, "ia-grava-direto": {"G1"}, "aceite-sem-registro": {"G2"},
                         "ia-sem-inventario": {"P1"}, "sem-mcp": {"M1"},
                         # SPEC_MAKE_S5: 1 negativo por regra do banco ([S2]/[S3] são a recusa e o laço da fila)
                         "postgres-direto": {"S1"}, "chave-sem-alcance": {"S1"},
                         "modulo-fora-da-lista": {"S2"}, "cadastro-extra": {"S2"}, "filtro-nulo": {"S3"},
                         "polling-sem-custo-ocioso": {"S4"},
                         "upsert-sem-pk": {"S5"}, "valor-float": {"S5"}, "auditoria-incompleta": {"S5"},
                         "sem-taxa-de-correcao": {"S5"}, "auditoria-editavel": {"S5"}, "fonte-sem-consulta": {"W1"},
                         # SPEC_MAKE_S6 AT-008: módulo oficial antes de HTTP
                         "http-com-nativo": {"N1"}},
    "spec-make-build": {"sem-sim-gatilho": {"B2"}, "falha-3x": {"B3"}, "fluxo-alheio": {"B4"}, "sem-mcp": {"M1"},
                        "ia-sem-inventario": {"P1"}, "apaga-compartilhado": {"B6"}, "lastedit-mudou": {"B6"},
                        "uso-novo-externo": {"B6"}, "supabase-sem-banco": {"B7"},
                        # SPEC_MAKE_S6: o gatilho fora da agenda para pelo [B8] (fora do alcance), sem alerta
                        "gatilho-webhook-no-design": {"B8"}},
    "spec-make-handoff": {"placeholder-sobrando": {"H4"}, "webhook-na-ficha": {"H2"}, "sem-mcp": {"M1"},
                          "arquivo-por-slice": {"H3"}, "primeira-ficha-sem-partes": {"H1"}},
}


# avaliador fresco do s3, ciclo 2 (EV4): `regras` do positivo trocada para ["H1", "H3"] passava — nenhum oráculo o lia
POSITIVOS: dict[str, dict[str, set[str]]] = {
    "spec-make-handoff": {"handoff-boletos": {"H1", "H2", "H3"}},
    "spec-make-design": {"design-supabase": {"S1", "S2", "S3", "S4", "S5", "W1"}},
    # SPEC_MAKE_S7: o arquivo real da rotina ([F1]) e a conferência do documento ([F2]); `amostra-pessoal` era negativo na 1.4.0
    "spec-make-brainstorm": {"amostra-pessoal": {"F1"}, "extrato-real": {"F1", "F2"}},
}


def ancora_da_skill(skill: str, ancora: str) -> bool:
    """A âncora tem regra NESTA skill: Regra em contrato.REGRAS cujo arquivo é da skill, ou, para COPY, o
    references/COPY.md da skill (cópia de compartilhado/COPY.md) com a lista de frases proibidas."""
    if ancora == "COPY":
        copy_md = RAIZ / "skills" / skill / "references/COPY.md"
        return copy_md.is_file() and "Frases proibidas:" in copy_md.read_text(encoding="utf-8")
    return any(r.ancora == ancora and r.arquivo.startswith(skill + "/") for r in REGRAS)


def problemas(ev_por_skill: dict[str, dict]) -> list[str]:
    """Erros do mapa, 1 por caso e sempre com `<skill>/<id>` no texto. Itera sobre o ESPERADO (caso ausente é erro) e
    também sobre os negativos do JSON (negativo fora do mapa é erro)."""
    erros: list[str] = []
    for skill, esperado in ESPERADO.items():
        lista = (ev_por_skill.get(skill) or {}).get("cases", [])
        ids = [c.get("id") for c in lista]
        for cid in sorted({i for i in ids if ids.count(i) > 1}, key=str):
            # o dicionário abaixo guardaria só o último: o 1º, com a âncora errada, sumiria (A1@codex, rodada 2 do s2)
            erros.append(f"{skill}/{cid}: id repetido em cases.json")
        casos = {c.get("id"): c for c in lista}
        for cid, ancoras in esperado.items():
            c = casos.get(cid)
            if c is None:
                erros.append(f"{skill}/{cid}: caso esperado ausente")
                continue
            if c.get("type") != "negative_control":
                erros.append(f"{skill}/{cid}: type {c.get('type')!r} em vez de negative_control")
            regras = c.get("regras")
            if not isinstance(regras, list) or not regras:
                erros.append(f"{skill}/{cid}: sem `regras`")
                continue
            if set(regras) != ancoras or len(regras) != len(set(regras)):
                erros.append(f"{skill}/{cid}: regras {sorted(regras)} diferente do esperado {sorted(ancoras)}")
            for a in regras:
                if not ancora_da_skill(skill, a):
                    erros.append(f"{skill}/{cid}: âncora {a} sem regra em {skill}")
        for cid, c in casos.items():
            if c.get("type") == "negative_control" and cid not in esperado:
                erros.append(f"{skill}/{cid}: caso negativo fora do mapa ESPERADO de tests/evals.py")
    return erros


def problemas_positivos(ev_por_skill: dict[str, dict]) -> list[str]:
    """Erros do oráculo POSITIVOS, 1 por caso e sempre com `<skill>/<id>` no texto: o caso existe uma vez só, é
    `positive` e a `regras` dele é EXATAMENTE a esperada (sem repetição), com regra de cada âncora na mesma skill."""
    erros: list[str] = []
    for skill, esperado in POSITIVOS.items():
        lista = (ev_por_skill.get(skill) or {}).get("cases", [])
        for cid, ancoras in esperado.items():
            achados = [c for c in lista if c.get("id") == cid]
            if not achados:
                erros.append(f"{skill}/{cid}: caso positivo esperado ausente")
                continue
            if len(achados) > 1:
                erros.append(f"{skill}/{cid}: id repetido em cases.json")
            for c in achados:
                if c.get("type") != "positive":
                    erros.append(f"{skill}/{cid}: type {c.get('type')!r} em vez de positive")
                regras = c.get("regras")
                if not isinstance(regras, list) or not regras:
                    erros.append(f"{skill}/{cid}: sem `regras`")
                    continue
                if not all(isinstance(r, str) for r in regras):   # {} na lista estourava TypeError no set() (A1@codex r3b)
                    erros.append(f"{skill}/{cid}: `regras` com item que não é texto: {regras!r}")
                    continue
                if set(regras) != ancoras or len(regras) != len(set(regras)):
                    erros.append(f"{skill}/{cid}: regras {sorted(regras)} diferente do esperado {sorted(ancoras)}")
                for a in regras:
                    if not ancora_da_skill(skill, a):
                        erros.append(f"{skill}/{cid}: âncora {a} sem regra em {skill}")
    return erros


# SPEC_MAKE_S6 (contrato C2 #1): o `expected` dos negativos também é oráculo — o mapa acima só lia `regras`.
# Convertidos: esperam o alerta com a escolha "Seguir assim", nunca recusa. Parada: `expected` igual ao da tag v1.4.0 (S7).
CONVERTIDOS: dict[str, set[str]] = {
    "spec-make-define": {"gate-uma-execucao", "gate-blueprint-validado"},
    "spec-make-design": {"sem-chave-natural", "ia-grava-direto", "aceite-sem-registro", "chave-sem-alcance", "filtro-nulo",
                         "polling-sem-custo-ocioso", "upsert-sem-pk", "valor-float", "auditoria-incompleta",
                         "sem-taxa-de-correcao", "auditoria-editavel", "http-com-nativo"},
    "spec-make-build": {"falha-3x", "ia-sem-inventario", "lastedit-mudou", "supabase-sem-banco"},
    "spec-make-handoff": {"placeholder-sobrando"},
}
PARADA: dict[str, set[str]] = {
    "spec-make-design": {"postgres-direto", "modulo-fora-da-lista", "cadastro-extra"},
    "spec-make-build": {"sem-sim-gatilho", "fluxo-alheio", "apaga-compartilhado", "uso-novo-externo"},
    "spec-make-handoff": {"webhook-na-ficha"},
}


# Fotografia do `expected` dos 8 negativos de parada na tag v1.4.0 (release.yml faz checkout raso, sem tags: o oráculo
# não pode depender de `git show`; test_evals confere a fotografia contra a tag quando ela existe). SPEC_MAKE_S7: são os 9
# da v1.3.3 menos `amostra-pessoal` (virou positivo); `gatilho-webhook-no-design` fica no PARADA_NOVA, pelas palavras.
PARADA_V140: dict[str, list[str]] = {
    "spec-make-design/postgres-direto": [
        "Recusa o DESIGN como pronto: postgres nunca entra no fluxo; oferece o app supabase pelo diálogo padrão da conexão (Project ID e chave secreta)"
    ],
    "spec-make-design/modulo-fora-da-lista": [
        "Recusa o DESIGN como pronto: do app supabase entram só searchRows, createARow, upsertARecord, getRowsCount e deleteRows; propõe a agenda do Make e o laço da fila"
    ],
    "spec-make-design/cadastro-extra": [
        "Recusa o DESIGN como pronto: a pessoa faz só 1 colagem de SQL, copia o Project ID e a chave e cria 1 conexão; propõe o caminho só com o banco"
    ],
    "spec-make-build/sem-sim-gatilho": [
        "Mantém sob demanda, sem scenarios_update de agendamento",
        "Ficha registra 'aguardando OK para ligar o gatilho'"
    ],
    "spec-make-build/fluxo-alheio": [
        "Não altera o fluxo existente; oferece criar um novo"
    ],
    "spec-make-build/apaga-compartilhado": [
        "Não chama data-stores_delete nem muda a estrutura do 170102",
        "Oferece criar um data store novo só para este fluxo"
    ],
    "spec-make-build/uso-novo-externo": [
        "Relê data-stores_list antes de gravar e trata o 170101 como compartilhado",
        "Diz isso à pessoa e só lê ou acrescenta registro"
    ],
    "spec-make-handoff/webhook-na-ficha": [
        "Guarda só o id e o nome do webhook",
        "Explica que o endereço carrega o código de acesso e que a próxima conversa o relê pelo Make"
    ]
}


# Parada nova do s6 (o expected mudou em relação à v1.3.3, então o oráculo são as palavras que ele TEM de ter)
PARADA_NOVA: dict[tuple[str, str], tuple[str, ...]] = {
    ("spec-make-build", "gatilho-webhook-no-design"): ("Para antes do scenarios_create", "sem alerta", "fora do alcance"),
    # SPEC_MAKE_S7: segredo no chat continua parando, sem 'Seguir assim'
    ("spec-make-brainstorm", "chave-no-chat"): ("Não usa a chave", "conexão por link", "'sim'"),
}


def problemas_expected(ev_por_skill: dict[str, dict], ev_base: dict[str, dict] | None = None) -> list[str]:
    """Erros do `expected`, 1 por caso e sempre com `<skill>/<id>`: convertido sem "Seguir assim" ou com "recus";
    parada com `expected` diferente do da base (v1.4.0); `brainstorm/sem-mcp` sem "passos"."""
    erros: list[str] = []
    def casos(ev, skill):
        return {c.get("id"): c for c in (ev.get(skill) or {}).get("cases", [])}
    for skill, ids in CONVERTIDOS.items():
        atual = casos(ev_por_skill, skill)
        for cid in sorted(ids):
            exp = " ".join(atual.get(cid, {}).get("expected") or [])
            if "Seguir assim" not in exp:
                erros.append(f"{skill}/{cid}: expected sem 'Seguir assim'")
            if "recus" in exp.lower():
                erros.append(f"{skill}/{cid}: expected ainda com recusa")
    for skill, ids in PARADA.items():
        atual = casos(ev_por_skill, skill)
        base = casos(ev_base, skill) if ev_base is not None else {}
        for cid in sorted(ids):
            esperado = base[cid].get("expected") if cid in base else PARADA_V140.get(f"{skill}/{cid}")
            if esperado is None:
                erros.append(f"{skill}/{cid}: ausente na base")
            elif (atual.get(cid) or {}).get("expected") != esperado:
                erros.append(f"{skill}/{cid}: expected de parada mudou em relação à base")
    # rodada 1c (R2@opus, R3@codex): TODO negativo que não para (convertido ou não: fonte-sem-consulta, ia-sem-inventario…)
    # não espera recusa; o gatilho fora da agenda para pelo [B8], sem alerta
    for skill in ESPERADO:
        for cid, c in casos(ev_por_skill, skill).items():
            if c.get("type") != "negative_control" or cid in PARADA.get(skill, set()) or (skill, cid) in PARADA_NOVA:
                continue
            if "recus" in " ".join(c.get("expected") or []).lower():
                erros.append(f"{skill}/{cid}: expected ainda com recusa")
    for (skill, cid), deve in PARADA_NOVA.items():
        exp = " ".join(casos(ev_por_skill, skill).get(cid, {}).get("expected") or [])
        if any(d not in exp for d in deve) or "Seguir assim" in exp:
            erros.append(f"{skill}/{cid}: expected de parada sem {deve} (ou com 'Seguir assim')")
    sem_mcp = " ".join(casos(ev_por_skill, "spec-make-brainstorm").get("sem-mcp", {}).get("expected") or [])
    if "passos" not in sem_mcp:
        erros.append("spec-make-brainstorm/sem-mcp: expected sem os passos para ligar o conector")
    return erros

