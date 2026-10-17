# Fluxo com Supabase — as receitas das regras [S1] a [S5]

Este arquivo é igual em todas as skills do spec-make. As regras curtas, com o que vira alerta e o que fica fora do alcance, ficam no `SKILL.md` da skill
`spec-make-design`; aqui fica o como fazer. Vale quando o fluxo **toca Supabase**: tem módulo do app `supabase`,
`supabase-management` ou `postgres`, ou chama por HTTP o endereço de um projeto Supabase.

Neste kit o Supabase é **só o banco de dados**: o fluxo inteiro mora no Make, e o app `supabase` do Make busca, grava e
atualiza linhas. Fonte: [app Supabase do Make](https://apps.make.com/supabase), conferida em 16/10/2026.

## [S1] A conexão e o que ela alcança

- A conexão do app Supabase no Make usa o diálogo padrão do app, com dois valores copiados do painel do Supabase:
  - **Project ID**: Project Settings → General (o código do projeto, não a URL);
  - **API Key**: Project Settings → API Keys → Secret keys (copie a chave secreta).
- Essa chave **ignora o RLS**: tudo que ela toca, ela lê e grava. Se for a mesma chave que outra parte do seu projeto usa,
  vazar ou trocar a chave atinge as duas. É o preço do caminho mais curto, e o DESIGN o deixa visível na coluna `alcance`.
- No DESIGN, a coluna `alcance` de cada conexão Supabase diz: o motivo ("o app Supabase do Make só conecta com chave
  secreta; ela ignora o RLS"), as tabelas que o fluxo usa e as operações (ler, gravar, apagar).
- Nunca no fluxo:
  - `postgres` (conexão direta com a senha do banco): abre o banco inteiro e esbarra na restrição de rede do projeto;
  - `supabase-management`: o módulo "Run a Query" roda qualquer SQL em **todos** os projetos da sua conta.

## [S2] Só os módulos do banco

Do app `supabase` entram só estes cinco módulos:

| Módulo | Para que serve |
|---|---|
| `searchRows` | Lista linhas de uma tabela por filtro (texto, número, data ou verdadeiro/falso) e limite |
| `createARow` | Cria uma linha nova (erro se a chave primária já existe) |
| `upsertARecord` | Cria a linha ou atualiza a que tem a mesma chave primária |
| `getRowsCount` | Conta as linhas de uma tabela |
| `deleteRows` | Apaga as linhas que casam com o filtro |

O fluxo não tem outro gatilho além da agenda do Make (ou da execução sob demanda), e a pessoa faz, antes do 1º fluxo
rodar, só isto fora do Make: **1 colagem de SQL** no SQL Editor, **copiar o Project ID e a chave** do painel e **1 conexão**
no Make. O DESIGN escreve essa contagem no bloco `Prepare o banco`. Qualquer passo a mais (aviso automático de tabela,
função do projeto chamada por endereço, tarefa agendada dentro do banco) fica fora deste kit.

Tabela que você já tem com id próprio: crie uma tabela de entrada nova, com a chave natural como chave primária, e deixe
o fluxo gravar nela.

## [S3] O laço da fila

Fila = tabela em que alguém (outro fluxo, o seu sistema, você) grava o que falta fazer. O fluxo lê os pendentes, faz, e
marca. Em 4 passos, nesta ordem:

1. **Agenda do Make** (ou sob demanda) dispara o fluxo.
2. **`searchRows`** na fila, filtro `processado` *Equals* `false`, com **limite** (o padrão do módulo é 10). O módulo não
   filtra "coluna vazia": por isso o pendente é uma coluna verdadeiro/falso que nasce `false`. No blueprint, o valor do
   filtro vai **em texto** (`"b": "false"`): com o booleano `false` o Make ignora a condição e a busca lê qualquer linha.
3. **Processa** cada linha que voltou (cada linha é uma passagem pelos módulos seguintes). Sem pendente, o `searchRows`
   devolve **1 pacote vazio** (não zero): o 1º módulo depois da busca leva o filtro "`{{<id da busca>.id}}` existe",
   senão ele roda com campos vazios, falha e o fluxo termina em erro. Com o filtro, a busca vazia gasta 1 operação.
4. **`upsertARecord`** na fila, pela chave primária (`id`), **regravando a linha inteira**: mapeie de volta todas as colunas
   que o `searchRows` leu e mude só `processado` para `true` e `processado_em` para agora.

Por que a linha inteira: o banco confere as colunas obrigatórias da linha proposta antes de olhar se ela já existe.
Marcar só `id` e `processado` falha em "coluna obrigatória vazia" (medido em 16/10/2026) ou, sem a obrigatoriedade,
apaga o que não foi mapeado.

Se o filtro verdadeiro/falso não funcionar no seu plano do Make, o plano B é uma coluna de texto `status` ("pendente" e
"feito") filtrada por texto, com o mesmo laço.

## [S4] Quem é o relógio do fluxo

Sem aviso automático de tabela, quem dispara o fluxo é a **agenda do Make** (ou você, sob demanda). Cada disparo roda o
1º módulo (a busca), então gasta **pelo menos 1 operação mesmo quando não há nada novo**.

Conta do custo parado: disparos por mês × operações do disparo vazio (normalmente 1). A cada 1 minuto são 43.200 disparos
por mês; a cada 15 minutos, 2.880; uma vez por hora, 720. Some isso ao custo por item na seção `Custo` do DESIGN. Se o
total passar do orçamento do DEFINE, aumente o intervalo.

## [S5] Prepare o banco — o SQL que o DESIGN entrega

O DESIGN traz o SQL pronto; você cola no SQL Editor do Supabase (Project → SQL Editor → New query) e roda uma vez,
**antes** da etapa 4. Rodar de novo é seguro. Os blocos 1, 3 e 4 são opcionais: apague o que o fluxo não usa (sem fila,
sem IA).

- **A chave natural é a chave primária da tabela de destino que o módulo "Upsert a Record" grava.** O módulo decide se o
  registro já existe pela chave primária; um `UNIQUE` em outra coluna não impede a duplicata por ele. A **fila** aceita a
  mesma chave natural mais de uma vez (o mesmo documento pode chegar duas vezes): ela tem o próprio `id` como chave
  primária, e o destino deduplica.
- **Dinheiro é sempre `numeric(18,2)`**, nunca `real` nem `float`: ponto flutuante erra o centavo e a diferença só
  aparece na conciliação. A conferência no fim do SQL olha as colunas que **você lista** no `a.attname in (…)` (uma por
  coluna de dinheiro) e, em qualquer coluna, recusa `real` e `double precision`; taxa e código de conta (`aliquota`,
  `conta_debito`) não são dinheiro e ficam fora da lista. Se o fluxo rateia um valor, o DESIGN escreve a regra do centavo residual (quem fica com a
  sobra).
- **`processado`** (`boolean not null default false`) e **`processado_em`**: o `searchRows` filtra o pendente por
  `processado` igual a `false`.
- **RLS ligado, sem política:** quem tiver a chave pública do projeto não lê nem grava a tabela. Toda chave secreta do
  projeto alcança; por isso o `alcance` do [S1] fica escrito no DESIGN. Se a tabela já existia com alguma política, a
  conferência no fim do SQL para e avisa.
- **Auditoria do aceite da IA ([G2]) só de acréscimo:** a chave primária é `chave_do_aceite` (o id da sugestão aceita: o
  mesmo aceite não entra 2 vezes), os **6 campos** são obrigatórios e um gatilho recusa alterar para valores diferentes,
  apagar e truncar. Repetir a **mesma linha idêntica** passa sem efeito. Por isso os 6 campos vêm do **passo de aceite**,
  gravados antes do "processa" (por exemplo, na fila, ao lado do item) e lidos de lá: nunca recalcule a sugestão da IA
  nem use "agora" no campo `quando` na hora de gravar a auditoria, ou a reexecução do mesmo item seria recusada.
- **Taxa de correção:** a view `<auditoria>_taxa_de_correcao` mostra, por pessoa e por mês, quantos aceites e quantos foram
  editados antes de aceitar. Quem aceita 100% sem editar por meses merece uma conversa. A view ignora a chave de aceite
  que começa com `TESTE-`. A pessoa lê essa view no SQL Editor do Supabase (`select * from public.<auditoria>_taxa_de_correcao`),
  e o DESIGN diz isso.
- **Teste sem sujar:** nos testes, grave as linhas da fila com a chave natural exatamente `TESTE-1` (a fila aceita a
  mesma chave mais de uma vez), use uma `chave_do_aceite` que começa com `TESTE-` e acrescente ao filtro do `searchRows`
  a condição `chave_natural` *Equals* `TESTE-1`, para o teste nunca ler nem marcar um pendente real ("contém" casaria
  uma chave real com `TESTE-` no meio). Quando ligar de verdade, tire essa condição, valide o módulo editado e confira
  que o filtro ficou só com `processado` igual a `false`. O aceite de teste fica na auditoria (ela não se apaga), mas a view da
  taxa de correção o ignora; o registro de teste do destino você apaga com um `delete`.

```sql
-- Prepare o banco — <fluxo>. Cole no SQL Editor do Supabase (Project → SQL Editor → New query) e rode uma vez.
-- Rodar de novo é seguro: tudo é "if not exists" ou "or replace".

-- 1. Fila de entrada: quem alimenta grava aqui; o fluxo lê os pendentes (só quando o fluxo lê uma fila).
create table if not exists public.<fila> (
  id bigint generated by default as identity primary key,   -- "by default": o marcador do fluxo regrava a linha com o próprio id
  <chave_natural> text not null,
  <valor> numeric(18,2) not null,                           -- dinheiro: sempre numeric(18,2), nunca real/float
  processado boolean not null default false,                -- o searchRows filtra "igual a false"; não filtra "vazio"
  processado_em timestamptz,
  criado_em timestamptz not null default now()
);
alter table public.<fila> enable row level security;        -- sem política: só a chave secreta alcança

-- 2. Destino: a chave natural É a primary key (o "Upsert a Record" decide pela primary key).
create table if not exists public.<destino> (
  <chave_natural> text primary key,
  <valor> numeric(18,2) not null
);
alter table public.<destino> enable row level security;

-- 3. Auditoria do aceite da IA ([G2]) — só de acréscimo (apague este bloco e o 4 se o fluxo não tem IA).
create table if not exists public.<auditoria> (
  chave_do_aceite text primary key,                          -- o id da sugestão aceita: o mesmo aceite não entra 2 vezes
  modelo text not null,
  versao_prompt text not null,
  sugestao_original text not null,
  quem_aceitou text not null,
  quando timestamptz not null,                               -- o instante do aceite, vindo do passo de aceite (nunca "agora")
  editou boolean not null
);
alter table public.<auditoria> enable row level security;
revoke all on public.<auditoria> from anon, authenticated;

create or replace function public.<auditoria>_bloqueia() returns trigger language plpgsql as $$
begin
  if tg_op = 'UPDATE' and new is not distinct from old then return new; end if;   -- repetição idêntica passa sem efeito
  raise exception '<auditoria> é só de acréscimo: % recusado', tg_op;
end $$;
create or replace trigger <auditoria>_sem_alteracao before update or delete on public.<auditoria>
  for each row execute function public.<auditoria>_bloqueia();
create or replace trigger <auditoria>_sem_truncate before truncate on public.<auditoria>
  for each statement execute function public.<auditoria>_bloqueia();

-- 4. Taxa de correção: quanto do que a IA sugere é editado antes de aceito, por pessoa e por mês.
--    Aceite de teste (chave que começa com TESTE-) não entra na conta: a auditoria não se apaga, a view o ignora.
create or replace view public.<auditoria>_taxa_de_correcao with (security_invoker = true) as
  select quem_aceitou, date_trunc('month', quando) as mes, count(*) as aceites,
         count(*) filter (where editou) as editados,
         round(100.0 * count(*) filter (where editou) / count(*), 1) as pct_editados
    from public.<auditoria> where chave_do_aceite not like 'TESTE-%' group by 1, 2;
revoke all on public.<auditoria>_taxa_de_correcao from anon, authenticated;

-- 5. Conferência: falha alto se alguma trava não pegou. Cada tabela opcional tem o próprio "if" aninhado: o PostgreSQL só
--    resolve o nome da tabela quando entra no bloco, então apagar o bloco 1 (fila) ou o 3 (auditoria) não quebra a conferência.
do $$ begin
  if to_regclass('public.<destino>') is not null then
    if not exists (select 1 from pg_constraint c join pg_attribute a on a.attrelid = c.conrelid and a.attnum = c.conkey[1]
                    where c.conrelid = 'public.<destino>'::regclass and c.contype = 'p'
                      and array_length(c.conkey, 1) = 1 and a.attname = '<chave_natural>') then
      raise exception 'Prepare o banco: <destino> já existia sem <chave_natural> como primary key — o Make duplicaria';
    end if;
  end if;
  if exists (select 1 from pg_attribute a join pg_class c on c.oid = a.attrelid join pg_namespace n on n.oid = c.relnamespace
              where n.nspname = 'public' and c.relname in ('<fila>', '<destino>', '<auditoria>') and c.relkind = 'r'
                and a.attnum > 0 and not a.attisdropped
                and (a.atttypid in ('real'::regtype, 'double precision'::regtype)
                     or (a.attname in ('<valor>')       -- escreva aqui o nome de CADA coluna de dinheiro do fluxo, entre aspas e com vírgula
                         and format_type(a.atttypid, a.atttypmod) <> 'numeric(18,2)'))) then
    raise exception 'Prepare o banco: há coluna de dinheiro fora de numeric(18,2), ou em real/double precision — o centavo se perde';
  end if;
  if exists (select 1 from pg_policies where schemaname = 'public' and tablename in ('<fila>', '<destino>', '<auditoria>')) then
    raise exception 'Prepare o banco: há política de RLS numa tabela do fluxo — ela pode abrir a tabela; revise';
  end if;
  if to_regclass('public.<fila>') is not null then
    if not exists (select 1 from pg_attribute a join pg_constraint k on k.conrelid = a.attrelid and k.contype = 'p'
                                                  and k.conkey = array[a.attnum]
                    where a.attrelid = 'public.<fila>'::regclass and a.attname = 'id' and a.attidentity = 'd') then
      raise exception 'Prepare o banco: <fila>.id precisa ser a primary key, gerada "by default" — senão o marcador não regrava a linha';
    end if;
    if not exists (select 1 from pg_attribute a
                    where a.attrelid = 'public.<fila>'::regclass and a.attname = 'processado_em' and a.atttypid = 'timestamptz'::regtype
                      and not a.attisdropped) then
      raise exception 'Prepare o banco: <fila>.processado_em (timestamptz) não existe — o marcador não grava e o item volta à fila';
    end if;
    if not exists (select 1 from pg_attribute a join pg_attrdef d on d.adrelid = a.attrelid and d.adnum = a.attnum
                    where a.attrelid = 'public.<fila>'::regclass and a.attname = 'processado' and a.atttypid = 'boolean'::regtype
                      and a.attnotnull and pg_get_expr(d.adbin, d.adrelid) = 'false') then
      raise exception 'Prepare o banco: <fila>.processado precisa ser boolean not null default false — senão o searchRows não lê a linha';
    end if;
  end if;
  if to_regclass('public.<auditoria>') is not null then
    if not exists (select 1 from pg_constraint c join pg_attribute a on a.attrelid = c.conrelid and a.attnum = c.conkey[1]
                    where c.conrelid = 'public.<auditoria>'::regclass and c.contype = 'p'
                      and array_length(c.conkey, 1) = 1 and a.attname = 'chave_do_aceite') then
      raise exception 'Prepare o banco: <auditoria> já existia sem chave_do_aceite como primary key — o mesmo aceite entraria 2 vezes';
    end if;
    if (select count(*) from pg_attribute where attrelid = 'public.<auditoria>'::regclass and attnum > 0 and not attisdropped
           and attnotnull and attname in ('modelo', 'versao_prompt', 'sugestao_original', 'quem_aceitou', 'quando', 'editou')) <> 6 then
      raise exception 'Prepare o banco: a auditoria precisa dos 6 campos de [G2] (modelo, versao_prompt, sugestao_original, quem_aceitou, quando, editou), todos obrigatórios';
    end if;
    if (select count(*) from pg_trigger where tgrelid = 'public.<auditoria>'::regclass and not tgisinternal) <> 2 then
      raise exception 'Prepare o banco: a auditoria não tem os 2 gatilhos de só-acréscimo';
    end if;
    if has_table_privilege('anon', 'public.<auditoria>', 'SELECT,INSERT,UPDATE,DELETE')
       or has_table_privilege('authenticated', 'public.<auditoria>', 'SELECT,INSERT,UPDATE,DELETE')
       or has_table_privilege('anon', 'public.<auditoria>_taxa_de_correcao', 'SELECT')
       or has_table_privilege('authenticated', 'public.<auditoria>_taxa_de_correcao', 'SELECT') then
      raise exception 'Prepare o banco: a auditoria ou a taxa de correção está aberta para anon ou authenticated';
    end if;
  end if;
end $$;
```

Por que o `revoke` e a conferência citam `anon` e `authenticated`: no Supabase, toda tabela ou view nova nasce legível
por esses 2 papéis, e uma view criada pelo dono ignora o RLS a menos que seja `security_invoker`.

## Como a etapa 4 prova

A 2ª passagem da mesma chave natural deixa a mesma contagem na tabela de destino **e** a linha nova da fila volta como
`processado = true` (o disparo vazio também gasta 1 operação, então "operações maiores que zero" sozinho não basta).
Essa é a prova de que a chave primária existe, de que o módulo a usa e de que o laço marca o que processou.
