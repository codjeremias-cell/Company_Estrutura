# Comunicação matricial com Negócios

## Condição de abertura

`diretor-de-lentes ↔ departamento-negocios` só pode abrir quando a
`EXECUTIVE_MISSION`:

- contém ambos em `recipients`;
- fixa o mesmo contrato e candidato;
- traz `matrix_exchange.allowed: true`;
- delimita `topics`, `read_scope` e `write_scope`;
- nomeia um único `consolidation_owner`;
- mantém `ceo-maestro` como canal de decisão executiva.

Com um único destinatário, a troca permanece negada.

## Autoridades

| Tema | Autoridade |
|---|---|
| viabilidade técnica e riscos técnicos | Diretor |
| mercado, cliente, preço e viabilidade comercial | Negócios |
| escopo, prioridade, orçamento e risco residual aceito | CEO |
| conflito de autoridade ou exceção | Jeremias, por meio do CEO |
| julgamento da entrega | Departamento de Juízes |

Recomendação lateral não é comando e não amplia o contrato.

## Handoff

Cada troca é materializada como `MATRIX_EXCHANGE_MESSAGE` e preserva:

- `contract_id`, versão e digest;
- `candidate_digest`;
- tópico autorizado;
- escopo de leitura e escrita;
- decisão solicitada;
- autor e evidência;
- destinatário e dono da consolidação.

O schema valida que remetente e destinatário são lados opostos e que o produtor causal é o
remetente. O Diretor confere a mensagem contra a `EXECUTIVE_MISSION`: tópico e escopos são
subconjuntos do autorizado, contrato e rodada coincidem e o dono da consolidação não muda.
O `candidate_digest` também deve coincidir; mensagem de outro candidato é rejeitada.

Quando o Diretor consolida, a contribuição de Negócios permanece assinada. Quando Negócios
consolida, o Diretor devolve contribuição técnica assinada e não emite pacote concorrente.

## Juízes

Negócios pode encaminhar sua entrega diretamente ao `departamento-juizes` e receber o
parecer, com o Diretor informado pela relação administrativa dos Juízes. Isso não subordina
Negócios ao Diretor e não concede ao Diretor poder sobre o conteúdo comercial ou o
veredito.

## Gatilhos de escalada

Voltar ao CEO quando:

- o assunto ultrapassa os tópicos permitidos;
- há disputa de escopo, prioridade, orçamento ou risco aceito;
- os lados usam candidatos ou versões diferentes;
- não existe dono único da consolidação;
- uma decisão vinculante seria alterada;
- falta capacidade necessária.

## Critério de conclusão

A troca fecha quando existe contribuição correlacionada, autoridade preservada, dono único
da consolidação e nenhuma ampliação silenciosa de escopo.
