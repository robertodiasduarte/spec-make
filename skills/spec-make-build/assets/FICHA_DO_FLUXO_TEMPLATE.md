# Ficha do fluxo — {nome do fluxo}

> spec-make · {data} · documentos: BRAINSTORM_{FLUXO}.md · DEFINE_{FLUXO}.md · DESIGN_{FLUXO}.md

## O que ele faz

{1 a 3 frases, em linguagem de escritório}

## Quando roda

{sob demanda · todo dia às … · quando chega …} · Gatilho: {ligado em {data} com o OK de {quem} | aguardando OK para ligar o gatilho}

## Onde ele está

Make → Cenários → {nome} · {link} · organização {nome} · equipe {nome}

## Quanto custa

{n} operações por execução · cerca de {n} por mês · plano {nome} com {limite}/mês

## Conexões que ele usa

| Conexão | App | Se expirar |
|---|---|---|
| {nome} | {app} | Make → Conexões → {nome} → Reautorizar |

## Quando ele falhar

| O que você vê | O que fazer |
|---|---|
| E-mail do Make "execução incompleta" | Abra o fluxo → Histórico → a execução marcada; o erro diz o módulo |
| Erro de conexão | Reautorize a conexão (tabela acima) e rode de novo a execução incompleta |
| Resultado errado sem erro | Pare o gatilho, rode a amostra do DEFINE e compare; volte à etapa de design se o desenho estiver errado |
| Fluxo desativado sozinho | O Make desativa depois de {maxErrors} falhas seguidas; corrija a causa e ative de novo |

## Proteções que já vêm no fluxo

- Confidencial: o Make não guarda os dados de cada passo no histórico.
- {Chave natural: rodar de novo o mesmo item não duplica registro (chave = …)}
- {Aceite humano e registro do aceite, se houver IA}

## Teste de aceite

Amostra e resultado esperado: ver DEFINE_{FLUXO}.md. Último teste: {data} · execução {id} · {resultado}.
