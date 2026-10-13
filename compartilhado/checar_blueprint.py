#!/usr/bin/env python3
"""Confere um blueprint do Make antes de criar o fluxo.

Uso:
    python3 checar_blueprint.py <blueprint.json>

Sai 0 quando não há problema e 1 quando há (cada problema numa linha). Sai 2 quando o arquivo
não é um JSON legível. Não acessa a rede nem a conta do Make: confere só o texto do blueprint.

O que confere (as três coisas que os validadores do MCP do Make não pegam):
  1. metadata.scenario.confidential é true;
  2. fluxo sob demanda com entrada (scenario-service:StartSubscenario) declara os campos no módulo 1 e NÃO
     traz a chave `interface` no blueprint (o validador do Make a recusa; ela é gravada com scenarios_set-interface);
  3. não há credencial escrita no blueprint: chave, token, senha, cabeçalho Authorization, chave na URL.

Este arquivo é igual nas skills spec-make-design e spec-make-build.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ENTRADA = "scenario-service:StartSubscenario"

TOKEN = re.compile(r"(sk-[A-Za-z0-9_-]{16,}|eyJ[A-Za-z0-9_-]{20,}\.|-----BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16})")
CAMPO = re.compile(
    r"^(authorization|proxy-authorization|x-api-key|x-auth-token|api[_-]?key|apikey|access[_-]?token|token|"
    r"secret|client[_-]?secret|password|senha)$",
    re.I,
)
PREFIXO = re.compile(r"^(Bearer|Basic|Token)\s+\S{6,}", re.I)
NA_URL = re.compile(r"[?&](api[_-]?key|apikey|access[_-]?token|token|key|secret)=(?!\{\{)[^&\s\"]{6,}", re.I)


MAPEAMENTO = re.compile(r"\{\{.*?\}\}", re.S)


def _sem_mapeamento(valor: str) -> str:
    """O texto que sobra quando se tiram os mapeamentos do Make ({{3.chave}}) e o prefixo de esquema (Bearer/Basic)."""
    resto = MAPEAMENTO.sub("", valor).strip()
    return re.sub(r"^(Bearer|Basic|Token)\b\s*", "", resto, flags=re.I).strip()


def _literal(valor: object) -> bool:
    """Valor escrito à mão: sobram 6+ caracteres fixos depois de tirar os mapeamentos. "{{3.chave}}" e
    "Bearer {{4.token}}" não são literais; "segredo-fixo{{emptystring}}" é (achado A2 da review)."""
    return isinstance(valor, str) and len(_sem_mapeamento(valor)) >= 6


def credenciais_literais(no: object) -> list[str]:
    """Onde há credencial escrita: chave de objeto com nome de credencial, par {name, value} de cabeçalho ou de
    query, valor com prefixo Bearer/Basic/Token, token em formato conhecido ou chave na URL."""
    achados: list[str] = []

    def andar(x: object, caminho: str) -> None:
        if isinstance(x, dict):
            nome = x.get("name") if isinstance(x.get("name"), str) else x.get("key")
            if isinstance(nome, str) and CAMPO.match(nome) and _literal(x.get("value")):
                achados.append(f"{caminho}.{nome}")
            for k, v in x.items():
                if isinstance(k, str) and CAMPO.match(k) and _literal(v):
                    achados.append(f"{caminho}.{k}")
                andar(v, f"{caminho}.{k}")
        elif isinstance(x, list):
            for i, v in enumerate(x):
                andar(v, f"{caminho}[{i}]")
        elif isinstance(x, str):
            fixo = MAPEAMENTO.sub("", x)
            if (PREFIXO.match(x.strip()) and len(_sem_mapeamento(x)) >= 6) or TOKEN.search(fixo) or NA_URL.search(fixo):
                achados.append(caminho)

    andar(no, "$")
    return achados


def _modulos(flow: list) -> list[dict]:
    """Todos os módulos, inclusive os de rotas de roteador e de tratamento de erro."""
    saida: list[dict] = []
    for m in flow or []:
        if not isinstance(m, dict):
            continue
        saida.append(m)
        for rota in m.get("routes") or []:
            if isinstance(rota, dict):
                saida += _modulos(rota.get("flow") or [])
        saida += _modulos(m.get("onerror") or [])
    return saida


def checar(bp: dict) -> list[str]:
    problemas: list[str] = []
    if not isinstance(bp, dict):
        return ["o arquivo não é um blueprint (esperado um objeto JSON)"]

    cenario = ((bp.get("metadata") or {}).get("scenario") or {})
    if cenario.get("confidential") is not True:
        problemas.append(
            "metadata.scenario.confidential precisa ser true: os dados do escritório não ficam no histórico do Make"
        )

    modulos = _modulos(bp.get("flow") or [])
    if "interface" in bp:
        problemas.append(
            "o blueprint traz a chave interface: o validador do Make a recusa; grave a interface com "
            "scenarios_set-interface depois de criar o fluxo"
        )
    for m in modulos:
        if m.get("module") == ENTRADA and not ((m.get("metadata") or {}).get("interface")):
            problemas.append(
                "o módulo de entrada (StartSubscenario) não declara os campos em metadata.interface: sem eles a "
                "interface do fluxo fica vazia e o teste falha com 'Validation failed for 1 parameter(s)'"
            )

    onde = credenciais_literais(bp)
    if onde:
        problemas.append(
            "há credencial escrita no blueprint (chave, token, senha ou cabeçalho Authorization) em "
            + ", ".join(onde[:3]) + ": use a conexão do Make"
        )

    return problemas


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("uso: python3 checar_blueprint.py <blueprint.json>")
        return 2
    try:
        bp = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"não consegui ler o blueprint: {e}")
        return 2
    problemas = checar(bp)
    if problemas:
        for p in problemas:
            print(f"PROBLEMA: {p}")
        return 1
    print("OK: confidencial ligado, interface de entrada no lugar e nenhuma credencial escrita.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
