# Changelog

## v1.0.1 — 2026-10

- A conferência do blueprint passa a pegar senha escrita em campo com nome em qualquer ordem (senha_certificado,
  senha_api, pwd_certificado, secret_key, cabeçalho X-Senha-Certificado), inclusive senha curta ou numérica.
  Campo que descreve a senha (password_type, secret_encoding) continua aceito.
- Os casos de teste das skills passam a ser conferidos contra a regra que cada um cita.

## v1.0.0 — 2026-10

- Primeira versão: quatro skills, uma por etapa (spec-make-brainstorm, spec-make-define, spec-make-design,
  spec-make-build), para criar fluxos no Make com o MCP do Make.
- Teste de aceite por execução, chave natural contra registro duplicado, aceite humano antes de a IA gravar e
  fluxo sempre confidencial.
