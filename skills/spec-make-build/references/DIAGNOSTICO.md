# Diagnóstico quando o teste falha

**[B3] Quando o teste falha.** O Make costuma devolver erro pouco claro (por exemplo,
"Validation failed for 1 parameter(s)") e o detalhe da execução pode vir vazio, principalmente com o fluxo
confidencial. Por isso, investigue nesta ordem, uma hipótese por vez:

1. **interface** — `scenarios_interface`: `input` vazio num fluxo sob demanda que recebe dados é a causa mais comum.
   Corrija com `scenarios_set-interface` e rode de novo.
2. **módulo** — `app-module_get` do módulo citado no erro (ou de cada um, na ordem): campo obrigatório faltando, nome
   de campo errado, versão diferente da do blueprint. Corrija com `scenarios_update` (o blueprint inteiro, partindo do
   que `scenarios_get` devolver).
3. **conexão** — `connections_list`: conexão expirada, de outra equipe ou sem a permissão do módulo. Peça nova
   autorização com `credential-requests_create`.
4. **mapeamento** — o valor que um módulo passa ao seguinte: campo vazio, tipo errado (texto onde se espera número),
   formato (CNPJ com pontuação). Corrija o mapeamento no blueprint.

A cada tentativa, fale com a pessoa em três partes:

- **o que aconteceu** — em linguagem de escritório: "a consulta à Receita não recebeu o CNPJ";
- **o que eu já fiz** — a hipótese conferida, a correção, a tentativa (n de 3) e as operações gastas até aqui;
- **o que você faz agora** — uma ação: "nada, vou rodar de novo" ou "autorize a conexão neste link".

**Teto: 3 tentativas** de correção para o mesmo teste. Na terceira falha, pare: não rode de novo, deixe o fluxo sob
demanda como está, entregue o resumo (as três hipóteses, o que o Make respondeu, as operações gastas) e a frase pronta
para pedir ajuda: "Meu fluxo {nome} falhou no teste com {erro}; já conferi interface, módulo, conexão e mapeamento."

Correções só no fluxo que esta conversa criou ([B4]).
