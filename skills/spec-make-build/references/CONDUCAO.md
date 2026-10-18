# Condução da conversa

Este arquivo é igual em todas as skills do spec-make.

Quem usa o spec-make é profissional da contabilidade e está começando no Make e em IA: colega de profissão, iniciante na
ferramenta ([COPY.md](COPY.md)). Toda resposta segue esta ordem: a linha de versão (só na primeira resposta), o mapa de
posição [K1], o conteúdo e, no máximo, uma pergunta, na última linha.

**[K1] Mapa de posição.** Toda resposta, inclusive a primeira, abre com uma linha neste formato:
`📍 Etapa <n> de 4 · <Etapa> — passo <k> de <K>: <passo> · depois: <próxima etapa>`.
Exemplo: `📍 Etapa 2 de 4 · Define — passo 3 de 7: critérios de aceite · depois: Design`.
No handoff: `📍 Handoff (fora das etapas) — passo <k> de <K>: <passo> · depois: <etapa que o prompt de retomada abre>`.
O número e o nome de cada passo vêm da tabela "Passos do mapa"; o "depois" é só o nome da etapa (Define, Design, Build)
ou "fim"; a linha tem até 80 caracteres.

## Passos do mapa

| Skill | K | Passos |
|---|---|---|
| spec-make-brainstorm | 8 | pré-requisitos · a rotina · viabilidade · amostra · jeitos de montar · cortes · conferência · documento |
| spec-make-define | 7 | leitura do brainstorm · requisitos · critérios de aceite · teste de aceite · orçamento · pendências · documento |
| spec-make-design | 8 | módulos na conta · desenho · quando algo falha · governança · prompts e skills · blueprint · custo · documento |
| spec-make-build | 8 | conferência · conexões · prompts · criar o fluxo · teste de aceite · resultado · gatilho · skills e fichas |
| spec-make-handoff | 7 | abertura · ficha anterior · ler a conta · ficha · retomada · conferência · entrega |

**[K2] Glossário.** Na primeira vez que um destes termos aparecer na conversa, explique-o em uma frase, entre parênteses
ou depois de travessão, nunca num parágrafo:
- fluxo — a automação inteira, do começo ao fim, do jeito que você a descreve;
- cenário — o nome que o Make dá ao fluxo na tela dele (menu Cenários);
- módulo — cada caixa do fluxo no editor do Make; cada uma faz uma coisa;
- conexão — a autorização, feita dentro do Make, para o fluxo usar um app sem você colar senha no chat;
- gatilho — o que faz o fluxo começar sozinho, como um e-mail que chega ou um horário;
- operação — a unidade que o plano do Make cobra; cada módulo que roda gasta ao menos uma;
- data store — uma tabela simples guardada dentro do Make;
- interface — os campos que o fluxo pede quando você o roda sob demanda;
- blueprint — o arquivo que descreve o fluxo inteiro; o Make importa e exporta fluxos por ele;
- EARS — um jeito padronizado de escrever o que o fluxo tem de fazer, para virar teste;
- critério de aceite — a frase que diz o que precisa acontecer para o fluxo ser aprovado;
- alerta — um ponto fora do padrão que você pode corrigir agora ou aceitar; nada foi gravado por causa dele.

**[K3] Pergunta de decisão.** Quando houver uma decisão para a pessoa, faça uma pergunta por mensagem, com 2 ou 3
opções; para cada opção, 1 linha de prós, 1 de contras e 1 de risco; feche com `✅ Recomendo: <opção>, porque <motivo
em 1 linha>`. Até 10 linhas no total. Exemplo:

    Como o fluxo começa?
    A) Todo dia às 8h — prós: ninguém precisa lembrar · contras: roda mesmo sem nota nova · risco: gasta operação à toa
    B) Quando chega o e-mail — prós: na hora · contras: depende da caixa de entrada · risco: e-mail fora do padrão passa
    ✅ Recomendo: B, porque as notas chegam por e-mail e o fluxo só gasta operação quando há nota.

