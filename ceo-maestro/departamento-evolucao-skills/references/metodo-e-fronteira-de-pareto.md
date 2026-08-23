# O método de evolução e a fronteira de Pareto

Fonte única do motor de evolução: o ciclo, a fronteira, o que conta como ganho e quando parar.
Fundamentação e decisões em [adr-004-evolucao-no-nivel-do-ceo.md](adr-004-evolucao-no-nivel-do-ceo.md).

## 1. O ciclo, por frente

Uma **frente** é um conjunto de skills que compartilha o mesmo gap. Frente de uma skill só é
legítima, mas rende menos — ver §5.

1. **Medir antes de opinar.** Rodar os casos de eval da skill e ler o **transcript**: acionou sem
   ser nomeada? aderiu até o fim? onde contornou? O gap nasce da execução observada, nunca da
   leitura crítica do arquivo.
2. **Nomear o gap**, em uma frase verificável, ancorada no trecho do transcript que o revelou.
   Gap sem trecho é opinião.
3. **Agrupar por alcance.** Antes de propor conserto, perguntar **quantas outras skills têm este
   mesmo gap**. O agrupamento é o passo que produz ganho composto (§5).
4. **Buscar material** quando falta conceito: colheita de aprendizagem via `departamento-registros`
   ou mineração externa ([mineracao-e-proveniencia.md](mineracao-e-proveniencia.md)). **Sem material
   novo, não abrir rodada** — é a lição do regime de teto.
5. **Gerar candidatos**, no mínimo dois por gap, deliberadamente diferentes entre si. Um candidato
   só não é fronteira; é preferência.
6. **Provar** cada candidato pelo baseline executado (§4). Candidato sem vermelho→verde não é
   recomendado, por melhor que leia.
7. **Fechar a fronteira** (§2) e devolver ao CEO: candidatos não dominados, placar, alcance,
   divergências preservadas e o que **não** foi provado. Selecionar o vencedor é do
   `departamento-juizes`; promover é do CEO e de Jeremias.

**Concluído quando:** cada gap tem trecho de origem, alcance medido, dois ou mais candidatos
provados, e a fronteira fechada com o que fica e o que foi dominado.

## 2. A fronteira de Pareto

