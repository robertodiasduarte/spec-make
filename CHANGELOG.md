# Changelog

## v1.1.0 — 2026-10

- Skill nova `spec-make-handoff`: guarda a ficha do fluxo para continuar depois — um arquivo por fluxo, com os números
  de cada cenário, webhook, data store e conexão lidos na sua conta (sem gravar nada), o que a próxima conversa pode
  alterar, o que já foi testado, o que falta, e a frase para retomar numa conversa nova. Serve também para um fluxo
  criado direto no Make.
- A etapa 4 passa a entregar também a ficha para continuar depois, e pode mudar um fluxo que já está na conta quando a
  ficha vem anexada: antes de gravar, confere se alguém mexeu no fluxo depois da ficha e se algum recurso passou a ser
  usado por outro fluxo.
- A etapa 3, com a ficha anexada, desenha a mudança sobre o que já existe em vez de um fluxo novo.

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
