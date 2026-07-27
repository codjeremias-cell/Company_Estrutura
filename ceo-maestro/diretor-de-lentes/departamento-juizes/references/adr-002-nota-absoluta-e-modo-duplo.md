# ADR-002 — Juízes emitem nota absoluta e operam em dois modos

- **Data:** 2026-07-26
- **Status:** aceito por decisão de Jeremias
- **Decisores:** Jeremias
- **Contexto normativo:** [ADR-001 da diretoria e da camada de Juízes](../../references/adr-001-diretoria-e-camada-de-juizes.md)

## Contexto

O ADR-001 fixou o Departamento de Juízes como camada obrigatória: toda entrega de Departamento e
todo candidato integrado passam por ele antes de o Diretor integrar ou submeter. Mas o pacote
legado `lente-juizes` foi construído para outra pergunta. Ele compara **candidatos entre si**,
recusa explicitamente emitir nota absoluta ("isso é do Comitê via `lente-auditor-responsabilidades`")
e devolve uma **recomendação** de quem vence, não um veredito de gate.

Os contratos já migrados exigem o contrário. O schema do CEO define `JUDGE_REPORT` com `scorecard`,
`minimum_score`, `verdict: VALIDATED | REPROVED` e produtor fixado em `departamento-juizes`; o
schema do Diretor define `DEPARTMENT_JUDGE_REPORT` nos mesmos termos e condiciona
`ACCEPTED_FOR_INTEGRATION` a `VALIDATED` com `minimum_score >= 9.5`. Migrar a skill legada sem
resolver isso entregaria um Departamento que não produz o artefato que seus dois consumidores
exigem.

Ao mesmo tempo, a capacidade comparativa cega é o núcleo de valor do legado — sorteio por juiz,
óticas isoladas, fail-closed, enxertos preservados — e continua útil sempre que houver duas
propostas disputando o mesmo contrato.

## Decisão

**1. O Departamento emite nota absoluta.** A nota por critério e o `minimum_score` passam a ser
produto dos Juízes. A Auditoria fornece a **prova de conformidade** com contrato e Regras de Ouro;
os Juízes consolidam as evidências e emitem o veredito. Isso reverte a fronteira do legado, que
mandava a nota absoluta ao Auditor.

**2. O Departamento opera em dois modos, com o mesmo time.** VALIDACAO é o padrão e responde ao
gate obrigatório. DISPUTA é secundário, preserva o protocolo cego do legado e responde a
comparação entre 2+ candidatos. O modo é fixado no recebimento, nunca no meio da rodada. O vencedor
de uma disputa **não** está validado: ainda passa por VALIDACAO antes de integrar.

**3. A nota nasce nas três óticas, não na gerente.** Cada critério aplicável recebe exatamente uma
ótica dona, registrada em `CRITERIA_MATRIX` antes de qualquer delegação. A gerente reparte,
consolida e transcreve; ela **nunca** pontua. Critério sem dona não recebe nota estimada: abre
lacuna e proíbe `VALIDATED`.

**4. Consolidação pelo mínimo, jamais pela média.** `minimum_score` é a menor nota do `scorecard`
aplicável. Critério avaliado por duas óticas vale a **menor** das duas. Média, mediana, ponderação
por confiança, arredondamento e compensação entre critérios são proibidos.

**5. Fail-closed em cobertura.** Ótica ausente, critério sem dona ou pendência bloqueante impedem
`VALIDATED`. A reprovação resultante é **nomeada como lacuna de cobertura** já na primeira frase
das críticas, para não mandar um Departamento reescrever entrega sadia por um defeito que ninguém
observou.

**6. O Departamento não corrige e não executa.** Não reescreve candidato, não propõe patch, não
roda build, teste ou lint. Consome prova produzida por outros. Reprovação volta ao Departamento
responsável, via Diretor, com crítica e mudança exigida ligadas a critério com evidência.

## Consequências

- os dois consumidores — Diretor e CEO — recebem exatamente o envelope que seus schemas exigem;
- a menor nota vira o único número que decide, e nenhum agregado pode mascará-la;
- a capacidade comparativa cega sobrevive à migração em vez de morrer com o pacote legado;
- o corte de 9,5 sobre notas inteiras significa, na prática, **10 em todos os critérios
  aplicáveis** dentro de uma rodada — endurecimento consciente, registrado em
  [rubrica-e-corte.md](rubrica-e-corte.md);
- a Auditoria perde a nota e mantém a prova, o que exigiu que o
  `departamento-auditoria-responsabilidades` nascesse já sem scorecard próprio — **migrado em
  2026-07-26, exigência cumprida** pelo ADR-003 ("conformidade sem nota");
- o modo `leve` do legado não migra, e disputa repetida do mesmo contrato volta a custar as três
  óticas.

## Alternativas consideradas

- **Manter os Juízes só comparativos e mandar a nota ao Auditor:** descartada — contraria o
  organograma e os dois schemas já aceitos, que fixam `departamento-juizes` como produtor de
  `JUDGE_REPORT`, e devolveria ao Diretor um parecer que ele não pode usar como gate.
- **Criar dois Departamentos, um de nota e outro de disputa:** descartada — duplicaria as três
  óticas, o time e o contrato para uma diferença que é de **pergunta**, não de competência, e
  abriria a porta para os dois discordarem sobre o mesmo artefato.
- **Descartar o modo comparativo:** descartada — perderia sorteio por juiz, enxertos e o
  fail-closed comparativo, que são o valor específico do pacote legado e não existem em nenhuma
  outra skill da estrutura.
- **Consolidar por média ponderada pela confiança:** descartada — permitiria que um critério
  `quebrado` fosse compensado por notas altas em critérios fáceis, exatamente o que o corte por
  menor nota existe para impedir.
- **Deixar a gerente pontuar critério sem dona:** descartada — transformaria a gerente em quarto
  juiz secreto, sem ótica declarada, sem cegueira e sem fronteira exclusiva.
