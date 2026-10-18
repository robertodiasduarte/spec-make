#!/usr/bin/env python3
"""Confere um documento do spec-make (BRAINSTORM, DEFINE, DESIGN, recibo ou ficha) antes de entregá-lo.

Uso:
    python3 checar_documento.py <arquivo.md>

Sai 0 sem achado; 1 com ao menos um ERRO (URL de webhook, credencial, CPF, CNPJ ou sequência de 11+ dígitos: segredo ou
dado pessoal inteiro, que o documento não guarda); 3 só com AVISO (e-mail pessoal inteiro); 2 quando o arquivo não pode ser
lido. Cada achado sai numa linha, `ERRO:` ou `AVISO:`, com a seção. O arquivo da pessoa (o extrato, a folha) pode ter o dado
inteiro; o documento que a skill entrega guarda só a estrutura, com exemplo mascarado (regra [F1] de CONDUCAO.md).

O que confere:
  1. URL de webhook do Make (o endereço carrega o código de acesso: o documento guarda só o id);
  2. credencial escrita: token no corpo (Bearer, JWT, sk-, sb_secret_) e campo de segredo (api key, secret, senha, password,
     token) com valor entre aspas ou valor solto de 8+ caracteres com dígito — "API key: autorizada por link" e
     `token: {{1.token}}` não casam;
  3. CPF inteiro (123.456.789-01 ou 123456789-01) e CNPJ inteiro (12.345.678/0001-90 ou 12345678/0001-90);
  4. sequência de 11 ou mais dígitos (pode ser CPF, CNPJ ou chave de nota; o id de execução e o sha256 vão em grupos de 8
     com hífen);
  5. AVISO: e-mail pessoal inteiro (gmail, hotmail, outlook, yahoo, live, icloud, uol, bol, terra).
Exceção: a linha com `(CNPJ público)` não conta CNPJ nem os 14 dígitos dela (companhia aberta); CPF, e-mail e credencial da
mesma linha continuam sendo achados.

Biblioteca padrão; Python 3.9+.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

WEBHOOK = re.compile(r"hook\.[a-z0-9]+\.make\.com/")
CPF = re.compile(r"(?<![0-9])(?:[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}|[0-9]{9}-[0-9]{2})(?![0-9])")
CNPJ = re.compile(r"(?<![0-9])(?:[0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2}|[0-9]{8}/[0-9]{4}-[0-9]{2})(?![0-9])")
DIGITOS = re.compile(r"(?<![0-9])[0-9]{11,}(?![0-9])")
CNPJ_PUBLICO = "(CNPJ público)"
CREDENCIAL = re.compile(      # token no corpo do texto
    r"(?i:\bBearer)\s+[A-Za-z0-9._~+/=-]{20,}|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.|\bsk-[A-Za-z0-9_-]{20,}"
    r"|\bsb_secret_[A-Za-z0-9_-]{10,}")
CAMPO_SEGREDO = re.compile(   # campo de segredo: entre aspas (JSON) ou valor solto com dígito; `{{1.token}}` e prosa não casam
    r"""(?i)(?<![A-Za-z0-9_])(?:api[_ -]?key|secret|senha|password|token)["']?\s*[:=]\s*"""
    r"""(?:["'][^"'\s{}]{8,}["']|(?=[A-Za-z0-9_+/=.-]*[0-9])[A-Za-z0-9_+/=.-]{8,})""")
EMAIL_PESSOAL = re.compile(
    r"(?i)\b[a-z0-9._%+-]{2,}@(?:gmail|hotmail|outlook|yahoo|live|icloud|uol|bol|terra)\.[a-z.]{2,}\b")


def classificar(texto: str) -> tuple[list[str], list[str]]:
    """(erros, avisos). ERRO = segredo ou dado pessoal inteiro no documento; AVISO = e-mail pessoal inteiro."""
    erros: list[str] = []
    avisos: list[str] = []
    secao = "(topo)"
    for n, linha in enumerate(texto.splitlines(), 1):
        if linha.startswith("## "):
            secao = linha[3:].strip()
        publico = CNPJ_PUBLICO in linha
        base = CNPJ.sub("", linha) if publico else linha
        if WEBHOOK.search(linha):
            erros.append(f"{secao}: URL de webhook na linha {n} — guarde só o id (a próxima conversa relê com hooks_get)")
        if CREDENCIAL.search(linha) or CAMPO_SEGREDO.search(linha):
            erros.append(f"{secao}: credencial escrita na linha {n} — guarde só o id da conexão (ela se autoriza por link)")
        if CPF.search(base):
            erros.append(f"{secao}: CPF inteiro na linha {n} — mascare como ***.123.456-**")
        elif not publico and CNPJ.search(linha):
            erros.append(f"{secao}: CNPJ inteiro na linha {n} — mascare como 12.345.***/****-90")
        elif any(not (publico and len(m.group()) == 14) for m in DIGITOS.finditer(base)):
            erros.append(f"{secao}: sequência de 11+ dígitos na linha {n} — se for número de pessoa ou de nota, mascare pela "
                         "tabela do [F1]; se for id do Make, escreva em grupos de 8 com hífen")
        if EMAIL_PESSOAL.search(linha):
            avisos.append(f"{secao}: e-mail pessoal inteiro na linha {n} — mascare como m***@dominio.com.br")
    return erros, avisos


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("uso: checar_documento.py <documento.md>")
        return 2
    try:
        texto = Path(argv[1]).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"não consegui ler {argv[1]}: {e}")
        return 2
    erros, avisos = classificar(texto)
    for e in erros:
        print(f"ERRO: {e}")
    for a in avisos:
        print(f"AVISO: {a}")
    if not erros and not avisos:
        print("ok: documento sem webhook, credencial, CPF, CNPJ nem sequência de 11+ dígitos")
    return 1 if erros else 3 if avisos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
