# Changelog

## v1.3.1 — 2026-10

- Duas correções do fluxo que lê uma fila no Supabase, achadas no 1º teste de ponta a ponta com o kit publicado:
  - O valor do filtro de verdade ou falso vai em texto no blueprint (`"false"`). Com o booleano, o Make ignora a condição
    e a busca lê qualquer linha, então a fila nunca esvazia.
  - Sem pendente, a busca devolve 1 pacote vazio. O módulo seguinte leva o filtro "o `id` existe"; sem ele, roda com
    campos vazios e a execução termina em erro.
- A etapa 4 passa a rodar uma 3ª execução com a fila vazia, que tem de terminar em sucesso gastando exatamente 1
  operação: é a prova de que o filtro vale e de que nada roda depois de uma busca vazia.
- O verificador de blueprint passa a recusar o filtro de verdade ou falso com valor booleano e o módulo logo depois da
  busca sem o filtro "existe".

## v1.3.0 — 2026-10

A numeração salta da 1.1.0 para a 1.3.0.

- Fluxo que usa o Supabase só como banco de dados: tudo mora no Make, sem nada para cadastrar fora dele além de colar 1
  SQL, copiar o Project ID e a chave do painel e criar 1 conexão. A etapa 3 passa a desenhar com 5 regras novas.
  - A conexão é a do app Supabase do Make, e o desenho diz quais tabelas e operações ela alcança. Conexão direta ao
    banco (`postgres`) e o app `supabase-management` ficam de fora.
  - Do app entram só os cinco módulos de dados: buscar linhas, criar uma linha, gravar ou atualizar pela chave, contar e
    apagar. Aviso automático de tabela, chamada a função do projeto e tarefa agendada dentro do banco ficam de fora.
  - O fluxo que lê uma fila usa a agenda do Make: busca os pendentes (coluna verdadeiro ou falso), faz, e marca a linha
    inteira como feita. O desenho soma as operações gastas mesmo quando não há nada novo.
  - O desenho entrega o SQL para colar no SQL Editor: a chave natural como chave primária, dinheiro com duas casas
    decimais, RLS ligado e, quando há IA, a tabela de registro do aceite que não pode ser alterada nem apagada (com os 6
    campos obrigatórios) e a taxa de correção por pessoa e por mês.
- A etapa 3 consulta a documentação pública do Make uma vez por app e anota o endereço e a data no desenho.
- A etapa 4 para antes de criar o fluxo quando o desenho com Supabase não traz o que precisa; aceita que a 2ª execução
  do teste gaste menos que a 1ª e confere que o item foi processado; testa com chaves que começam com `TESTE-`.
- O verificador de blueprint passa a recusar arquivo sem a lista de módulos e, no Supabase, tudo que não seja módulo de
  dados do app, inclusive o endereço de um projeto Supabase em qualquer módulo e em qualquer caixa de letra.

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
