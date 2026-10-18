# Changelog

## v1.5.0 — 2026-10

- Você pode anexar o arquivo real da rotina (extrato, nota fiscal, folha, CSV com CNPJ ou CPF) no Brainstorm, no Define, no
  Design e no Build. A skill lê o arquivo, diz o que entendeu dele (colunas, formatos, chave, um caso de borda) e o usa para
  desenhar o fluxo com os casos reais.
- Os documentos que a skill entrega (BRAINSTORM, DEFINE, DESIGN, recibo e ficha) guardam só o layout, com exemplo
  mascarado, e dizem o que foi mascarado. Antes de entregar, um verificador novo (`checar_documento.py`) confere se não ficou
  CPF, CNPJ, número longo, credencial ou endereço de webhook inteiros no texto; se achar, a skill mascara sozinha.
- Continuam travando só segredo, chave e endereço de webhook, ligar o gatilho sem o seu "Ligar agora" e mexer no que a
  conversa não criou. Dado pessoal deixou de travar.
- A primeira resposta do Brainstorm avisa, em duas linhas, onde o seu arquivo passa: fica na conversa, o teste roda na sua
  conta do Make em modo confidencial e o Make guarda que o fluxo rodou, não o conteúdo de cada passo.

## v1.4.0 — 2026-10

- As 5 skills conduzem desde a primeira mensagem: toda resposta abre com um mapa de posição ("Etapa 2 de 4 · Define —
  passo 3 de 7 · depois: Design"), cada termo é explicado na primeira vez, cada etapa termina com o arquivo produzido e o
  próximo comando pronto para colar. A etapa 1 explica o método e confere os pré-requisitos pelo Make; o que faltar vem
  com o como resolver, e a conversa segue.
- Cada critério do DEFINE ganha, logo abaixo, "Em outras palavras", em linguagem do dia a dia.
- Pergunta de decisão sempre com opções, prós, contras, riscos e a recomendação; o que o Make responde sozinho ou tem
  resposta padrão não vira pergunta.
- O que antes travava a etapa vira alerta: a skill mostra o risco, recomenda e espera "Corrigir agora" ou "Seguir assim e
  registrar o alerta"; o alerta aceito fica no documento da etapa, no recibo e na ficha. Continuam travando só segredo ou
  dado pessoal real, ligar o gatilho sem o seu "Ligar agora" e mexer no que a conversa não criou; o Supabase segue só
  como banco.
- Módulo oficial do app antes de HTTP: chamada HTTP só com o motivo escrito, e o verificador avisa.
- Os verificadores separam ERRO (para a etapa 4) de AVISO (vira alerta).
- O prompt do agente de IA passa a ser escrito pela `prompt-builder-by-rdd`; fluxo acionado pelo assistente ganha uma
  skill feita pela `skill-builder-by-rdd`.

## v1.3.3 — 2026-10

- A etapa 4, quando o fluxo toca o Supabase, roda o verificador de blueprint como passo obrigatório e, se ele reprovar,
  não cria o fluxo: diz o problema e manda voltar à etapa 3.
- A etapa 3 manda o desenho dizer que a pessoa lê a view da taxa de correção no SQL Editor do Supabase, com o comando.

## v1.3.2 — 2026-10

- O verificador de blueprint passa a conferir também a busca que está dentro de uma rota de roteador (o valor em texto do
  filtro de verdade ou falso e o filtro "existe" no módulo seguinte), e a reconhecer o módulo do Supabase escrito com
  outra caixa de letra ou com espaço (módulo fora da lista não escapa mais por causa disso).

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