O programa antigo mantinha **um** candidato por skill, substituído a cada rodada. Isso é otimização
gulosa e colapsa em ótimo local — foi o que produziu o teto de 9,27. O mecanismo aqui é o do
**GEPA** ([arXiv:2507.19457](https://arxiv.org/abs/2507.19457)): manter o conjunto **não dominado**
e combinar lições complementares.

**Dominância.** O candidato `A` **domina** `B` quando `A` é pelo menos tão bom quanto `B` em
**todos** os casos de eval **e** estritamente melhor em ao menos um. "Bom" aqui é o resultado
observado por caso — `passou`/`falhou`, mais `acionou` e `aderiu` —, não uma nota agregada.

**A fronteira** é o conjunto dos candidatos que ninguém domina. Regras:

- **Candidato dominado sai**, com o motivo registrado. Sair não apaga: a lição dele pode ser
  enxertada em outro.
- **Candidato pior na média e melhor em um caso FICA**, e é **nomeado** no relatório. Ele é a
  defesa contra o colapso de diversidade que a literatura descreve
  ([arXiv:2606.29719](https://arxiv.org/pdf/2606.29719)): o caminho que hoje parece pior sob o
  avaliador vigente é justamente o que a otimização gulosa mata primeiro.
- **Fusão é permitida e preferida.** Combinar a lição de dois candidatos da fronteira num terceiro
  é o movimento de maior retorno do GEPA — e o resultado entra como candidato novo, que **também**
  precisa ser provado.
- **Fronteira de um só elemento é sinal, não conquista.** Registrar em `pending`: ou os candidatos
  eram variações do mesmo, ou os casos de eval não discriminam.

**Concluído quando:** a dominância foi calculada caso a caso e é recalculável por terceiro a partir
do placar, e todo candidato removido tem o dominador nomeado.

## 3. O que se lê: trajetória, não texto

Três sinais, todos do transcript, todos do `PADRAO-DE-AUTORIA` §11.5:

| Sinal | Pergunta | Valores |
|---|---|---|
| **acionou** | a skill disparou **sem ser nomeada** no prompt? | `S` / `N` |
| **aderiu** | o agente seguiu a skill até o fim? | `S` / `parcial` / `N` |
| **contorno** | qual passo obrigatório foi omitido ou substituído por solução ad hoc? | trecho literal |

`acionou: N` ⇒ `aderiu: —`: não há aderência a medir. **Contorno é defeito da skill**, não do
modelo: corpo confuso ou description fraca. Um contorno citado por trecho vale mais que três
parágrafos de crítica ao estilo.

## 4. Baseline executado — o gate de admissão

TDD aplicado a skill, §11 do padrão da casa, e a resposta direta ao juiz que pontua plausibilidade:

1. **Vermelho.** Rodar o caso **sem** a mudança. Registrar a falha observada.
2. **Verde.** Rodar o mesmo caso **com** a mudança. Passar tendo falhado antes é a evidência.
3. **Corte.** Se o caso **já passava** sem a mudança, a mudança é redundante — não recomendar.
4. **Corte inverso.** Se continua falhando com a mudança, o candidato não ensinou o que devia.

**Nada de placar fabricado.** Caso não executado é `SKIP` declarado com motivo; nunca "presumido
verde". Quem escreveu o candidato **não** roda a prova dele — a independência é entre agentes deste
Departamento, e vale mesmo quando parece burocracia.

**Caso sintético** segue as três salvaguardas do §11.6 do padrão: gerado antes de afinar a
description ou em outra sessão; placar separado de real × sintético; e sintético criado depois da
skill existir roda o baseline uma vez. Caso sintético **não** conta para escalar força de regra.

## 5. O que conta como ganho

A meta declarada **não** é subir a média das notas. Essa métrica satura e depois infla — é o achado
do ADR-004. Por rodada, o Departamento mede:

| Métrica | O que é | Por que |
|---|---|---|
| **Alcance** | quantas skills a mudança toca | é o que compõe: um achado que serve a 12 skills vale 12 retoques |
| **Material admitido** | gems minerados adotados + lições convertidas em regra | sem material novo, a rodada só recombina o que já havia |
| **Cobertura de eval** | casos novos que passaram a discriminar | fronteira só existe se os casos separam candidatos |
| **Vermelho→verde** | casos que falhavam e passaram | é a única prova de que houve ensino |
| *(secundária)* nota | parecer do painel, quando houver | sinal sujeito a inflação; nunca a meta |

**"Exponencial" quer dizer transversal.** Ganho composto vem de uma mudança que se aplica a muitas
skills, não de muitas rodadas sobre uma. Frente que toca uma skill só é legítima, mas o relatório
declara o alcance `1` — para que a escolha de gastar ali seja consciente.

## 6. Quando parar

- **Anti-estagnação.** Duas rodadas sem ganho **verificado por placar** encerram a frente. Não
  "sem ganho de nota": sem vermelho→verde novo, sem alcance novo, sem material novo.
- **Teto honesto.** Encerrada por estagnação, a frente sai declarada `TETO_HONESTO`, com o gap
  remanescente nomeado e o material que faltaria para destravá-lo. Teto honesto **não** é fracasso;
  é informação, e o programa da casa já registrava ~25 skills nesse estado.
- **Anti-sedimento.** Toda edição deixa a skill **mais curta ou mais afiada**. Ao adicionar regra,
  remover a redação que ela substitui. Candidato que só cresce é rejeitado na fronteira, mesmo
  passando no baseline — inchaço passa em eval e cobra depois.
- **Sem material, sem rodada.** Abrir rodada sem colheita nem mineração é comprar o teto de novo.

## 7. Modos de falha do próprio programa

O laço de auto-melhoria tem patologias conhecidas. Elas não são hipóteses: têm literatura e têm
registro no tracker desta casa.

| Falha | Como aparece aqui | Mitigação | Teto |
|---|---|---|---|
| **Reward hacking de auto-refinamento** — a nota do avaliador sobe enquanto a qualidade cai ([arXiv:2407.04549](https://arxiv.org/pdf/2407.04549)) | rodadas sucessivas elevando o parecer sem nenhum caso novo passando | ganho só conta com **vermelho→verde executado**; nota é métrica secundária | quem executa o eval também escreve o relatório; a execução não é auditável de fora |
| **Auto-preferência do avaliador** ([NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/7f1f0218e45f5414c79c0679633e47bc-Paper-Conference.pdf)) | o Departamento gostaria mais do candidato que ele mesmo escreveu | seleção é do `departamento-juizes`, cego e externo; aqui ninguém escolhe vencedor | o Departamento ainda escolhe **quais** candidatos submete |
| **Juiz sem referência pontua plausibilidade** ([arXiv:2607.05904](https://arxiv.org/html/2607.05904)) | candidato bem escrito e errado vence o feio e certo | baseline executado é a referência; sem ele não há recomendação | caso de eval mal desenhado passa a medir a mesma plausibilidade |
| **Colapso de diversidade** ([arXiv:2606.29719](https://arxiv.org/pdf/2606.29719)) | a fronteira converge num único estilo de candidato | manter o não dominado que é melhor em um caso só, e nomeá-lo | quem gera os candidatos tende ao mesmo estilo; variedade é declarada, não garantida |
| **Variância maior que o ganho** — registrada no tracker da casa: *"cada painel fresco acha defeitos novos"* | duas rodadas oscilando sem direção | anti-estagnação em 2 rodadas, com teto honesto declarado | distinguir variância de ganho exige mais rodadas do que o freio permite |
| **Sedimento** — §12 do padrão | a skill cresce a cada rodada e ninguém remove nada | candidato que só cresce é rejeitado | "mais afiada" é julgamento, não medida |

**Concluído quando:** o relatório da rodada nomeia qual destas falhas era plausível naquela frente e
o que foi feito a respeito — e nomeia **sempre** a primeira, porque ela não depende de condição.
