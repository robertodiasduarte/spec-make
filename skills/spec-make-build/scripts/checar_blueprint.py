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
  3. não há credencial escrita no blueprint: chave, token, senha, cabeçalho Authorization, chave ou usuário:senha
     na URL, inclusive dentro de corpo JSON escrito como texto. O nome exato "key" (data store) não é credencial.

Este arquivo é igual nas skills spec-make-design e spec-make-build.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ENTRADA = "scenario-service:StartSubscenario"

TOKEN = re.compile(r"(sk-[A-Za-z0-9_-]{16,}|eyJ[A-Za-z0-9_-]{20,}\.|-----BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16})")
# Marcadores no NOME normalizado (minúsculas, sem "-", "_", "." nem espaço) de campo, cabeçalho ou parâmetro de query:
# "app_key", "Ocp-Apim-Subscription-Key", "client_secret", "x-api-key" contêm um deles. O nome exato "key" fica de
# fora: é a chave do registro no data store do Make, não credencial (na URL, "?key=" continua sendo).
MARCADORES = ("secret", "password", "passwd", "passphrase", "authpass", "senha", "token", "apikey", "appkey",
              "accesskey", "subscriptionkey", "privatekey", "authorization", "clientsecret")
# Nome de campo que guarda ENDEREÇO ("token_url", "authorization_endpoint"): só nele um https://… sem credencial
# passa. Em "password": "https://…" o valor é a senha (A2 do auditor, rodada 3b).
ENDERECO = ("url", "uri", "endpoint", "href", "link")
PREFIXO = re.compile(r"^(Bearer|Basic|Token)\s+\S{6,}", re.I)
NA_URL = re.compile(r"[?&]([A-Za-z0-9_.\-\[\]]+)=(?!\{\{)([^&\s\"#]{6,})")
# usuário:senha antes do host: https://usuario:senha@api.exemplo.com
USUARIO_SENHA = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^/\s:@\"]+:([^/\s@\"]+)@")
# par "nome": "valor" num corpo JSON que não se deixa ler (ex.: {{1.n}} sem aspas no meio)
PAR_JSON = re.compile(r'"([^"\\]{1,80})"\s*:\s*"((?:[^"\\]|\\.)*)"')


def _normalizado(nome: str) -> str:
    return re.sub(r"[-_.\s]", "", nome.lower())


def nome_de_credencial(nome: object) -> bool:
    """Nome de campo, cabeçalho ou parâmetro que guarda credencial. "key" sozinho não conta (data store)."""
    if not isinstance(nome, str):
        return False
    n = _normalizado(nome)
    return n != "key" and any(m in n for m in MARCADORES)


def _na_url(texto: str) -> bool:
    """Credencial na URL: parâmetro de query com nome de credencial (ou "key") e valor fixo, ou usuário:senha."""
    for m in NA_URL.finditer(texto):
        if nome_de_credencial(m.group(1)) or _normalizado(m.group(1)) == "key":
            return True
    return any(_sem_mapeamento(m.group(1)) for m in USUARIO_SENHA.finditer(texto))


MAPEAMENTO = re.compile(r"\{\{.*?\}\}", re.S)


def _sem_mapeamento(valor: str) -> str:
    """O texto que sobra quando se tiram os mapeamentos do Make ({{3.chave}}) e o prefixo de esquema (Bearer/Basic)."""
    resto = MAPEAMENTO.sub("", valor).strip()
    return re.sub(r"^(Bearer|Basic|Token)\b\s*", "", resto, flags=re.I).strip()


def _literal(valor: object) -> bool:
    """Valor escrito à mão: sobram 6+ caracteres fixos depois de tirar os mapeamentos. "{{3.chave}}" e
    "Bearer {{4.token}}" não são literais; "segredo-fixo{{emptystring}}" é (achado A2 da review)."""
    return isinstance(valor, str) and len(_sem_mapeamento(valor)) >= 6


def _como_json(texto: str) -> object | None:
    """Corpo JSON escrito como texto (bodyType raw): o objeto lido, ou None quando o texto não começa com { ou [.
    Se não se deixa ler (mapeamento sem aspas no meio), devolve CADA par "nome": "valor" achado no texto como um item
    separado — nunca achatado num dicionário, onde um par posterior de mesmo nome apagaria o anterior (A1 do auditor,
    rodada 3b)."""
    t = texto.strip()
    if not t.startswith(("{", "[")) or t.startswith("{{"):
        return None
    try:
        return json.loads(t)
    except ValueError:
        return [{"name": m.group(1), "value": m.group(2)} for m in PAR_JSON.finditer(t)] or None


def _palavras(nome: str) -> list[str]:
    """token_url → [token, url]; securityToken → [security, token]; authorizationEndpoint → [authorization, endpoint]."""
    return [w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+", nome)]


def _nome_de_endereco(nome: object) -> bool:
    """Endereço por PALAVRA, não por pedaço: "security_password" contém "uri" mas não é endereço (R5@opus, rodada 4)."""
    return isinstance(nome, str) and any(w in ENDERECO for w in _palavras(nome))


def _url_sem_credencial(valor: object) -> bool:
    """Endereço sem usuário:senha nem chave na query ("token_url": "https://…/token") não é credencial."""
    return isinstance(valor, str) and bool(re.match(r"^https?://\S+$", valor.strip())) and not _na_url(valor)


def credenciais_literais(no: object) -> list[str]:
    """Onde há credencial escrita: chave de objeto com nome de credencial, par {name, value} de cabeçalho ou de
    query, valor com prefixo Bearer/Basic/Token, token em formato conhecido, chave na URL, usuário:senha na URL
    ou qualquer um desses dentro de um corpo JSON escrito como texto."""
    achados: list[str] = []

    def suspeito(nome: object, valor: object, par: bool = False) -> bool:
        # par = {name, value} de cabeçalho ou query, ou campo de um corpo HTTP escrito como texto: aí "key" é credencial
        # (como "?key=" na URL — R3@opus 3b; o mesmo nos dois jeitos de ler o corpo — R4@opus 4). Só a chave de objeto do
        # próprio blueprint (o "key" do módulo de data store) fica de fora.
        credencial = nome_de_credencial(nome) or (par and isinstance(nome, str) and _normalizado(nome) == "key")
        isento = _nome_de_endereco(nome) and _url_sem_credencial(valor)
        return credencial and _literal(valor) and not isento

    def andar(x: object, caminho: str, corpo: bool = False) -> None:
        if isinstance(x, dict):
            nome = x.get("name") if isinstance(x.get("name"), str) else x.get("key")
            if "value" in x and suspeito(nome, x.get("value"), par=True):
                achados.append(f"{caminho}.{nome}")
            for k, v in x.items():
                if suspeito(k, v, par=corpo):
                    achados.append(f"{caminho}.{k}")
                andar(v, f"{caminho}.{k}", corpo)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                andar(v, f"{caminho}[{i}]", corpo)
        elif isinstance(x, str):
            # Token conhecido e chave na URL valem até DENTRO de uma expressão {{…}} (R1@opus, rodada 2): só o
            # teste de "texto fixo" (prefixo de esquema) desconta os mapeamentos.
            if (PREFIXO.match(x.strip()) and len(_sem_mapeamento(x)) >= 6) or TOKEN.search(x) or _na_url(x):
                achados.append(caminho)
            lido = _como_json(x)
            if lido is not None:
                andar(lido, f"{caminho}<json>", corpo=True)

    andar(no, "$")
    return list(dict.fromkeys(achados))


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