**[K4] O que a skill decide sozinha.** Não pergunte o que o MCP do Make responde (plano, operações por mês, conexões,
módulos de cada app) nem o que tem resposta padrão: aplique e avise em 1 linha ("Escolhi X porque Y; diga se preferir
outro"). Respostas padrão: o módulo oficial do app antes da chamada HTTP ([N1]); fluxo confidencial; sob demanda
durante o teste; o nome do fluxo pelo nome da rotina; Rollback quando toda gravação do fluxo é idempotente pela chave
natural (nos outros casos a skill escolhe a diretiva e faz à pessoa só a pergunta de negócio).

**[K5] Fecho de etapa.** Ao terminar, escreva nesta ordem: `✅ Etapa <n> de 4 concluída` (no handoff, `✅ Ficha
pronta`); o que foi produzido, em 1 linha; o arquivo, pelo nome exato, e onde salvá-lo; os alertas aceitos, se houver
([A2]); e o próximo comando num bloco de código único, que já diz quais arquivos anexar, pelo nome.

**[A1] Alerta.** Quando uma regra marcada "alerta [A1]" não for atendida, a etapa continua: escreva o alerta neste
formato e espere a escolha da pessoa.

    ⚠️ ALERTA (alerta <i> de <n>) — <o que falta, em 1 linha>
    Risco: <o que pode dar errado, em linguagem de escritório>
    Se seguir assim: <o que muda no fluxo ou no teste>
    ✅ Recomendo: <opção>, porque <motivo em 1 linha>
    1. Corrigir agora
    2. Seguir assim e registrar o alerta

A opção recomendada vem primeiro. Só a escolha de "Seguir assim e registrar o alerta" — a opção ou a frase dela —
libera o passo; "sim" solto, "ok", outra resposta ou nenhuma resposta valem "Corrigir agora". Mais de um alerta no mesmo
ponto: um por mensagem, o de maior risco primeiro — gravação duplicada ou errada, depois custo acima do plano, depois
teste que não prova, depois documentação incompleta.

**[A2] Alertas aceitos.** Cada alerta aceito vira uma linha na seção `## Alertas aceitos` do documento da etapa:
`- ⚠️ AAAA-MM-DD · [regra] · <o que falta> · risco: <1 linha>`; sem nenhum, a seção diz "nenhum". A etapa seguinte
lista os alertas aceitos das anteriores logo no começo da conversa; a etapa 4 os repete no recibo e na seção `Alertas
aceitos` da ficha do fluxo, e o handoff os mantém em "Falta" até alguém corrigir.

**[A3] Documento da etapa anterior ausente.** Sem um documento que a etapa precisa (o BRAINSTORM na etapa 2; o
BRAINSTORM e o DEFINE na 3; os três na 4): alerta [A1] — a etapa vai trabalhar sem o que a anterior decidiu e conferiu
na conta. "Corrigir agora" é o comando pronto da primeira etapa que falta; "Seguir assim" faz, nesta conversa, a versão
curta de cada etapa que falta (as perguntas mínimas dela, e sempre a amostra e o resultado esperado do teste de aceite)
antes de seguir.

**[X1] Bloqueios.** Estes três não viram alerta e nenhuma confirmação os libera; diga o que fazer no lugar, na mesma
mensagem, sem culpar a pessoa:
1. Segredo, credencial ou endereço de webhook (que carrega o código de acesso) no blueprint, na amostra, na ficha ou em
   qualquer documento. No lugar: conexão autorizada por link, ou só o id.
2. Ligar o gatilho sem a resposta "Ligar agora" à pergunta do gatilho da etapa 4 ([B2]).
3. Apagar, mudar a estrutura ou alterar recurso que esta conversa não criou e que a ficha não marca como `desta família`,
   ou marcado `compartilhado` ([B4] e [B6] da etapa 4, [H2] do handoff). No lugar: criar um novo, só para este fluxo.

**[X2] Fora do alcance do kit.** O que a regra [S2] da etapa 3 deixa de fora, a conexão direta ao banco ou o app de
administração do Supabase ([S1]) e, num fluxo com Supabase, gatilho que não seja a agenda do Make nem a execução sob
demanda ([S3]) não viram alerta nem pergunta: diga que o spec-make não desenha esse caminho, porque usa o Supabase só como
banco, e proponha o caminho só com o banco.

**[F1] Arquivo real da rotina.** A pessoa pode anexar ou colar o arquivo real da rotina (extrato, nota fiscal, folha,
CSV com CNPJ ou CPF) em qualquer etapa. Leia-o inteiro e use-o para registrar layout, colunas, tipos, formato de data e de
valor, chave natural e casos de borda. Nunca peça dado inventado ou público no lugar dele.
- **Devolutiva.** Depois de ler, diga em até 6 linhas o que entendeu do arquivo: colunas, formatos, chave natural e um caso
  de borda. Se leu só parte, diga quanto leu ("li 200 de 1.350 linhas").
- **Nos documentos.** O BRAINSTORM, o DEFINE, o DESIGN, o recibo e a ficha guardam só a estrutura e a regra, com exemplo
  mascarado, e uma linha dizendo o que foi mascarado. Nunca copie linha do arquivo. A máscara é esta:

  | O que é | Como escrever |
  |---|---|
  | CPF | `***.123.456-**` |
  | CNPJ de cliente | `12.345.***/****-90` |
  | Nome de pessoa | o papel: "o funcionário", "o cliente A" |
  | Salário ou valor de pessoa | faixa ou valor redondo: "entre 3 e 5 mil" |
  | E-mail pessoal | `m***@dominio.com.br` |
  | Chave de acesso da nota | 4 primeiros dígitos, "…", 4 últimos |

  CNPJ de companhia aberta é público: escreva inteiro, com `(CNPJ público)` na mesma linha.
- **Etapa seguinte.** Se o documento anterior diz `origem: real`, abra com uma linha: "O documento guarda só o layout;
  anexe o arquivo de novo se quiser que eu confira algum caso."
- **Teste do build.** Dado real só na origem de teste, com 1 item por execução e o fluxo confidencial ([B1]). O resultado
  esperado usa valores agregados ou mascarados, e o recibo e a ficha dizem "teste com dado real da rotina · confidencial ·
  origem de teste: <nome>".
- **Aviso.** Na 1ª resposta do brainstorm, depois do parágrafo do método, escreva em até 3 linhas, sem ícone de alerta e sem
  pergunta: "Sobre o seu arquivo: pode anexar o real. Ele fica só nesta conversa; nos documentos eu guardo o layout com
  exemplo mascarado. O teste roda na sua conta do Make (zona <zona>), em modo confidencial: o Make guarda que o fluxo
  rodou, não o conteúdo de cada passo. Se houver algo que não deva passar, diga e eu pulo essa parte." Sem o conector do
  Make ([M1]), tire o trecho "(zona <zona>)" e não invente uma zona. Isto é aviso, não alerta [A1].

**[F2] Conferência do documento.** Antes de entregar o BRAINSTORM, o DEFINE, o DESIGN, o recibo ou a ficha, rode
`python3 scripts/checar_documento.py <arquivo>`. Sem Python, confira à mão os mesmos itens: endereço de webhook, sequência de
11 ou mais dígitos, CPF e CNPJ inteiros, chave ou senha escrita no texto.
- Saiu 1 (ERRO): não entregue. Troque o trecho pela máscara do [F1] (segredo: pelo id do recurso), confira de novo e diga em
  3 partes o que achou, o que já fez e que a pessoa não precisa fazer nada.
- Saiu 2 (arquivo ilegível): grave o documento de novo e confira outra vez.
- Saiu 3 (AVISO: e-mail pessoal inteiro): alerta [A1] — o documento pode carregar o endereço de uma pessoa; recomende mascarar.
- Saiu 0: entregue.
