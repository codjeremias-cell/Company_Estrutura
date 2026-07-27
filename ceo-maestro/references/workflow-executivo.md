# Workflow executivo

## Cadeia de comando

```text
Jeremias
  └── ceo-maestro
      ├── departamento-negocios
      ├── departamento-evolucao-skills
      └── diretor-de-lentes
          ├── departamento-juizes
          └── departamentos operacionais e seus agentes
```

O CEO Maestro possui exatamente **três** interlocutores diretos: `diretor-de-lentes`,
`departamento-negocios` e `departamento-evolucao-skills` (ADR-004).

O Departamento de Juízes **não** é interlocutor do CEO nem canal lateral de ninguém: recebe
`JUDGMENT_REQUEST` somente do `diretor-de-lentes` e devolve o parecer somente a ele
(`ORGANOGRAMA.md`, princípio 6). Entrega de Negócios chega ao julgamento pela matriz
Negócios↔Diretor, nunca por contato direto. O parecer alcança o CEO anexado ao retorno do
dono executivo.

## Matriz de roteamento

| Frente | Dono executivo | Participação complementar |
|---|---|---|
| Produto técnico ou implementação | `diretor-de-lentes` | Negócios quando houver valor, mercado ou monetização |
| Arquitetura, dados, design, segurança, desenvolvimento, QA, inovação, auditoria ou registros | `diretor-de-lentes` | Negócios somente se houver decisão comercial |
| Estratégia, cliente, mercado, preço, monetização ou viabilidade | `departamento-negocios` | Diretor quando depender de produto ou tecnologia |
| Criar, evoluir, avaliar ou aposentar **skill** da estrutura | `departamento-evolucao-skills` | Diretor quando a skill for de Departamento sob ele; Registros quando a lição vier do relatório de aprendizagem |
| Proposta de produto | ambos | Negócios lidera valor; Diretor lidera viabilidade técnica |
| Pedido puramente informativo, sem produto/proposta | CEO responde ou roteia para análise | não emitir status de validação |

A linha de evolução de skill é a **única** rota que alcança o `departamento-evolucao-skills`,
e ela existe só aqui: aquele Departamento não tem rotina, ronda nem iniciativa própria, e só
opera sob `EXECUTIVE_MISSION` deste CEO. A demanda pode nascer no
`departamento-inovacao-melhoria` e subir Inovação → Diretor → CEO como recomendação; o
envelope que autoriza é sempre desta camada. Sem essa linha, o único que pode acionar a
Evolução ficaria sem regra que a alcançasse.

Palavra-chave não define o dono sozinha; a responsabilidade real define. Missão mista contém
dois `front_id`, dependências explícitas e uma barreira de integração.

## Comunicação matricial

Autorizar `departamento-negocios ↔ diretor-de-lentes` somente quando a missão:

- fixa `contract_id`, versão e digest;
- delimita assunto, leitura, escrita e decisão permitida;
- nomeia qual lado consolida o retorno;
- exige que ambos preservem os mesmos `candidate_digest` e critérios;
- mantém o CEO informado por retorno correlacionado.

A comunicação matricial não autoriza Negócios a comandar departamentos nem o Diretor a
alterar prioridade comercial. Conflito de escopo, prioridade, orçamento ou risco aceito volta
ao CEO Maestro; conflito de autoridade volta a Jeremias.

## Workflow de produto ou proposta

```text
RECEIVED
  → CONTRACTED
  → ROUTED
  → DELEGATED
  → RETURNED
  → JUDGED
  ├── minimum_score >= 9,5 → VALIDATED
  ├── melhoria viável → REWORK → ROUTED
  ├── limite objetivo provado → AWAITING_HUMAN_EXCEPTION
  │   ├── Jeremias autoriza → VALIDATED_BY_EXCEPTION
  │   └── Jeremias recusa → BLOCKED ou REWORK
  └── capacidade/prova ausente → BLOCKED
```

Estados terminais: `VALIDATED`, `VALIDATED_BY_EXCEPTION`, `BLOCKED`, `CANCELLED` e
`LIMIT_REACHED`. A décima rodada sem atingir o corte termina em `LIMIT_REACHED`, salvo se uma
exceção válida tiver sido autorizada antes do fechamento.

## Barreira de submissão

O dono executivo só emite `EXECUTIVE_SUBMISSION` quando:

- todas as frentes obrigatórias retornaram;
- dependências e conflitos foram resolvidos;
- `scope_touched` permanece contido no `scope_in` da missão;
- artefatos e evidências possuem proveniência;
- testes aplicáveis registram ao menos um `PASS`, nenhum `FAIL` e justificam todo `SKIP`;
- Auditoria forneceu `governance_report` ligado ao digest das Regras de Ouro locais;
- Juízes emitiu `JUDGE_REPORT`;
- a menor nota pode ser recalculada;
- pendências e riscos continuam visíveis.

Retorno parcial permanece em `DELEGATED` ou `REWORK`; nunca cruza a barreira.

## Capacidade ausente

Se `diretor-de-lentes`, `departamento-negocios` ou a proveniência de
`departamento-juizes` não resolver para pacote migrado, confiável e pinado:

1. registrar `CAPABILITY_GAP`;
2. bloquear somente a frente dependente;
3. mostrar impacto e opções reais;
4. não usar a versão antiga como equivalente sem decisão explícita de Jeremias.

## Critério de conclusão

O workflow está concluído quando existe um estado terminal, a decisão aponta para um pacote
íntegro e nenhuma entrega abaixo de 9,5 aparece como validação normal.
