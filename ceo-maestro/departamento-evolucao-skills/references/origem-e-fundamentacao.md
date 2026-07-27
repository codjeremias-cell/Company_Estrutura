# Origem e fundamentação — Departamento de Evolução de Skills

Este Departamento **não é migração**. Não existe `lente-evolucao-skills` no pacote legado, e ele não
está na lista de Departamentos do organograma original: foi pedido por Jeremias em 2026-07-26 como
frente nova. Por isso não há tabela de proveniência de pacote legado — há **fundamentação**: o que
foi lido dentro de casa, o que foi pesquisado fora, e o que deliberadamente não entrou.

## Fontes internas — a prática que já existia

O método não foi inventado. Ele formaliza, com correções, o que a casa já pratica:

| Fonte interna | O que entrou |
|---|---|
| `Catalogo-Skills-Unificado/_evolucao-skills/PLANO-EVOLUCAO.md` | o ciclo (medir → diagnosticar → manipular → buscar material → reauditar → promover), a regra "nada de nota fabricada", "quem editou nunca se autoavalia", anti-estagnação em 2 rodadas, **teto honesto** e o banco de trabalho separado do canônico |
| `Catalogo-Skills-Unificado/PADRAO-DE-AUTORIA.md` §10 | Selo Lendário — os cinco critérios que definem skill pronta |
| idem, §11 | **baseline antes do eval** (vermelho→verde), acionamento × aderência, casos sintéticos declarados com as três salvaguardas |
| idem, §12 | os 5 modos de falha do corpo (prosa no-op, conclusão prematura, sedimento, espalhamento, duplicação), **anti-sedimento** e a régua de escalada de força |
| `Aprendizagem/COMO-COLHER.md` | colheita por destilação, **categorias de falha nomeadas**, e o princípio de fonte única — a memória nativa é a verdade, a consolidação é camada |
| `Catalogo-Skills-Unificado/garimpo-*.md` | o formato de garimpo já praticado: gem com fonte, degrau de adoção, adoção fora do ciclo de nota |
| `ROADMAP`, item 11 | *"evoluir por padrão transversal rende mais que skill a skill"* — a frase que virou a tese do alcance |

**O dado que mais pesou** veio do tracker do `PLANO-EVOLUCAO.md`: média por rodada
**8,45 → 8,58 → 9,03 → 9,17 → 9,25 → 9,27 → ≈9,27**, com **"REGIME DE TETO"** declarado, o
diagnóstico *"variância entre avaliadores > ganho por micro-onda"* e ~25 skills em
**"aguarda material externo"**. É evidência de casa, não hipótese, e é o que justifica o desenho.

## Fontes externas — pesquisa de 2026-07-26

Toda consultada como **dado** (nível 4 da hierarquia de canal), resumida e adaptada, nunca copiada:

| Fonte | O que entrou | Limite declarado |
|---|---|---|
| [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457) — arXiv 2507.19457, ICLR 2026 Oral | **fronteira de Pareto** em vez de campeão único; **reflexão sobre trajetória** (raciocínio, chamadas, saídas) em linguagem natural; fusão de lições complementares. Reporta superar GRPO em até 20% com **35× menos rollouts** e o MIPROv2 em +10% | os números são de otimização de prompt com métrica automática; aqui não há métrica automática equivalente, então o ganho **não é transferível como número** — só o mecanismo |
| [Spontaneous Reward Hacking in Iterative Self-Refinement](https://arxiv.org/pdf/2407.04549) | a nota do avaliador **infla enquanto a humana cai**, sem atualização de peso | mostra o fenômeno, não dá o freio; o freio adotado (vermelho→verde) é da casa |
| [More Convincing, Not More Correct](https://arxiv.org/html/2607.05904) | juiz sem referência pontua **plausibilidade**, não correção | reforça a necessidade de baseline; não resolve caso de eval mal desenhado |
| [LLM Evaluators Recognize and Favor Their Own Generations](https://proceedings.neurips.cc/paper_files/paper/2024/file/7f1f0218e45f5414c79c0679633e47bc-Paper-Conference.pdf) — NeurIPS 2024 | **auto-preferência**: o avaliador prefere o que ele mesmo gerou | por isso a seleção é do `departamento-juizes`, cego e externo |
| [Evaluator-Driven Preference Dynamics in Self-Adapting LLM Agents](https://arxiv.org/pdf/2606.29719) | laços evolutivos **colapsam diversidade** e exploram o padrão de alta recompensa conhecido | daí a regra de manter e nomear o candidato melhor em um caso só |
| [Voyager: An Open-Ended Embodied Agent](https://voyager.minedojo.org/) | biblioteca de skills que só admite o **verificado**; currículo automático | é ambiente com verificação executável; aqui a verificação é o eval, mais fraca |
| [SkillFoundry](https://arxiv.org/html/2604.03964v1) | mineração que extrai **contrato operacional** e valida executabilidade antes de admitir | domínio científico com recurso estruturado; aqui a fonte é heterogênea |

## O que deliberadamente não entrou

- **Meta de nota exponencial.** Nenhuma evidência sustenta, e a de casa contradiz. A meta declarada é
  alcance composto — [ADR-004](adr-004-evolucao-no-nivel-do-ceo.md), decisão 4.
- **Números do GEPA como promessa.** O mecanismo migrou; os percentuais ficaram na fonte, porque o
  contexto de medição é outro.
- **Auto-otimização contínua.** Nada de laço rodando sozinho: o Departamento é inerte sem missão do
  CEO. É a diferença entre um programa de evolução e um agente que se reescreve.
- **Leitura direta da memória dos projetos.** Fica com o `departamento-registros`; aqui só entra
  relatório.
- **Nota emitida por este Departamento.** Pontuar é do `departamento-juizes` (ADR-002); provar
  conformidade é da Auditoria (ADR-003). Aqui se produz e se prova candidato.
- **O tracker histórico como régua vigente.** As notas R0–R6 do `PLANO-EVOLUCAO.md` são de outra
  régua e de outro painel. Comparar rodada nova com aquela tabela exige dizer qual régua está em
  uso — a própria tabela já avisa isso duas vezes.

## Relação com o banco de trabalho legado

`Catalogo-Skills-Unificado/_evolucao-skills/` **permanece intacto**: é histórico e é o banco onde o
programa antigo rodou. Este Departamento **não** o edita, **não** o promove e **não** o usa como
área de trabalho. Candidato novo nasce em área própria da rodada, declarada na missão.
