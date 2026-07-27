# ADR-009 — Design migra sem painel cego, com time fixo e gate visual mecânico

- **Data:** 2026-07-26
- **Status:** aceito por decisão de Jeremias
- **Decisores:** Jeremias
- **Contexto normativo:** [ADR-001 hierarquia](../../../../references/adr-001-hierarquia-executiva.md) ·
  [ADR-002 Juízes](../../../departamento-juizes/references/adr-002-nota-absoluta-e-modo-duplo.md) ·
  [ADR-006 Arquitetura](../../departamento-arquitetura-software/references/adr-006-arquitetura-sem-julgamento-e-com-seis-agentes.md) ·
  [ADR-008 Dados](../../departamento-arquitetura-dados/references/adr-008-dados-skill-nova-e-seis-agentes.md)

## Contexto

A `lente-designer` é o **pacote legado mais maduro** do Comitê: 249 arquivos, protocolo de
orquestração de 527 linhas, rubrica de superfície com nove dimensões, dois JSON Schemas próprios e
uma bateria de evals com placar-baseline já executado. Ela não é um esboço — é uma skill que já
rodou.

Isso cria um problema que as migrações anteriores não tiveram: **o legado já resolve, à sua maneira,
três coisas que a nova estrutura resolve de outra**. Descrever a migração como "copiar e adaptar"
esconderia as decisões. Elas estão abaixo.

## Decisão

**1. O time é fixo; a descoberta de executores em runtime não migra.** O legado descobre
"executores de design" no inventário a cada rodada, congela um `capability_snapshot` e delega a
quem encontrar. A nova estrutura define Departamento como **gerente + agentes de capacidade
exclusiva**, declarados e testados. Manter descoberta dinâmica criaria um Departamento cujo time
muda a cada execução — inauditável pelo `departamento-auditoria-responsabilidades` e impossível de
travar por `enum` de schema.

O que era "executor não encontrado no inventário" vira `DESIGN_CAPABILITY_GAP` ao Diretor.

**2. A Lei de Ferro sobrevive, com a fronteira redesenhada.** *Orquestre, não produza* continua
valendo, e agora tem endereço: este Departamento **decide e especifica** a experiência; quem
**materializa** — código de tela, arquivo de tokens, imagem, protótipo executável — é o
`departamento-desenvolvimento`, por `delegated_dependency`. Wireframe anotado e especificação
visual inequívoca **são artefatos de design** e continuam sendo produzidos aqui; HTML, CSS, FXML e
JSON de tokens, não.

**3. O painel cego não migra.** O legado compara alternativas em painel cego com identificadores
opacos e proveniência selada. Isso é **exatamente** o modo `DISPUTA` que o ADR-002 atribuiu ao
`departamento-juizes`. Este Departamento **produz alternativas ortogonais** e as devolve ao Diretor,
que emite o `JUDGMENT_REQUEST`. Duplicar o painel aqui criaria dois donos do julgamento comparativo
na mesma estrutura — o mesmo erro que o ADR-006 evitou ao não migrar o modo `JULGAR`.

**4. As nove dimensões da rubrica viram cobertura, não nota.** Estados `COBERTA`, `PARCIAL`,
`NAO_APLICAVEL`, `AUSENTE`. Nenhum campo de nota existe no schema, e o validador reprova se
aparecer. Pontuar é dos Juízes.

**5. Sete agentes, um por dimensão com dono exclusivo.**

| Agente | Dimensão da rubrica |
|---|---|
| `agente-direcao-e-anti-slop` | 1 — direção deliberada e anti-AI-slop |
| `agente-fluxo-estados-e-transicoes` | 2 — fluxo, estados e transições |
| `agente-acessibilidade-medida` | 3 — acessibilidade mensurável |
| `agente-linguagem-visual` | 4 — tipografia, espaço, cor e motion |
| `agente-nitidez-e-adaptacao` | 5 e 7 — nitidez e adaptação nativa por stack |
| `agente-dataviz` | 6 — data-viz |
| `agente-design-system-e-tokens` | o contrato design↔código |

As dimensões **8 (Polish Pass)** e **9 (evidência de conclusão)** ficam com a gerente: a primeira é
um *modo de operação*, não uma especialidade; a segunda é consolidação.

**6. Duas separações por conflito de interesse.**

- quem faz `LINGUAGEM_VISUAL` **não** faz `ACESSIBILIDADE_MEDIDA` — quem escolheu a paleta
  racionaliza o próprio contraste, e "contraste medido, não presumido" morre;
- quem faz `LINGUAGEM_VISUAL` **não** roda o teste anti-slop sobre a própria saída — anti-slop é
  verificação adversarial, e autor não é adversário de si mesmo. Ela cabe ao
  `agente-direcao-e-anti-slop`.

**7. O `DESIGN_GATE` migra e vira mecânico.** Enquanto o gate estiver `PENDING`, **nenhuma
dependência de implementação sai** — o schema recusa. Comentário informal, ausência de objeção ou
"o código já está pronto" não são aprovação. O ator autorizado é nomeado ou o gate não fecha.

**8. A taxonomia de evidência migra inteira e vira trava.** `OBSERVED`, `PRODUCED`, `MEASURED`,
`REPORTED`, `UNAVAILABLE`. **Critério marcado como atendido sustentado apenas por `REPORTED` ou
`UNAVAILABLE` é rejeitado pelo schema.** É a versão mecânica de "nunca converta relatado em
sucesso". Critério não medido é `UNVERIFIED` e nunca vira aprovado.

**9. Adaptação nativa é transversal e obrigatória.** Nunca forçar API ou padrão web em
JavaFX/Flutter/nativo, nem padrão mobile em desktop sem motivo observado. O retorno declara as
primitivas reais do stack; sem isso, a entrega não fecha.

## Consequências

- o `departamento-juizes` ganha um segundo cliente para o modo `DISPUTA`, agora com alternativas de
  design chegando pelo Diretor;
- o `departamento-desenvolvimento` — ainda ausente — passa a ter mais um emissor de dependências;
- o legado permanece intacto como rollback manual, com seus 249 arquivos e o placar-baseline
  preservados;
- o `capability_snapshot` do legado perde função: o time é declarado, não descoberto.

## Alternativas consideradas

- **Manter a descoberta de executores em runtime.** Descartada: torna o time do Departamento
  variável, portanto não auditável e não travável por schema. A flexibilidade que ela dava é
  recuperada pela `delegated_dependency`, que é explícita e rastreável.
- **Manter o painel cego aqui, "porque já funciona".** Descartada pelo mesmo motivo que o ADR-006
  descartou o modo `JULGAR`: dois donos do julgamento comparativo é ambiguidade de autoridade, e a
  estrutura já decidiu quem julga.
- **Fundir nitidez e adaptação em agentes separados (oito agentes).** Descartada: as duas dimensões
  respondem à mesma pergunta — *isso funciona nas densidades, escalas e primitivas reais deste
  stack?* — e separá-las produziria dois retornos que sempre se citam.
- **Deixar a taxonomia de evidência como orientação em prosa.** Descartada: era o ponto mais frágil
  do legado, porque depende de disciplina. Virou condição de schema.
