# Governança do fluxo — [G1], [G2], [G3]

Um fluxo do Make que grava num sistema do escritório é um importador, e um fluxo com IA que decide é um autor. As três
regras abaixo valem para qualquer fluxo desenhado pelo spec-make.

## [G3] Chave natural — não gravar duas vezes

**Quando se aplica:** o fluxo cria registros (linha de planilha, lançamento no ERP, registro de data store, contato no
CRM).

**O que o DESIGN declara:**

| Campo | Exemplo |
|---|---|
| Chave natural | chave de acesso da nota · id do e-mail · CNPJ · id da transação do extrato |
| Regra | Já existe ⇒ não grava de novo |
| Como | Consultar pela chave antes de gravar (filtro "não encontrado") **ou** gravar substituindo pela chave (data store "Adicionar ou substituir") |
| Destino é um banco (Supabase) | A chave existe no banco como restrição: a `primary key` da tabela que o "Upsert a Record" grava ([S5], SQL em SUPABASE.md) |

**Por quê:** o mesmo item volta — e-mail reaberto, linha reprocessada, nova tentativa depois de falha. Sem a chave, o
escritório descobre a duplicata na conciliação, meses depois.

**Prova no teste de aceite:** a segunda execução da mesma amostra deixa a mesma contagem de registros.

**Sem a chave:** alerta [A1]; peça a chave.

## [G1] Aceite humano antes de a IA gravar

**Quando se aplica:** um módulo de IA grava, classifica ou altera lançamento, documento fiscal ou cadastro do
escritório.

**O que o DESIGN declara:** o passo de aceite entre a IA e a gravação, e quem aceita (pessoa identificada).

| Forma de aceite | Como fica no fluxo |
|---|---|
| Fila de sugestões | A IA grava a sugestão numa planilha; a pessoa marca "aprovado"; outro fluxo (ou passo) grava no destino |
| Aprovação por e-mail | O fluxo manda a sugestão; a pessoa responde; o fluxo só grava com a resposta |
| Formulário | A pessoa confirma num formulário; o fluxo grava a partir da confirmação |

**Por quê:** quem responde pelo lançamento é o profissional. "O modelo classificou" não serve de resposta diante de um
cliente, do fisco ou de um perito.

**Sem o passo:** alerta [A1]; diga o que falta e ofereça o desenho com o passo.

## [G2] Registro do aceite

**Quando se aplica:** há IA com sugestão aceita ([G1]).

**O que o DESIGN declara:** onde fica o registro (planilha ou data store da própria pessoa, fora do histórico do
Make; quando o fluxo já usa Supabase, a 1ª opção é uma tabela de auditoria só de acréscimo, com o SQL de SUPABASE.md) e os seis campos:

| Campo | Exemplo |
|---|---|
| modelo | o modelo de IA usado no módulo |
| versão do prompt | a do inventário [P1] |
| sugestão original | o que a IA propôs, antes de qualquer edição |
| quem aceitou | nome ou e-mail de quem aprovou |
| quando | data e hora em UTC |
| editou | sim ou não |

**Por quê:** com `confidential: true`, o histórico do Make não guarda a entrada nem a saída da IA. Sem o registro, não
há como reconstruir por que um lançamento foi feito daquele jeito, nem medir se as sugestões são aceitas sem leitura.

**Sem o registro:** alerta [A1].
