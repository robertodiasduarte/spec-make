#!/usr/bin/env python3
"""Confere um blueprint do Make antes de criar o fluxo.

Uso:
    python3 checar_blueprint.py <blueprint.json>

Sai 0 quando não há problema e 1 quando há (cada problema numa linha). Sai 2 quando o arquivo
não é um JSON legível. Não acessa a rede nem a conta do Make: confere só o texto do blueprint.

O que confere (o que os validadores do MCP do Make não pegam):
  0. o blueprint tem `flow`: uma lista com pelo menos um módulo (objeto com `module` em texto não vazio; sem ele, nada
     seria conferido e a saída seria "OK");
  1. metadata.scenario.confidential é true;
  2. fluxo sob demanda com entrada (scenario-service:StartSubscenario) declara os campos no módulo 1 e NÃO
     traz a chave `interface` no blueprint (o validador do Make a recusa; ela é gravada com scenarios_set-interface);
  3. não há credencial escrita no blueprint: chave, token, senha, cabeçalho Authorization, chave ou usuário:senha
     na URL, inclusive dentro de corpo JSON ou de formulário escrito como texto e dentro de fórmula {{…}}. O nome
     exato "key" como chave de objeto (data store) não é credencial; em cabeçalho, query ou corpo em texto, é;
  4. o Supabase entra só como banco ([S1] e [S2] da skill de design): do app `supabase` passam apenas `searchRows`,
     `createARow`, `upsertARecord`, `getRowsCount` e `deleteRows` (lista PERMITIDA: módulo novo do app reprova);
     `supabase-management` e `postgres` reprovam; e qualquer outro módulo cujo mapeamento traga o endereço de um
     projeto Supabase (o domínio do projeto, terminado em `.co`, `/functions/v1/`, `/rest/v1/`, `/graphql/v1`, `/storage/v1/`, `/auth/v1/`,
     sem diferenciar maiúsculas de minúsculas, inclusive dentro de fórmula) reprova. A conferência olha os módulos de
     todas as rotas do roteador e dos tratadores de erro. Endereço montado por pedaços entre módulos e domínio próprio
     do Supabase (sem o domínio padrão do projeto) não são reconhecidos.

Alcance declarado: credencial reconhecida pelo NOME (MARCADORES, NOMES_DE_PAR) ou pelo FORMATO (TOKEN), em texto ou número. Um segredo com
nome neutro e formato desconhecido não é detectado: a defesa principal é a conexão do Make, nunca o texto do blueprint.
Nome com palavra de senha ou segredo em QUALQUER posição ("senha_certificado", "X-Senha-Certificado", "api_password")
conta a partir de 1 caractere fixo, salvo quando outra palavra do nome diz que o campo descreve a senha em vez de
guardá-la ("password_type", "token_expires_in", "token_url"); palavra de senha fundida a outra numa palavra só
("senhacertificado") segue o limite de 6 caracteres dos nomes comuns.

Este arquivo é igual nas skills spec-make-design e spec-make-build.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ENTRADA = "scenario-service:StartSubscenario"
# lista PERMITIDA (LM-142): módulo novo do app supabase nasce reprovado
SUPABASE_PERMITIDOS = frozenset({"supabase:searchRows", "supabase:createARow", "supabase:upsertARecord",
                                 "supabase:getRowsCount", "supabase:deleteRows"})
APPS_FORA = ("supabase-management:", "postgres:")
# endereço de projeto Supabase: comparado em minúsculas (o hostname não diferencia caixa) no texto de TODO o mapeamento
# o domínio é casado como DOMÍNIO, não como prefixo de texto: o final ".co" seguido de letra (o painel, que termina em ".com") não conta.
# Em pedaços: o vocabulário privado do publish-gate barra o literal (LM-096).
DOMINIO_PROJETO = re.compile(r"\.supabase" + r"\.co(?![a-z0-9])")
PROJETO_SUPABASE = ("/functions/v1/", "/rest/v1/", "/graphql/v1", "/storage/v1/", "/auth/v1/")

# Credencial em formato conhecido, em qualquer string do blueprint (caminho de URL, cabeçalho genérico, corpo em texto):
# OpenAI, JWT, chave privada, AWS, Stripe, Slack (token e webhook), GitHub, GitLab, Google, bot do Telegram, webhook do
# Discord (avaliador, ciclo 4).
# Âncora de início: nada de letra, dígito ou "_" antes do formato — "helpdesk-chamados" e "network_test_homologacao" não
# são credencial (R1@opus, rodada 7).
TOKEN = re.compile(
    r"(?:(?<![A-Za-z0-9_])|(?<=%[0-9A-Fa-f][0-9A-Fa-f]))"
    r"(sk-[A-Za-z0-9_-]{16,}|eyJ[A-Za-z0-9_-]{20,}\.|-----BEGIN [A-Z ]*PRIVATE KEY|(?:AKIA|ASIA)[0-9A-Z]{16}"
    r"|whsec_[A-Za-z0-9]{20,}|xapp-[0-9A-Za-z-]{10,}|\d{8,10}:AA[A-Za-z0-9_-]{30,}"
    r"|[sr]k_(?:live|test)_[A-Za-z0-9]{10,}|xox[abposr]-[A-Za-z0-9-]{10,}|hooks\.slack\.com/services/[A-Za-z0-9/]{20,}"
    r"|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|glpat-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}"
    r"|bot\d{6,}:[A-Za-z0-9_-]{30,}|discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]{20,})")
# Marcadores no NOME normalizado (minúsculas, sem "-", "_", "." nem espaço) de campo, cabeçalho ou parâmetro de query:
# "app_key", "Ocp-Apim-Subscription-Key", "client_secret", "x-api-key" contêm um deles. O nome exato "key" fica de
# fora: é a chave do registro no data store do Make, não credencial (na URL, "?key=" continua sendo).
MARCADORES = ("secret", "password", "passwd", "passphrase", "authpass", "senha", "token", "apikey", "appkey",
              "accesskey", "subscriptionkey", "privatekey", "authorization", "clientsecret", "pwd", "authkey",
              "chaveapi", "apichave", "chavesecreta", "chaveprivada", "apphash", "credential", "credencial",
              "accesscode", "sessionid")
# Em cabeçalho, parâmetro de query e corpo HTTP em texto, o NOME EXATO "key", "chave" ou "pass" também é credencial
# (avaliador, ciclo 3; "X-Auth-Key", "chave-api" e "pwd" já caem nos MARCADORES), e "auth"/"X-Auth" (ciclo 4). Por nome exato, não por palavra:
# "sort_key", "partitionKey" e "X-Pass-Through" não são credencial (R4@opus, rodada 6). Fora desses pares (chave de objeto
# do blueprint) não: "key" é a chave do registro no data store. "cookie" também por nome exato: "X-Cookie-Consent" e
# "accept_cookies" não são credencial (R2@opus, rodada 7).
NOMES_DE_PAR = ("key", "chave", "pass", "auth", "xauth", "cookie")
# Nome de campo que guarda ENDEREÇO ("token_url", "authorization_endpoint"): só nele um https://… sem credencial
# passa. Em "password": "https://…" o valor é a senha (A2 do auditor, rodada 3b).
ENDERECO = ("url", "uri", "endpoint", "href", "link")
# O valor inteiro é "esquema + 1 credencial": "Token expirado: renove a conexão" é frase, não credencial (ciclo 5).
PREFIXO = re.compile(r"^(Bearer|Basic|Token)\s+\S{6,}\s*$", re.I)
NA_URL = re.compile(r"[?&]([A-Za-z0-9_.\-\[\]]+)=(?!\{\{)([^&\s\"#]+)")
# usuário:senha antes do host: https://usuario:senha@api.exemplo.com
USUARIO_SENHA = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^/\s:@\"]+:([^/\s@\"]+)@")
# corpo de formulário escrito como texto: nome=valor&nome=valor
FORM = re.compile(r"^[A-Za-z0-9_.\-\[\]]+=[^&]*(?:&[A-Za-z0-9_.\-\[\]]+=[^&]*)*$")
# par "nome": "valor" num corpo JSON que não se deixa ler (ex.: {{1.n}} sem aspas no meio)
PAR_JSON = re.compile(r'"([^"\\]{1,80})"\s*:\s*(?:"((?:[^"\\]|\\.)*)"|(-?\d[\d.]*))')


def _normalizado(nome: str) -> str:
    return re.sub(r"[-_.\s]", "", nome.lower())


# Palavra comum que CONTÉM um marcador sem ser credencial (avaliador, ciclo 5): fica de fora da busca por pedaço. Por
# começo ou fim da palavra: "secretariaFazenda", "resenhas", "max_tokens"/"maxtokens".
PALAVRA_COMUM = ("secretari", "secretary", "resenha", "maxtoken", "tokeniz")
# Nome de senha, segredo ou Authorization: qualquer valor fixo não vazio é credencial ("senha": 1234 — ciclo 6). Nos
# outros nomes, menos de 6 caracteres fixos não conta (evita reprovar "true", "json", "v1"): limite declarado no manifest.
FORTES = ("senha", "password", "passwd", "pwd", "pass", "secret", "passphrase", "authorization")
# Campo de duração ou limite: número ali é medida, não credencial ("token_expires_in": 2592000 — R2@opus, rodada 8).
MEDIDA = {"expires", "expire", "expiry", "expiration", "ttl", "limit", "limite", "max", "min", "age", "timeout",
          "budget", "qtd", "quantidade", "total", "num", "count", "usage", "uso", "contagem",
          "length", "size", "count", "seconds", "minutes", "hours", "days", "lifetime", "validity", "validade"}


def _palavra_comum(p: str) -> bool:
    return any(p.startswith(c) or p.endswith(c) for c in PALAVRA_COMUM)


def nome_de_credencial(nome: object) -> bool:
    """Nome de campo, cabeçalho ou parâmetro que guarda credencial. O marcador vale como PEDAÇO de cada palavra
    ("secretkey", "tokenacesso", "credentials" — R1@opus e A1, rodada 8) e de 2 ou 3 palavras juntas ("app_key" →
    appkey, "Ocp-Apim-Subscription-Key" → subscriptionkey), menos nas palavras comuns de PALAVRA_COMUM ("secretaria",
    "resenha", "max_tokens" — avaliador, ciclo 5). Última palavra "cookie" também é credencial ("auth_cookie",
    "X-Session-Cookie"; "X-Cookie-Consent" não — R3@opus, rodada 8). "key" sozinho não conta (data store)."""
    if not isinstance(nome, str):
        return False
    w = _palavras(re.sub(r"[-_.\s]+", " ", nome))
    if w == ["key"] or not w:
        return False
    if w[-1] == "cookie":
        return True
    # junto de palavra de medida ("max_tokens", "token_limit"), "token" é unidade, não credencial; sozinho ou no plural
    # ("api_tokens", "X-Tokens"), é credencial (ciclo 6)
    marcadores = [m for m in MARCADORES if not (m == "token" and MEDIDA & set(w))]
    return any(m in p for p in _pedacos(w) for m in marcadores)


def _pedacos(w: list[str]) -> list[str]:
    """Cada palavra e as junções de 2 e 3 palavras, menos as palavras comuns de PALAVRA_COMUM."""
    todos = w + [a + b for a, b in zip(w, w[1:])] + [a + b + c for a, b, c in zip(w, w[1:], w[2:])]
    return [p for p in todos if not _palavra_comum(p)]


# Palavra que descreve a senha em vez de guardá-la ("password_type", "secret_encoding", "secret_name", "token_url"):
# junto de uma palavra de FORTES, o nome volta ao limite de 6 (SPEC_MAKE s2). Por PALAVRA inteira, nunca por pedaço.
# "hash", "reset", "arquivo" e "file" ficam de fora: "password_hash", "senha_reset" e "senha_arquivo" (a do certificado
# A1, .pfx) guardam um segredo (R1@opus, rodada 1 do s2).
CONFIGURACAO = {"type", "tipo", "encoding", "codificacao", "policy", "politica", "hint", "dica", "required",
                "obrigatorio", "obrigatoria", "enabled", "habilitado", "field", "campo", "format", "formato", "mode",
                "modo", "strength", "forca", "rule", "rules", "regra", "regras", "label", "rotulo", "placeholder",
                "length", "tamanho", "name", "nome", "id", "ref", "arn", "path"}
DESCRITIVA = CONFIGURACAO | MEDIDA | set(ENDERECO)


def _forte(p: str) -> bool:
    """"senha", "passwords", "dbpwd", "apisenha": a palavra é de senha, segredo ou Authorization. "pass" só conta como
    palavra inteira: "dbpass" e "userpass" nem chegam aqui, porque "pass" não é marcador de nome (bypass, passagem)."""
    return any(p.rstrip("s").endswith(f) or p == f for f in FORTES)


def _minimo(nome: object) -> int:
    """Caracteres fixos a partir dos quais o valor é credencial: 1 quando ALGUMA palavra do nome é de senha/segredo/
    Authorization, em qualquer posição ("senha_certificado", "X-Senha-Certificado", "pwd_certificado", "secret_key",
    "password_hash" — avaliador, ciclo 7) e NENHUMA descreve a senha ("password_type", "secret_encoding", "token_url":
    6, como os nomes comuns — A2, rodada 9). Palavra forte no FIM conta sempre, como na v1.0.0 ("pfx_file_password",
    "nome_senha"): a regra nova só amplia a anterior (R1@opus, rodada 1 do s2). Palavra comum ("secretaria",
    "resenha") não conta como forte."""
    if isinstance(nome, str):
        w = [p for p in _palavras(re.sub(r"[-_.\s]+", " ", nome)) if not _palavra_comum(p)]
        if w and _forte(w[-1]):
            return 1
        if any(_forte(p) for p in w) and not DESCRITIVA & set(w):
            return 1
    return 6


def nome_de_credencial_em_par(nome: object) -> bool:
    """Nome de cabeçalho, parâmetro de query ou campo de corpo HTTP em texto que guarda credencial."""
    if not isinstance(nome, str):
        return False
    return nome_de_credencial(nome) or _normalizado(nome) in NOMES_DE_PAR


def _na_url(texto: str) -> bool:
    """Credencial na URL: parâmetro de query com nome de credencial (ou "key") e valor fixo, ou usuário:senha. Confere
    o texto como está e com cada expressão {{…}} trocada pelo texto fixo dela (?key={{"abc123…"}})."""
    for t in dict.fromkeys((texto, _resolvido(texto))):
        for m in NA_URL.finditer(t):
            if nome_de_credencial_em_par(m.group(1)) and len(m.group(2)) >= _minimo(m.group(1)):
                return True
        if any(_sem_mapeamento(m.group(1)) for m in USUARIO_SENHA.finditer(t)):
            return True
    return False


EXPRESSAO = re.compile(r"\{\{(.*?)\}\}", re.S)
ASPAS = re.compile(r'"((?:[^"\\]|\\.)*)"')
# Referência a dado de outro módulo ou variável: 1.chave, 3.data[].token, var.input.cnpj, 1.`Nome do campo`, 3.códigoAcesso.
# Só começa pelo número do módulo ou por "var": "senha.2026" escrito à mão não é referência (R1@opus, rodada 5); \w
# aceita acento (R3@opus, rodada 5).
REFERENCIA = re.compile(r"\b(?:\d+|var)(?:\.(?:`[^`]*`|[\w\[\]]+))+")
# Texto entre aspas que é operando de comparação ({{if(1.ambiente = "producao"; …)}}) não chega ao valor: não conta como
# texto fixo (R2@opus, rodada 5).
COMPARADO = re.compile(r'(?:(?:!=|<>|<=|>=|=|<|>)\s*"(?:[^"\\]|\\.)*")|(?:"(?:[^"\\]|\\.)*"\s*(?:!=|<>|<=|>=|=|<|>))')
FUNCAO = re.compile(r"\b[A-Za-z_]\w*\s*\(")
PALAVRAS_DO_MAKE = {"emptystring", "emptyarray", "null", "true", "false", "now", "timestamp", "pi", "space", "nbsp",
                    "tab", "newline", "carriagereturn", "random", "uuid"}


def _fixo_da_expressao(expr: str) -> str:
    """O texto fixo de dentro de uma expressão do Make: o que está entre aspas ({{"abc123"}}) e o argumento escrito
    sem aspas ({{base64(usuario:senha)}}). Referências (1.chave), nomes de função, separadores e palavras do Make
    (emptystring) não contam. Achado 1 do avaliador, ciclo 2: o que estava dentro de {{…}} era descartado inteiro."""
    expr = COMPARADO.sub(" ", expr)
    fixos = ASPAS.findall(expr)
    resto = FUNCAO.sub(" ", REFERENCIA.sub(" ", ASPAS.sub(" ", expr)))
    for p in re.split(r"[\s();,+*/<>=!&|]+", resto):
        if p and p.lower() not in PALAVRAS_DO_MAKE and not (p.isdigit() and len(p) < 6):
            fixos.append(p)
    return "".join(fixos)


def _resolvido(valor: str) -> str:
    """O valor com cada expressão {{…}} trocada pelo texto fixo dela: "Bearer {{4.token}}" → "Bearer ";
    'Bearer {{"abc123def"}}' → "Bearer abc123def"."""
    return EXPRESSAO.sub(lambda m: _fixo_da_expressao(m.group(1)), valor)


def _sem_mapeamento(valor: str) -> str:
    """O texto fixo que sobra quando se tiram os mapeamentos do Make ({{3.chave}}), mantendo o texto fixo de dentro
    das expressões ({{"abc123"}}, {{base64(usuario:senha)}}), e o prefixo de esquema (Bearer/Basic)."""
    resto = _resolvido(valor).strip()
    return re.sub(r"^(Bearer|Basic|Token)\b\s*", "", resto, flags=re.I).strip()


def _literal(valor: object, minimo: int = 6) -> bool:
    """Valor escrito à mão: sobram 6+ caracteres fixos depois de tirar os mapeamentos. "{{3.chave}}" e
    "Bearer {{4.token}}" não são literais; "segredo-fixo{{emptystring}}" é (achado A2 da review), e também
    '{{ifempty(1.chave; "abc123def")}}' e '{{"abc123def"}}' (avaliador, ciclo 2)."""
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        # número também é valor escrito à mão: "senha": 98765432 (avaliador, ciclo 5)
        return len(str(valor).lstrip("-")) >= minimo
    if isinstance(valor, list):
        # valor em lista: "api_keys": ["abc123…"] (ciclo 6)
        return any(_literal(x, minimo) for x in valor if not isinstance(x, (bool, dict, list)))
    if not isinstance(valor, str):
        return False
    fixo = _sem_mapeamento(valor)
    if minimo < 6 and "{{" in valor:
        # nome forte com fórmula: conta letra ou dígito, não a pontuação dela (base64(1.usuario + ":" + 1.senha)); sem
        # fórmula, o valor inteiro conta, inclusive senha só de símbolos (R1, rodada 9)
        return sum(c.isalnum() for c in fixo) >= minimo
    return len(fixo) >= minimo


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
        return [{"name": m.group(1), "value": m.group(2) if m.group(3) is None else m.group(3)}
                for m in PAR_JSON.finditer(t)] or None


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
        credencial = nome_de_credencial_em_par(nome) if par else nome_de_credencial(nome)
        isento = _nome_de_endereco(nome) and _url_sem_credencial(valor)
        if isinstance(valor, (int, float)) and isinstance(nome, str) and MEDIDA & set(_palavras(re.sub(r"[-_.]+", " ", nome))):
            return False
        if credencial and isinstance(nome, str) and _palavras(re.sub(r"[-_.]+", " ", nome))[-1:] == ["cookie"] \
                and isinstance(valor, str):
            # Cookie: nome=valor; nome2=valor2 — o nome do cookie é fixo por natureza; o que conta é o valor de cada par.
            # Parte SEM "=" conta inteira (R2@codex, rodada 7: "Cookie: <literal>" escapava). Lido depois de resolver as
            # fórmulas, para o texto fixo de dentro de {{…}} contar.
            partes = _resolvido(valor).split(";")
            # o mínimo de cada parte segue o nome dela: "senha=1234" conta com mínimo 1 (A1, rodada 9)
            return any(_literal(p.partition("=")[2], _minimo(p.partition("=")[0].strip())) if "=" in p else _literal(p)
                       for p in partes)
        return credencial and _literal(valor, _minimo(nome)) and not isento

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
            if (PREFIXO.match(_resolvido(x).strip()) and len(_sem_mapeamento(x)) >= 6) or TOKEN.search(x) or _na_url(x):
                achados.append(caminho)
            lido = _como_json(x)
            if lido is not None:
                andar(lido, f"{caminho}<json>", corpo=True)
            elif FORM.match(x.strip()):
                # corpo x-www-form-urlencoded escrito como texto: client_secret=…&grant_type=… (avaliador, ciclo 3)
                pares = [{"name": n, "value": v} for n, _, v in (par.partition("=") for par in x.strip().split("&"))]
                andar(pares, f"{caminho}<form>", corpo=True)

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


def problemas_supabase(m: dict) -> list[str]:
    """O Supabase entra só como banco: lista permitida do app, nada de supabase-management/postgres, nada de endereço
    de projeto fora do app (SPEC_MAKE_S5, [S1] e [S2])."""
    nome = str(m.get("module") or "")
    if nome.startswith("supabase:"):
        if nome in SUPABASE_PERMITIDOS:
            return []
        return [f"o módulo {nome} não está entre os do banco (searchRows, createARow, upsertARecord, getRowsCount, "
                "deleteRows): o fluxo usa o Supabase só como banco ([S2])"]
    saida = []
    if nome.startswith(APPS_FORA):
        saida.append(f"o módulo {nome} abre o banco inteiro ou todos os projetos: use o app supabase ([S1])")
    texto = json.dumps(m.get("mapper") or {}, ensure_ascii=False).lower()
    if DOMINIO_PROJETO.search(texto) or any(t in texto for t in PROJETO_SUPABASE):
        saida.append(f"o módulo {nome} traz o endereço de um projeto Supabase: use os módulos do app supabase ([S2])")
    return saida


def problemas_busca_supabase(fluxo: list) -> list[str]:
    """Duas armadilhas medidas na 1.3.0 do kit (teste de ponta a ponta de 16/10/2026): (1) o valor do filtro de
    verdade/falso do `searchRows` tem de ir em texto, o booleano faz o Make ignorar a condição; (2) sem pendente a busca
    devolve 1 pacote vazio, então o módulo seguinte precisa do filtro "existe" sobre o id da busca."""
    saida: list[str] = []
    for i, m in enumerate(fluxo):
        if not isinstance(m, dict) or m.get("module") != "supabase:searchRows":
            continue
        for grupo in (m.get("mapper") or {}).get("search") or []:
            for cond in grupo if isinstance(grupo, list) else []:
                if isinstance(cond, dict) and str(cond.get("o", "")).startswith("boolean:") \
                        and isinstance(cond.get("b"), bool):
                    saida.append(
                        f"o searchRows (módulo {m.get('id')}) filtra {cond.get('a')!r} com o booleano {cond.get('b')!r}: "
                        'escreva o valor em texto ("true" ou "false"), senão o Make ignora a condição e a busca lê qualquer linha')
        if i + 1 >= len(fluxo) or not isinstance(fluxo[i + 1], dict):
            continue
        seguinte = fluxo[i + 1]
        if str(seguinte.get("module", "")).startswith("builtin:") and not str(seguinte.get("module")).endswith(
                ("SetVariable", "SetVariables")):
            continue                      # roteador, agregador e iterador tratam o pacote vazio por conta própria
        marca = "{{" + str(m.get("id")) + "."
        existe = any(isinstance(c, dict) and c.get("o") == "exist" and marca in str(c.get("a", ""))
                     for g in ((seguinte.get("filter") or {}).get("conditions") or []) if isinstance(g, list) for c in g)
        if not existe:
            saida.append(
                f"o módulo {seguinte.get('id')} vem logo depois do searchRows (módulo {m.get('id')}) sem o filtro "
                f'"{marca}id}}}} existe": com a fila vazia a busca devolve 1 pacote vazio e este módulo roda com campos vazios')
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

    fluxo = bp.get("flow")
    tem_modulo = isinstance(fluxo, list) and any(
        isinstance(m, dict) and isinstance(m.get("module"), str) and m["module"].strip() for m in fluxo)
    if not tem_modulo:
        problemas.append("o blueprint não tem flow (lista de módulos): nada foi conferido; exporte o blueprint de novo")
    modulos = _modulos(fluxo if isinstance(fluxo, list) else [])
    problemas += problemas_busca_supabase(fluxo if isinstance(fluxo, list) else [])
    if "interface" in bp:
        problemas.append(
            "o blueprint traz a chave interface: o validador do Make a recusa; grave a interface com "
            "scenarios_set-interface depois de criar o fluxo"
        )
    for m in modulos:
        campos = (m.get("metadata") or {}).get("interface") if m.get("module") == ENTRADA else None
        for c in campos if isinstance(campos, list) else []:
            if isinstance(c, dict) and nome_de_credencial(c.get("name")):
                problemas.append(
                    f"o módulo de entrada pede o campo {c.get('name')!r}, que é credencial: ela viria pelo chat e pela "
                    "entrada da execução; use a conexão do Make (R1@opus, rodada 6)"
                )
        problemas += problemas_supabase(m)
        if m.get("module") == ENTRADA and not ((m.get("metadata") or {}).get("interface")):
            problemas.append(
                "o módulo de entrada (StartSubscenario) não declara os campos em metadata.interface: sem eles a "
                "interface do fluxo fica vazia e o teste falha com 'Validation failed for 1 parameter(s)'"
            )

    onde = credenciais_literais(bp)
    if onde:
        problemas.append(
            "há credencial escrita no blueprint (chave, token, senha ou cabeçalho Authorization) em "
            + ", ".join(onde[:3]) + ": use a conexão do Make (credential-requests_create); nunca peça a credencial no "
            "chat nem a ponha na entrada do fluxo"
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
