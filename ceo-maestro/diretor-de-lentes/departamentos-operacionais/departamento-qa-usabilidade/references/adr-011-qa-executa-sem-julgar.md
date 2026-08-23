# ADR-011 — QA gerencia execução e não julga a própria entrega

- **Status:** aceito
- **Data:** 2026-07-26
- **Autoridade:** organograma vigente e solicitação de Jeremias
- **Renumerado em 2026-07-26:** nasceu como `adr-005` numa frente paralela e colidiu, na série
  **global** da estrutura, com o `adr-005` de Registros
  ([adr-005-quatro-agentes-e-relatorios-de-registros.md](../../departamento-registros/references/adr-005-quatro-agentes-e-relatorios-de-registros.md)),
  já commitado e citado pelo `ORGANOGRAMA.md`. Por decisão de Jeremias, o de Registros permaneceu
  com o número e este passou a `adr-011`, o primeiro livre depois do `adr-010` de Segurança. Só o
  número mudou: contexto, decisões, consequências e alternativas seguem íntegros. A colisão agora é
  impedida mecanicamente por `validate_adr_series` em
  [`_compartilhado/verificacoes_pacote.py`](../../../../../_compartilhado/verificacoes_pacote.py),
  ligada a todos os validadores de pacote.

## Contexto

A lente legada combinava `GERENCIAR | JULGAR`, proibia criar agentes e
dependia da rota antiga Maestro → Comitê → lente. A nova empresa já possui um
`departamento-juizes` independente e exige que todo Departamento nasça como
gerente com três agentes.

O pedido atual requer especialistas para qualidade funcional, não funcional e
experiência, cobrindo desktop, web/mobile, API/CLI, banco, dashboards,
relatórios, PDFs, documentos e jogos.

## Decisão

1. Criar `departamento-qa-usabilidade` como gerente sob o Diretor.
2. Retirar integralmente o modo `JULGAR` do QA.
3. Proibir nota, corte 9,5 e validação dentro do Departamento.
4. Criar exatamente os três agentes já fixados no organograma.
5. Especializar os agentes por propriedade e perfis, não por tecnologia
   isolada, evitando agentes sobrepostos no nascimento.
6. Preservar do legado rastreabilidade, estados de evidência, autorização,
   limpeza, causalidade e fail-closed.
7. Manter o legado intacto como rollback histórico, nunca fallback.

## Consequências

- A execução de QA passa a ter produtores reais e contratos próprios.
- A gerente consolida sem executar.
- Juízes preservam independência e são os únicos que pontuam/validam.
- Um alvo pode acionar os três agentes, com critério atômico e dona única.
- Especialidade que não caiba ou exija ferramenta/independência própria vira
  `QA_CAPABILITY_GAP` e proposta de expansão formal.

## Alternativas consideradas

### Copiar e renomear a lente legada

Descartada: manteria rota, identidades e autoridade de julgamento incompatíveis
e continuaria sem agentes.

### Manter o modo `JULGAR` como “segunda opinião”

Descartada: seria autojulgamento e duplicaria o Departamento de Juízes.

### Criar seis agentes por plataforma imediatamente

Descartada no nascimento: contraria o guia e o organograma, aumenta
sobreposição e não há evidência operacional de carga/gap. Os perfis preservam
especificidade; expansão exige dado real e ADR.

### Usar `testador-real` e skills canônicas como agentes em runtime

Descartada: são fontes e ferramentas do cânone, não subordinados desta
hierarquia. Fallback silencioso esconderia capacidade ausente.

## Critério de revisão

Revisar quando forward tests ou missões reais mostrarem capability gap
recorrente, fronteira impossível, isolamento necessário ou carga que prejudica
cobertura. A revisão começa pelo organograma e por novo ADR.

## Concluído quando

Contrato, schema, três agentes e validação mecânica impedem a gerente de
executar/julgar e impedem agentes de operar por bypass.

