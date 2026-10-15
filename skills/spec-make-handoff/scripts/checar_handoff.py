#!/usr/bin/env python3
"""Confere uma ficha HANDOFF_<FLUXO>.md antes de entregá-la ou de retomar por ela.

Uso:
    python3 checar_handoff.py <HANDOFF.md>

Sai 0 quando não há problema, 1 quando há (um por linha, com a seção) e 2 quando o arquivo não pode ser lido.
Não acessa a rede nem a conta do Make: confere só o texto da ficha.

O que confere:
  1. as quatro seções obrigatórias, cada uma com o título exato (a data da leitura vai na linha de baixo);
  2. trecho de modelo sobrando: «…» ou {…} (fórmula do Make, {{…}}, não conta);
  3. URL de webhook do Make (o endereço carrega o código de acesso: a ficha guarda só o id);
  4. sequência de 11 ou mais dígitos (pode ser CPF ou CNPJ; o id de execução e o sha256 vão em grupos de 8 com hífen);
  5. linha do inventário sem id numérico;
  6. ficha gerada sem o conector que afirma custódia ou lastEdit no inventário (lá, tudo é "a confirmar na conta").

Biblioteca padrão; Python 3.9+.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SECOES = ("## Ficha", "## Inventário e custódia", "## Prompt de retomada", "## Histórico de sessões")
PLACEHOLDER = re.compile(r"«|»|(?<!\{)\{[A-Za-zÀ-ú_][^{}]*\}(?!\})")
WEBHOOK = re.compile(r"hook\.[a-z0-9]+\.make\.com/")
DIGITOS = re.compile(r"[0-9]{11,}")
LINHA_INV = re.compile(r"^\|\s*(Cenário|Webhook|Data store|Conexão)\s*\|\s*([^|]*)\|")
ID_OK = re.compile(r"^\s*\d+(\s*·\s*\d+)*\s*$")
A_CONFIRMAR = "a confirmar na conta"
SEM_CONECTOR = re.compile(r"^\|\s*Gerada\s*\|[^|]*sem o conector", re.M)
AFIRMA = re.compile(r"desta família|compartilhado com|lastEdit \d")


def problemas(texto: str) -> list[str]:
    p = [f"seção ausente: {s}" for s in SECOES if not re.search(rf"^{re.escape(s)}\s*$", texto, re.M)]
    sem_conector = SEM_CONECTOR.search(texto) is not None
    secao = "(topo)"
    for n, linha in enumerate(texto.splitlines(), 1):
        if linha.startswith("## "):
            secao = linha[3:].strip()
        if PLACEHOLDER.search(linha):
            p.append(f"{secao}: placeholder sobrando na linha {n}")
        if WEBHOOK.search(linha):
            p.append(f"{secao}: URL de webhook na linha {n} — guarde só o id (a próxima conversa relê com hooks_get)")
        if DIGITOS.search(linha):
            p.append(f"{secao}: sequência de 11+ dígitos na linha {n} — use grupos de 8 com hífen ou apague")
        m = LINHA_INV.match(linha)
        if m:
            celula = m.group(2).strip()
            if not ID_OK.match(celula) and not (sem_conector and celula == A_CONFIRMAR):
                p.append(f"{secao}: {m.group(1)} sem id numérico na linha {n}")
            if sem_conector and AFIRMA.search(linha):
                p.append(f"{secao}: ficha sem o conector afirma custódia ou lastEdit na linha {n} — use '{A_CONFIRMAR}'")
    return p


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("uso: checar_handoff.py <HANDOFF.md>")
        return 2
    try:
        texto = Path(argv[1]).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"não consegui ler {argv[1]}: {e}")
        return 2
    erros = problemas(texto)
    print("\n".join(erros) if erros else "ok: ficha completa, sem trecho de modelo, sem segredo e com id em todo recurso")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
