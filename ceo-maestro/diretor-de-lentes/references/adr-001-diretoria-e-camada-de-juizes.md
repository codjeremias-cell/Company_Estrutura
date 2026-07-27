# ADR-001 — Diretor como camada própria e Juízes obrigatórios

- **Data:** 2026-07-26
- **Status:** aceito por decisão de Jeremias
- **Decisores:** Jeremias

## Contexto

O pacote legado `comite-de-lentes` reunia direção das especialidades, tratava Juízes como
opcionais em disputas e mantinha os Departamentos dentro da própria árvore. A nova estrutura
exige CEO, Diretor, Departamentos gerentes, agentes executores, Negócios como par e Juízes
como camada obrigatória.

## Decisão

Materializar `ceo-maestro/diretor-de-lentes` como skill própria. O Diretor dirige
Departamentos e não executa. `departamento-juizes` fica sob sua direção administrativa, em
camada paralela aos Departamentos operacionais, e valida toda entrega sem corrigi-la.
`departamento-negocios` permanece subordinado ao CEO e conversa matricialmente com o
Diretor.

Migrar somente o núcleo diretor nesta etapa. Os filhos legados não são copiados nem usados
como fallback.

## Consequências

- nome, contratos e handoffs passam a refletir a hierarquia aprovada;
- ausência de Departamento migrado fica visível como lacuna;
- Auditoria fornece prova e Juízes emite o veredito;
- produto ou proposta só chega ao CEO após o gate;
- o legado permanece intacto para rollback;
- os Departamentos precisam de migração individual posterior.

## Alternativas consideradas

- **Renomear a pasta legada inteira:** descartada porque promoveria mais de 35 MiB de pacotes,
  evidências históricas e contratos antigos como se fossem a nova estrutura.
- **Absorver a direção no CEO:** descartada porque misturaria decisão executiva com
  coordenação operacional.
- **Manter Juízes opcionais:** descartada por contrariar o organograma aprovado.
