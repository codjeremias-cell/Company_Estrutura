# As oito dimensões da entrega arquitetural

**Isto não é rubrica de nota.** É o checklist de **cobertura** da entrega: o que um pacote
arquitetural precisa conter para estar completo. Nota, peso e corte saíram com o
[ADR-006](adr-006-arquitetura-sem-julgamento-e-com-seis-agentes.md), decisão 2 — pontuar é do
`departamento-juizes`.

Serve a dois usos:

1. **Portão de saída do próprio Departamento** — dimensão sem cobertura é `PENDING` com dono, nunca
   silêncio.
2. **Vocabulário para o Diretor** compor `applicable_criteria` quando mandar a entrega ao gate.

## As dimensões

| # | Dimensão | Cobertura mínima | Agente dono |
|---:|---|---|---|
| 1 | **drivers e aderência ao contexto** | drivers priorizados e **medíveis**, ligados às decisões que os consomem | `agente-drivers-e-restricoes` |
| 2 | **domínio, limites e modularidade** | capacidades, contextos, módulos, dependências e acoplamentos explícitos | `agente-modularidade-e-limites` |
| 3 | **integração, contratos e donos de dados** | APIs/eventos, síncrono × assíncrono, versionamento, idempotência, modos de falha, ownership | `agente-integracoes-e-contratos` |
| 4 | **qualidade, resiliência e operação** | NFRs como cenários mensuráveis, SLO/RTO/RPO propostos, observabilidade, implicações operacionais | `agente-qualidade-e-operacao` |
| 5 | **alternativas, trade-offs e reversibilidade** | 2–3 opções distintas (ou única justificada), o que cada uma perde, custo de reverter, gatilho de mudança | `agente-alternativas-e-tradeoffs` |
| 6 | **ADR e C4** | decisão, contexto, consequências, alternativas descartadas; C4 Contexto e Contêiner em texto | `agente-adr-e-c4` |
| 7 | **evidência e confiança** | cada alegação aponta para prova, inferência declarada ou ausência; `SKIP` visível | **gerente**, na consolidação |
| 8 | **simplicidade e evolução** | a recomendação é a mais simples que atende os drivers e a maturidade real; caminho incremental | **gerente**, na consolidação |

As dimensões 7 e 8 não têm agente dono porque são propriedades do **pacote inteiro**, não trabalho
de alguém: elas se verificam na consolidação, olhando o conjunto.

## Estados de cobertura

Cada dimensão fecha em um destes, e só neles:

| Estado | Significa |
|---|---|
| `COBERTA` | tem conteúdo e evidência ou inferência declarada |
| `PARCIAL` | tem conteúdo, com lacuna nomeada, dono e condição de fechamento |
| `NAO_APLICAVEL` | não incide nesta missão, **com justificativa específica dela** |
| `AUSENTE` | ninguém cobriu — bloqueia a entrega |

`NAO_APLICAVEL` genérico é `AUSENTE`. Se ninguém consegue dizer por que a dimensão não incide neste
sistema, ninguém a verificou.

## O que continua valendo do legado

Três regras da rubrica antiga sobrevivem — não como cálculo, como **postura**:

- **Ausência de prova não vira plausibilidade.** Alegação sem evidência fica marcada como não
  comprovada; ela não sobe de estado por soar razoável.
- **Opção única exige justificativa verificável.** Duas ou três opções distintas, ou a prova de que
  as demais caíram por restrição real. Preferência não é restrição.
- **Contrato ou fronteira crítica ausente torna a proposta não executável.** Isso é lacuna
  bloqueante da dimensão 3, não detalhe a resolver depois.

## O que saiu, e para onde

| Saiu | Foi para |
|---|---|
| escala 0–10 por dimensão | `departamento-juizes`, rubrica própria |
| pesos e soma ponderada | idem |
| corte 9,5 e dimensão crítica ≥ 9,0 | idem — a régua vigente é a do ADR-014, não da produção |
| vetos e `REPROVADA` | idem |
| `NÃO_JULGÁVEL`, `BLOQUEADO_AUTOJULGAMENTO` | idem, e o aparato de independência nasceu lá |
| confiança `high/medium/low` como nota paralela | virou a dimensão 7, como cobertura |

**Concluído quando:** as oito dimensões têm estado, todo `PARCIAL` tem dono e condição, todo
`NAO_APLICAVEL` tem justificativa desta missão, e nenhuma está `AUSENTE`.
